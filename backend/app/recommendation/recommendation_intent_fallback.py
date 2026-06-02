from typing import List

CODE_KEYWORDS: List[str] = ['tsconfig', 'typescript', 'import', 'def ', 'class ', 'public ', 'private ', 'const ', 'let ', 'var ', 'function', 'return', 'console.log']
DESIGN_KEYWORDS: List[str] = ['figma', 'ui', 'ux', 'design', 'mockup', 'prototype', 'layout', 'color', 'typography']
SHOPPING_KEYWORDS: List[str] = ['price', 'buy', 'checkout', 'cart', 'discount', 'product', 'compare']
TESTING_KEYWORDS: List[str] = ['test', 'assert', 'assertion', 'regression', 'failed test', 'bug', 'coverage']
ANALYTICS_KEYWORDS: List[str] = ['dashboard', 'kpi', 'chart', 'metrics', 'analytics', 'report', 'data quality']
STUDENT_KEYWORDS: List[str] = ['tutorial', 'how to', 'example', 'explain', 'learn', 'study', 'documentation']


def _text_from_context(context) -> str:
    parts = [
        context.ocr_text or '',
        context.vision_caption or '',
        ' '.join(context.labels or []),
        ' '.join([obj.get('label', '') for obj in context.detected_objects or []]),
        context.provider_reasoning or '',
    ]
    return ' '.join(filter(None, parts)).lower()


def fallback_intent(context) -> str:
    text = _text_from_context(context)
    if any(keyword in text for keyword in CODE_KEYWORDS):
        return 'code'
    if any(keyword in text for keyword in DESIGN_KEYWORDS):
        return 'design'
    if any(keyword in text for keyword in SHOPPING_KEYWORDS):
        return 'shopping'
    if any(keyword in text for keyword in TESTING_KEYWORDS):
        return 'testing'
    if any(keyword in text for keyword in ANALYTICS_KEYWORDS):
        return 'analytics'
    if any(keyword in text for keyword in STUDENT_KEYWORDS):
        return 'student'
    return 'unknown'
