from collections import defaultdict
from typing import Any, Dict, List, Tuple

from app.core.config import settings
from app.persona.persona_models import DetectObject

PERSONA_KEYWORD_SCORES: Dict[str, List[str]] = {
    'developer': [
        'code', 'source code', 'programming', 'software', 'developer', 'engineer',
        'terminal', 'command line', 'shell', 'bash', 'powershell', 'git', 'github',
        'gitlab', 'pull request', 'merge request', 'repository', 'branch', 'commit',
        'vscode', 'visual studio', 'intellij', 'pycharm', 'eclipse', 'debugger',
        'debug', 'stack trace', 'exception', 'error', 'api', 'rest', 'graphql',
        'backend', 'frontend', 'full stack', 'react', 'angular', 'vue', 'nextjs',
        'nodejs', 'express', 'typescript', 'javascript', 'python', 'java', 'c#',
        'c++', 'golang', 'rust', 'sql', 'mongodb', 'postgres', 'mysql', 'redis',
        'docker', 'kubernetes', 'helm', 'terraform', 'aws', 'azure', 'gcp',
        'ci/cd', 'pipeline', 'deployment', 'microservice', 'tsconfig', 'package.json',
        'yaml', 'json', 'configuration', 'compiler', 'module', 'build', 'npm',
        'yarn', 'pnpm', 'pytest', 'unittest', 'integration test',
    ],
    'designer': [
        'design', 'designer', 'ui', 'ux', 'visual design', 'prototype', 'wireframe',
        'mockup', 'figma', 'adobe xd', 'sketch', 'typography', 'spacing',
        'color palette', 'design system', 'component library', 'user flow',
        'interaction design', 'accessibility', 'branding', 'iconography',
        'illustration', 'layout', 'responsive design',
    ],
    'qa': [
        'qa', 'quality assurance', 'testing', 'automation', 'selenium', 'playwright',
        'cypress', 'regression', 'smoke test', 'bug', 'defect', 'issue', 'jira',
        'testcase', 'validation', 'assertion', 'failed test', 'test suite',
        'test execution', 'bug report',
    ],
    'analyst': [
        'analytics', 'dashboard', 'data', 'metrics', 'kpi', 'report', 'trend',
        'business intelligence', 'tableau', 'power bi', 'excel', 'spreadsheet',
        'sql', 'visualization', 'chart', 'graph', 'forecast', 'insights',
        'revenue', 'growth', 'conversion', 'engagement',
    ],
    'student': [
        'learning', 'tutorial', 'explain', 'lesson', 'course', 'classroom',
        'study', 'practice', 'homework', 'assignment', 'notes', 'lecture',
        'concept', 'example', 'training', 'certification', 'education',
        'quiz', 'exam',
    ],
    'shopper': [
        'buy', 'purchase', 'compare', 'shopping', 'cart', 'checkout', 'offer',
        'discount', 'coupon', 'review', 'rating', 'product', 'price',
        'marketplace', 'ecommerce', 'amazon', 'flipkart', 'ebay',
    ],
}

OBJECT_PATTERNS: Dict[str, List[str]] = {
    'developer': [
        'code editor', 'terminal', 'source file', 'json file', 'yaml file', 'tsconfig',
        'package.json', 'stack trace', 'log viewer', 'api response', 'swagger',
        'postman', 'repository', 'pull request', 'commit history', 'ci pipeline',
        'docker container', 'kubernetes dashboard',
    ],
    'designer': [
        'figma canvas', 'wireframe', 'prototype', 'design board', 'component library',
        'color palette', 'design system', 'mobile mockup', 'desktop mockup', 'artboard',
    ],
    'qa': [
        'test report', 'bug report', 'failed testcase', 'regression dashboard',
        'automation report', 'execution summary', 'error screenshot', 'jira ticket',
    ],
    'analyst': [
        'dashboard', 'chart', 'graph', 'spreadsheet', 'table', 'report',
        'analytics panel', 'kpi board',
    ],
    'student': [
        'notebook', 'textbook', 'lecture slide', 'course page', 'learning portal',
        'flashcard', 'assignment',
    ],
    'shopper': [
        'product card', 'shopping cart', 'checkout page', 'product listing',
        'coupon banner', 'price tag', 'review section',
    ],
}

INTENT_KEYWORD_SCORES: Dict[str, List[str]] = {
    'developer': ['code', 'coding', 'programming'],
    'designer': ['ui', 'ux', 'design'],
    'qa': ['bug', 'testing', 'test', 'defect'],
    'analyst': ['analytics', 'report', 'dashboard', 'insight'],
    'student': ['learning', 'education', 'tutorial', 'lesson', 'study'],
    'shopper': ['shopping', 'buying', 'purchase', 'checkout'],
}


