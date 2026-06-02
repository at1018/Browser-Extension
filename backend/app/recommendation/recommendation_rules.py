from typing import Dict, List, Tuple

# Keyword maps per persona/area -> issue types
ISSUE_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    'developer': {
        'typescript_error': ['tsconfig', 'typescript error', 'TS', 'tsc', 'compilerOptions'],
        'build_error': ['build failed', 'build error', 'failed to build', 'npm err!', 'errno', 'failed at the build'],
        'dependency_issue': ['npm install', 'package.json', 'dependency', 'missing module'],
        'lint_error': ['eslint', 'lint error', 'linting'],
        'runtime_error': ['exception', 'stack trace', 'runtime error', 'typeerror', 'referenceerror', 'traceback'],
        'api_error': ['500', '404', 'api error', 'request failed'],
    },
    'designer': {
        'alignment_issue': ['alignment', 'misaligned', 'left aligned', 'right aligned'],
        'spacing_issue': ['spacing', 'padding', 'margin', 'gutter'],
        'color_issue': ['color contrast', 'contrast', 'color mismatch'],
        'typography_issue': ['font-size', 'typography', 'font weight'],
        'ux_issue': ['ux', 'usability', 'discoverability'],
        'accessibility_issue': ['aria', 'accessible', 'screen reader', 'a11y'],
    },
    'qa': {
        'bug_report': ['bug', 'regression', 'failed test', 'assertion error', 'stack trace', 'swagger', 'api docs', 'api documentation'],
        'failed_test': ['failed test', 'assertion failed', 'test failure'],
        'validation_issue': ['validation error', 'invalid input'],
    },
    'analyst': {
        'dashboard_issue': ['dashboard', 'kpi', 'chart', 'visualization'],
        'data_quality_issue': ['null values', 'nan', 'missing data', 'incomplete data'],
        'missing_metrics': ['metric missing', 'no data', 'empty chart'],
    },
    'student': {
        'learning_question': ['how do i', 'how to', 'tutorial', 'example', 'explain'],
        'concept_confusion': ['confused', 'dont understand', 'unclear'],
    },
    'shopper': {
        'product_comparison': ['compare', 'comparison', 'vs', 'vs.'],
        'pricing_question': ['price', 'cost', 'discount', 'coupon'],
        'purchasing_decision': ['add to cart', 'buy now', 'checkout'],
    },
}


def _match_keywords(text: str, keywords: List[str]) -> int:
    t = (text or '').lower()
    score = 0
    for kw in keywords:
        if kw.lower() in t:
            score += 1
    return score


def classify_issue(context, issue_detected: bool = True) -> Tuple[str, Dict]:
    """Return (issue_type, metadata) detected from context using simple keyword rules."""
    if not issue_detected:
        return 'unknown', {'scores': {}, 'matched': {}, 'top_score': 0.0, 'dominance': 0.0}

    text_blob = ' '.join(filter(None, [context.ocr_text or '', context.vision_caption or '', context.provider_reasoning or '']))
    persona = (context.persona or 'unknown').lower()

    candidates: Dict[str, int] = {}
    # Try persona-specific rules first
    if persona in ISSUE_KEYWORDS:
        for issue, kws in ISSUE_KEYWORDS[persona].items():
            score = _match_keywords(text_blob, kws) + _match_keywords(' '.join(context.labels or []), kws)
            if score > 0:
                candidates[issue] = candidates.get(issue, 0) + score

    # Fallback: scan all personas
    if not candidates:
        for persona_map in ISSUE_KEYWORDS.values():
            for issue, kws in persona_map.items():
                score = _match_keywords(text_blob, kws) + _match_keywords(' '.join(context.labels or []), kws)
                if score > 0:
                    candidates[issue] = candidates.get(issue, 0) + score

    if not candidates:
        return 'unknown', {'scores': {}, 'matched': {}, 'top_score': 0.0, 'dominance': 0.0}

    # pick top candidate
    sorted_c = sorted(candidates.items(), key=lambda kv: kv[1], reverse=True)
    issue_type, top_score = sorted_c[0]
    if len(sorted_c) == 1:
        dominance = 1.0 if top_score > 0 else 0.0
    else:
        runner_up = sorted_c[1][1]
        dominance = float(top_score - runner_up) / float(top_score) if top_score else 0.0
    metadata = {
        'scores': dict(sorted_c),
        'top_score': top_score,
        'dominance': dominance,
    }
    return issue_type, metadata
