from typing import Dict, Any


SEVERITY_PRIORITY = ['critical', 'high', 'medium', 'low', 'informational']


def assess_severity(issue_type: str, context, confidence: float) -> str:
    text = ' '.join(filter(None, [context.ocr_text or '', context.provider_reasoning or ''])).lower()
    # Production indicators
    if 'outage' in text or 'production' in text or 'downtime' in text:
        return 'critical'

    if issue_type in ('runtime_error', 'api_error', 'authentication_error'):
        return 'high' if confidence > 0.5 else 'medium'

    if issue_type in ('build_error', 'compilation_error', 'dependency_issue'):
        return 'high'

    if issue_type in ('alignment_issue', 'spacing_issue', 'color_issue', 'typography_issue', 'ux_issue'):
        return 'medium'

    if issue_type in ('learning_question', 'product_comparison'):
        return 'low'

    if issue_type == 'unknown':
        return 'informational'

    return 'medium'
