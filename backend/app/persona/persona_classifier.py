import logging
from typing import Dict, List

from app.persona.persona_models import PersonaContext, PersonaResult, PersonaSignal
from app.persona.persona_registry import get_persona_definition
from app.persona.persona_rules import aggregate_rule_scores, normalize_text

logger = logging.getLogger(__name__)


def normalize_score(score: float) -> float:
    return min(max(score, 0.0), 1.0)


def _compute_confidence(
    combined_scores: Dict[str, float],
    signal_count: int = 0,
    provider_success: bool = False,
    ocr_confidence: float = 0.0,
) -> Dict[str, float]:
    if not combined_scores:
        return {
            'confidence': 0.0,
            'dominance': 0.0,
            'evidence': 0.0,
            'signal_diversity': 0.0,
            'signal_strength': 0.0,
            'top_score': 0.0,
            'second_score': 0.0,
            'total_score': 0.0,
            'signal_count': 0,
            'provider_success': provider_success,
            'ocr_confidence': ocr_confidence,
        }

    sorted_scores = sorted(combined_scores.values(), reverse=True)
    top_score = sorted_scores[0]
    second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0.0
    total_score = sum(sorted_scores)
    
    # Dominance: how clear the winner is relative to runner-up (0-1)
    # Clamped: even huge first score vs tiny second should not exceed 0.99
    dominance_raw = top_score / (top_score + second_score + 1e-6)
    dominance = min(0.99, max(0.0, dominance_raw))
    
    # Evidence: absolute strength of top score (0-1)
    # Normalize to 0-1 where 6.0+ is considered "very strong"
    evidence = min(1.0, max(0.0, top_score / 6.0))
    
    # Signal diversity: how many different personas have signals (penalty for single-source)
    # Range: 0-1, where 1 = all personas have signals, 0 = only one has signals
    personas_with_signals = sum(1 for score in combined_scores.values() if score > 0)
    total_personas = len(combined_scores)
    signal_diversity = (personas_with_signals / total_personas) if total_personas > 0 else 0.0
    signal_diversity_normalized = signal_diversity  # 0.0 to 1.0
    
    # Total strength: how rich the overall scoring landscape is
    total_strength = min(1.0, max(0.0, total_score / 8.0))
    
    # Signal strength: raw count of distinct signals
    signal_strength = min(1.0, max(0.0, signal_count / 5.0))
    
    # OCR quality factor
    ocr_factor = min(1.0, max(0.0, ocr_confidence))
    
    # Provider success penalty
    provider_factor = 1.0 if provider_success else 0.80
    
    # Compute raw confidence with balanced weights
    # Reduced dominance weight to prevent overconfidence from single top scorer
    raw_confidence = (
        0.20 * dominance              # Clarity of choice (reduced from 0.35)
        + 0.30 * evidence              # Absolute signal strength (increased from 0.20)
        + 0.20 * signal_diversity_normalized  # Breadth of signals (new component)
        + 0.10 * total_strength        # Overall scoring richness
        + 0.10 * signal_strength       # Count of distinct signals
        + 0.10 * ocr_factor            # OCR quality support
    )
    
    # Apply provider factor
    confidence_before_ceiling = raw_confidence * provider_factor
    
    # Confidence ceiling based on evidence quantity and signal diversity
    # Strong evidence (top_score >= 6): max 0.90 normally, but 0.85 if multiple personas
    # Moderate evidence (top_score 3-6): max 0.80 normally, but 0.70 if multiple personas
    # Weak evidence (top_score 1-3): max 0.65 normally, but 0.55 if multiple personas
    # Very weak (top_score < 1): max 0.45
    diversity_penalty = 0.05 if personas_with_signals > 1 else 0.0
    
    if top_score >= 6.0:
        confidence_ceiling = max(0.85, 0.90 - diversity_penalty)
    elif top_score >= 3.0:
        confidence_ceiling = max(0.70, 0.80 - diversity_penalty)
    elif top_score >= 1.0:
        confidence_ceiling = max(0.55, 0.65 - diversity_penalty)
    else:
        confidence_ceiling = 0.45
    
    # Apply ceiling and normalize
    confidence = normalize_score(min(confidence_ceiling, confidence_before_ceiling))
    
    # Ensure minimum confidence for any detected signals
    if signal_count > 0 and confidence < 0.15:
        confidence = 0.15

    return {
        'confidence': confidence,
        'confidence_components': {
            'dominance': dominance,
            'evidence': evidence,
            'signal_diversity': signal_diversity_normalized,
            'signal_strength': signal_strength,
            'total_strength': total_strength,
            'ocr_factor': ocr_factor,
            'provider_factor': provider_factor,
            'confidence_ceiling': confidence_ceiling,
        },
        'top_score': top_score,
        'second_score': second_score,
        'total_score': total_score,
        'personas_with_signals': personas_with_signals,
        'signal_count': signal_count,
        'provider_success': provider_success,
        'ocr_confidence': ocr_confidence,
    }


