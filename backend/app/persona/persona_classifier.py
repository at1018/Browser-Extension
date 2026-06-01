import logging
from typing import Dict, List

from app.persona.persona_models import PersonaContext, PersonaResult, PersonaSignal
from app.persona.persona_registry import get_persona_definition
from app.persona.persona_rules import aggregate_rule_scores, normalize_text

logger = logging.getLogger(__name__)


def normalize_score(score: float) -> float:
    return min(max(score, 0.0), 1.0)


def _compute_confidence(combined_scores: Dict[str, float]) -> Dict[str, float]:
    if not combined_scores:
        return {
            'confidence': 0.0,
            'dominance': 0.0,
            'evidence': 0.0,
            'gap': 0.0,
            'top_score': 0.0,
            'second_score': 0.0,
            'total_score': 0.0,
        }

    sorted_scores = sorted(combined_scores.values(), reverse=True)
    top_score = sorted_scores[0]
    second_score = sorted_scores[1] if len(sorted_scores) > 1 else 0.0
    total_score = sum(sorted_scores)
    dominance = top_score / (top_score + second_score + 1e-6)
    evidence = min(1.0, top_score / 6.0)
    gap = min(1.0, max(0.0, (top_score - second_score) / max(1.0, top_score)))
    confidence = normalize_score(0.55 * dominance + 0.25 * evidence + 0.20 * gap)

    return {
        'confidence': confidence,
        'dominance': dominance,
        'evidence': evidence,
        'gap': gap,
        'top_score': top_score,
        'second_score': second_score,
        'total_score': total_score,
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
    debug_info = _compute_confidence(combined_scores)
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
        'confidence_components': {
            'dominance': debug_info['dominance'],
            'evidence': debug_info['evidence'],
            'gap': debug_info['gap'],
            'top_score': debug_info['top_score'],
            'second_score': debug_info['second_score'],
            'total_score': debug_info['total_score'],
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
