from collections import defaultdict
from typing import Dict, List, Tuple

PERSONA_KEYWORD_SCORES: Dict[str, List[str]] = {
    'developer': ['code', 'debug', 'compile', 'terminal', 'stack trace', 'api request', 'function', 'variable'],
    'designer': ['mockup', 'visual', 'ui', 'ux', 'layout', 'typography', 'color palette', 'design system'],
    'qa': ['bug', 'test', 'reproduce', 'regression', 'issue', 'assertion', 'validation', 'quality'],
    'analyst': ['metric', 'dashboard', 'analytics', 'data', 'insight', 'trend', 'kpi', 'report'],
    'student': ['learn', 'tutorial', 'example', 'explain', 'concept', 'practice', 'question', 'study'],
    'shopper': ['buy', 'price', 'compare', 'purchase', 'sale', 'offer', 'product', 'review'],
}

OBJECT_PATTERNS: Dict[str, List[str]] = {
    'developer': ['editor', 'terminal', 'code snippet', 'stack trace', 'diff'],
    'designer': ['wireframe', 'color swatch', 'composition', 'interface', 'button', 'layout'],
    'qa': ['test case', 'bug report', 'error message', 'checklist', 'screenshot of failure'],
    'analyst': ['chart', 'graph', 'dashboard', 'spreadsheet', 'table', 'report'],
    'student': ['lecture', 'notebook', 'flashcard', 'example problem', 'learning module'],
    'shopper': ['shopping cart', 'item listing', 'price tag', 'coupon', 'checkout'],
}


def normalize_text(text: str) -> str:
    return text.lower().strip() if text else ''


def score_keyword_signals(text: str) -> Dict[str, float]:
    normalized = normalize_text(text)
    scores = defaultdict(float)
    for persona, keywords in PERSONA_KEYWORD_SCORES.items():
        for keyword in keywords:
            if keyword in normalized:
                scores[persona] += 1.0
    return scores


def score_object_signals(objects: List[str]) -> Dict[str, float]:
    scores = defaultdict(float)
    for persona, patterns in OBJECT_PATTERNS.items():
        for obj in objects:
            normalized_obj = normalize_text(obj)
            for pattern in patterns:
                if pattern in normalized_obj:
                    scores[persona] += 1.0
    return scores


def aggregate_rule_scores(
    ocr_text: str,
    caption: str,
    labels: List[str],
    objects: List[str],
    intent: str,
    provider_reasoning: str,
    metadata: Dict[str, any],
) -> Tuple[Dict[str, float], List[Dict[str, any]]]:
    rule_scores = defaultdict(float)
    signals = []

    if ocr_text:
        text_scores = score_keyword_signals(ocr_text)
        for persona, score in text_scores.items():
            if score:
                rule_scores[persona] += score * 1.2
                signals.append({
                    'source': 'ocr_text',
                    'persona': persona,
                    'score': score * 1.2,
                    'evidence': ocr_text,
                })

    if caption:
        caption_scores = score_keyword_signals(caption)
        for persona, score in caption_scores.items():
            if score:
                rule_scores[persona] += score
                signals.append({
                    'source': 'caption',
                    'persona': persona,
                    'score': score,
                    'evidence': caption,
                })

    if labels:
        label_scores = score_keyword_signals(' '.join(labels))
        for persona, score in label_scores.items():
            if score:
                rule_scores[persona] += score * 0.8
                signals.append({
                    'source': 'labels',
                    'persona': persona,
                    'score': score * 0.8,
                    'evidence': ','.join(labels),
                })

    if objects:
        object_scores = score_object_signals(objects)
        for persona, score in object_scores.items():
            if score:
                rule_scores[persona] += score * 1.0
                signals.append({
                    'source': 'objects',
                    'persona': persona,
                    'score': score,
                    'evidence': ','.join(objects),
                })

    if intent:
        intent_scores = score_keyword_signals(intent)
        for persona, score in intent_scores.items():
            if score:
                rule_scores[persona] += score * 1.5
                signals.append({
                    'source': 'intent',
                    'persona': persona,
                    'score': score * 1.5,
                    'evidence': intent,
                })

    if provider_reasoning:
        reasoning_scores = score_keyword_signals(provider_reasoning)
        for persona, score in reasoning_scores.items():
            if score:
                rule_scores[persona] += score * 0.9
                signals.append({
                    'source': 'provider_reasoning',
                    'persona': persona,
                    'score': score * 0.9,
                    'evidence': provider_reasoning,
                })

    historical_text = ''
    if metadata:
        historical_text = ' '.join([str(value) for value in metadata.values() if isinstance(value, str)])
        history_scores = score_keyword_signals(historical_text)
        for persona, score in history_scores.items():
            if score:
                rule_scores[persona] += score * 0.7
                signals.append({
                    'source': 'historical_meta',
                    'persona': persona,
                    'score': score * 0.7,
                    'evidence': historical_text,
                })

    return dict(rule_scores), signals
