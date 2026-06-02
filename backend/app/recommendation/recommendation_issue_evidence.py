from typing import Dict, List

ERROR_KEYWORDS: List[str] = [
    'error',
    'exception',
    'failed',
    'failure',
    'cannot',
    'unable',
    'crash',
    'warning',
    'fatal',
    'traceback',
    'stack trace',
    'ts2307',
    'ts2345',
    'module not found',
    'undefined',
    'referenceerror',
    'typeerror',
    'syntaxerror',
    'build failed',
    'compile failed',
]


def _count_evidence(text: str) -> int:
    normalized = (text or '').lower()
    return sum(1 for keyword in ERROR_KEYWORDS if keyword in normalized)


def evaluate_issue_evidence(context) -> Dict[str, object]:
    text = ' '.join(filter(None, [context.ocr_text or '', context.vision_caption or '', context.provider_reasoning or '']))
    label_text = ' '.join(context.labels or [])
    object_text = ' '.join([obj.get('label', '') for obj in context.detected_objects or []])
    combined = ' '.join(filter(None, [text, label_text, object_text]))

    error_score = _count_evidence(combined)
    matched = [kw for kw in ERROR_KEYWORDS if kw in combined.lower()]
    issue_detected = error_score > 0

    return {
        'issue_detected': issue_detected,
        'error_score': error_score,
        'matched_evidence': matched,
    }
