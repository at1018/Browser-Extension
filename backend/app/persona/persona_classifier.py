from typing import Dict, List

from app.persona.persona_models import PersonaContext, PersonaResult, PersonaSignal
from app.persona.persona_registry import get_persona_definition
from app.persona.persona_rules import aggregate_rule_scores, normalize_text


def normalize_score(score: float) -> float:
    return min(max(score, 0.0), 1.0)


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
        return PersonaResult(
            persona='unknown',
            confidence=0.0,
            reasoning='No signals were identified for persona classification.',
            traits=[],
            signals=signals,
            metadata={
                'rule_scores': rule_scores,
                'llm_scores': llm_scores,
            },
        )

    selected_persona = max(combined_scores, key=combined_scores.get)
    selected_score = normalize_score(combined_scores[selected_persona] / 5.0)
    definition = get_persona_definition(selected_persona)
    reasoning = (
        f"Hybrid persona classification selected '{selected_persona}' with rule score "
        f"{rule_scores.get(selected_persona, 0.0):.2f} and llm score {llm_scores.get(selected_persona, 0.0):.2f}."
    )

    return PersonaResult(
        persona=selected_persona,
        confidence=selected_score,
        reasoning=reasoning,
        traits=definition.traits,
        signals=signals,
        metadata={
            'rule_scores': rule_scores,
            'llm_scores': llm_scores,
        },
    )


def _score_llm_signals(context: PersonaContext) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    reasoning_text = normalize_text(context.provider_reasoning or '')
    if not reasoning_text:
        return scores

    for persona, keywords in [
        ('developer', ['code', 'debug', 'compile', 'terminal', 'api', 'stack trace']),
        ('designer', ['visual', 'layout', 'ux', 'ui', 'color', 'mockup']),
        ('qa', ['bug', 'test', 'regression', 'issue', 'validation', 'error']),
        ('analyst', ['metric', 'dashboard', 'insight', 'trend', 'data', 'report']),
        ('student', ['learn', 'tutorial', 'example', 'explain', 'concept', 'practice']),
        ('shopper', ['buy', 'price', 'compare', 'purchase', 'review']),
    ]:
        score = 0.0
        for keyword in keywords:
            if keyword in reasoning_text:
                score += 1.0
        if score:
            scores[persona] = score
    return scores