def classify_with_signals(
    context: PersonaContext,
    rule_weight: float = 0.6,
    llm_weight: float = 0.4,
) -> PersonaResult:
    rule_scores, rule_signals = aggregate_rule_scores(
        ocr_text=context.ocr_text,
        caption=context.caption or '',
        labels=context.labels,
        objects=context.objects,
        intent=context.intent or '',
        provider_reasoning=context.provider_reasoning or '',
        metadata=context.historical_meta,
    )

    llm_scores = _score_llm_signals(context)
    all_personas = set(rule_scores) | set(llm_scores)
    combined_scores: Dict[str, float] = {}
    signals: List[PersonaSignal] = []

    for persona in all_personas:
        combined_value = (
            rule_scores.get(persona, 0.0) * rule_weight
            + llm_scores.get(persona, 0.0) * llm_weight
        )
        combined_scores[persona] = combined_value

    for signal in rule_signals:
        signals.append(PersonaSignal(**signal))

    for persona, score in llm_scores.items():
        if score > 0:
            signals.append(PersonaSignal(
                source='llm_assisted',
                persona=persona,
                score=score,
                evidence=context.provider_reasoning,
            ))

    if not combined_scores:
        logger.debug('Persona classification found no combined signals.')
        return PersonaResult(
            persona='unknown',
            confidence=0.0,
            reasoning='No signals were identified for persona classification.',
            traits=[],
            signals=signals,
            metadata={
                'rule_scores': rule_scores,
                'llm_scores': llm_scores,
                'combined_scores': combined_scores,
            },
        )

    selected_persona = max(combined_scores, key=combined_scores.get)
    signal_count = len(signals)
    debug_info = _compute_confidence(
        combined_scores,
        signal_count=signal_count,
        provider_success=context.provider_success,
        ocr_confidence=context.ocr_confidence,
    )
    selected_score = debug_info['confidence']
    definition = get_persona_definition(selected_persona)
    top_personas = sorted(
        [{'persona': persona, 'score': score} for persona, score in combined_scores.items()],
        key=lambda item: item['score'],
        reverse=True,
    )
    reasoning = (
        f"Hybrid persona classification selected '{selected_persona}' with rule score "
        f"{rule_scores.get(selected_persona, 0.0):.2f} and llm score {llm_scores.get(selected_persona, 0.0):.2f}."
    )

    debug_metadata = {
        'rule_scores': rule_scores,
        'llm_scores': llm_scores,
        'combined_scores': combined_scores,
        'confidence_components': debug_info.get('confidence_components', {}),
        'scoring_details': {
            'top_score': debug_info['top_score'],
            'second_score': debug_info['second_score'],
            'total_score': debug_info['total_score'],
            'personas_with_signals': debug_info.get('personas_with_signals', 0),
            'signal_count': debug_info['signal_count'],
        },
        'selected_persona': selected_persona,
        'top_personas': top_personas,
        'top_signals': [signal.dict() for signal in signals],
    }

    return PersonaResult(
        persona=selected_persona,
        confidence=selected_score,
        reasoning=reasoning,
        traits=definition.traits,
        signals=signals,
        metadata=debug_metadata,
    )


def _score_llm_signals(context: PersonaContext) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    reasoning_text = normalize_text(context.provider_reasoning or '')
    if not reasoning_text:
        return scores

    for persona, keywords in [
        ('developer', ['code', 'debug', 'compile', 'terminal', 'api', 'stack trace', 'git', 'github', 'typescript']),
        ('designer', ['visual', 'layout', 'ux', 'ui', 'color', 'mockup', 'prototype', 'figma']),
        ('qa', ['bug', 'test', 'regression', 'issue', 'validation', 'error', 'failed', 'assertion']),
        ('analyst', ['metric', 'dashboard', 'insight', 'trend', 'data', 'report', 'analytics', 'excel']),
        ('student', ['learn', 'tutorial', 'example', 'explain', 'concept', 'practice', 'study']),
        ('shopper', ['buy', 'price', 'compare', 'purchase', 'review', 'cart', 'checkout']),
    ]:
        score = 0.0
        for keyword in keywords:
            if keyword in reasoning_text:
                score += 1.0
        if score:
            scores[persona] = score
    return scores