def normalize_text(text: str) -> str:
    return text.lower().strip() if text else ''


def score_keyword_signals(text: str, score_map: Dict[str, List[str]]) -> Dict[str, float]:
    normalized = normalize_text(text)
    scores = defaultdict(float)
    for persona, keywords in score_map.items():
        for keyword in keywords:
            if keyword in normalized:
                scores[persona] += 1.0
    return scores


def detect_object_label(obj: Any) -> str:
    if isinstance(obj, str):
        return normalize_text(obj)
    if isinstance(obj, dict):
        return normalize_text(obj.get('label') or obj.get('name') or '')
    if hasattr(obj, 'label'):
        return normalize_text(getattr(obj, 'label', '') or '')
    return normalize_text(str(obj))


def score_object_signals(objects: List[Any]) -> Dict[str, float]:
    scores = defaultdict(float)
    for persona, patterns in OBJECT_PATTERNS.items():
        for obj in objects:
            normalized_obj = detect_object_label(obj)
            for pattern in patterns:
                if pattern in normalized_obj:
                    scores[persona] += 1.0
    return scores


def score_intent_signals(intent: str) -> Dict[str, float]:
    return score_keyword_signals(intent, INTENT_KEYWORD_SCORES)


def aggregate_rule_scores(
    ocr_text: str,
    caption: str,
    labels: List[str],
    objects: List[Any],
    intent: str,
    provider_reasoning: str,
    metadata: Dict[str, Any],
) -> Tuple[Dict[str, float], List[Dict[str, Any]]]:
    rule_scores = defaultdict(float)
    signals = []

    if ocr_text:
        text_scores = score_keyword_signals(ocr_text, PERSONA_KEYWORD_SCORES)
        for persona, score in text_scores.items():
            if score:
                weight = 1.4
                rule_scores[persona] += score * weight
                signals.append({
                    'source': 'ocr_text',
                    'persona': persona,
                    'score': score * weight,
                    'evidence': ocr_text,
                })

    if caption:
        caption_scores = score_keyword_signals(caption, PERSONA_KEYWORD_SCORES)
        for persona, score in caption_scores.items():
            if score:
                weight = 1.1
                rule_scores[persona] += score * weight
                signals.append({
                    'source': 'caption',
                    'persona': persona,
                    'score': score * weight,
                    'evidence': caption,
                })

    if labels:
        label_scores = score_keyword_signals(' '.join(labels), PERSONA_KEYWORD_SCORES)
        for persona, score in label_scores.items():
            if score:
                weight = 0.9
                rule_scores[persona] += score * weight
                signals.append({
                    'source': 'labels',
                    'persona': persona,
                    'score': score * weight,
                    'evidence': ','.join(labels),
                })

    if objects:
        object_scores = score_object_signals(objects)
        for persona, score in object_scores.items():
            if score:
                weight = 1.2
                rule_scores[persona] += score * weight
                signals.append({
                    'source': 'objects',
                    'persona': persona,
                    'score': score * weight,
                    'evidence': ','.join([detect_object_label(obj) for obj in objects]),
                })

    if intent:
        intent_scores = score_intent_signals(intent)
        for persona, score in intent_scores.items():
            if score:
                weight = settings.PERSONA_INTENT_WEIGHT
                rule_scores[persona] += score * weight
                signals.append({
                    'source': 'intent',
                    'persona': persona,
                    'score': score * weight,
                    'evidence': intent,
                })

    if provider_reasoning:
        reasoning_scores = score_keyword_signals(provider_reasoning, PERSONA_KEYWORD_SCORES)
        for persona, score in reasoning_scores.items():
            if score:
                weight = 1.0
                rule_scores[persona] += score * weight
                signals.append({
                    'source': 'provider_reasoning',
                    'persona': persona,
                    'score': score * weight,
                    'evidence': provider_reasoning,
                })

    if metadata:
        historical_text = ' '.join([str(value) for value in metadata.values() if isinstance(value, str)])
        history_scores = score_keyword_signals(historical_text, PERSONA_KEYWORD_SCORES)
        for persona, score in history_scores.items():
            if score:
                weight = 0.7
                rule_scores[persona] += score * weight
                signals.append({
                    'source': 'historical_meta',
                    'persona': persona,
                    'score': score * weight,
                    'evidence': historical_text,
                })

    return dict(rule_scores), signals
