from typing import Dict, List

CONTENT_TYPE_KEYWORDS: Dict[str, List[str]] = {
    'configuration': ['tsconfig', 'package.json', 'config file', 'configuration', 'settings', 'yaml', 'yml', 'json'],
    'source_code': ['function', 'class', 'import', 'def ', 'const ', 'let ', 'var ', 'public ', 'private ', 'return', 'console.log', 'cout', 'printf'],
    'error_screen': ['error', 'exception', 'traceback', 'stack trace', 'fatal', 'null pointer', 'segmentation fault', 'typeerror', 'referenceerror'],
    'terminal_output': ['build failed', 'compile failed', 'npm install', 'yarn install', 'make:', 'command not found', 'unable to', 'failed to', 'npm err!', 'errno', 'build script', 'failed at the build'],
    'documentation': ['readme', 'guide', 'tutorial', 'reference', 'documentation'],
    'bug_report': ['bug report', 'issue tracker', 'jira', 'zendesk', 'bug', 'reproduction steps', 'expected', 'actual', 'swagger', 'api docs', 'api documentation', 'swagger api', 'api response'],
    'ui_screen': ['figma', 'mockup', 'ui', 'ux', 'design', 'layout', 'color palette', 'prototype'],
}

CONTENT_TYPE_WEIGHTS: Dict[str, float] = {
    'ocr_text': 1.2,
    'caption': 1.1,
    'labels': 0.9,
    'objects': 1.0,
    'intent': 1.3,
    'provider_reasoning': 1.0,
}


def _match_keywords(text: str, keywords: List[str]) -> int:
    normalized = (text or '').lower()
    return sum(1 for kw in keywords if kw.lower() in normalized)


def classify_content_type(context) -> Dict[str, object]:
    text_sources = {
        'ocr_text': context.ocr_text or '',
        'caption': context.vision_caption or '',
        'labels': ' '.join(context.labels or []),
        'objects': ' '.join([obj.get('label', '') for obj in context.detected_objects or []]),
        'intent': context.intent or '',
        'provider_reasoning': context.provider_reasoning or '',
    }

    scores: Dict[str, float] = {}
    for content_type, keywords in CONTENT_TYPE_KEYWORDS.items():
        score = 0.0
        for source_name, source_text in text_sources.items():
            weight = CONTENT_TYPE_WEIGHTS.get(source_name, 1.0)
            score += _match_keywords(source_text, keywords) * weight
        scores[content_type] = score

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]
    total_score = sum(scores.values())
    confidence = 0.0
    if total_score > 0:
        confidence = min(0.95, best_score / total_score)
    return {
        'content_type': best_type,
        'confidence': confidence,
        'scores': scores,
    }
