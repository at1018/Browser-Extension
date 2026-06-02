from typing import Dict, Any, Tuple, List


def infer_root_cause(issue_type: str, context) -> Dict[str, Any]:
    text = ' '.join(filter(None, [context.ocr_text or '', context.provider_reasoning or ''])).lower()
    primary = 'unknown'
    contributing: List[str] = []
    confidence = 0.0

    if issue_type in ('typescript_error', 'build_error', 'compilation_error'):
        if 'tsconfig' in text or 'compileroptions' in text:
            primary = 'tsconfig.json contains incompatible compiler options'
            if 'isolatedmodules' in text:
                contributing.append('isolatedModules enabled')
            if 'moduleresolution' in text:
                contributing.append('moduleResolution mismatch')
            confidence = 0.85
        else:
            primary = 'compiler or build configuration error'
            confidence = 0.6

    elif issue_type in ('alignment_issue', 'spacing_issue', 'color_issue'):
        primary = 'design/layout inconsistency'
        confidence = 0.6
        if 'contrast' in text:
            contributing.append('insufficient color contrast')

    elif issue_type in ('bug_report', 'failed_test', 'regression'):
        primary = 'reproducible bug in code or tests'
        confidence = 0.7
        if 'assert' in text or 'assertion' in text:
            contributing.append('assertion failure in test')

    elif issue_type in ('data_quality_issue', 'missing_metrics'):
        primary = 'data ingestion or aggregation problem'
        confidence = 0.7

    elif issue_type in ('learning_question', 'concept_confusion'):
        primary = 'knowledge gap or unclear documentation'
        confidence = 0.5

    elif issue_type in ('product_comparison', 'pricing_question'):
        primary = 'clarification needed for product/pricing details'
        confidence = 0.5

    else:
        primary = 'unclear — needs human review'
        confidence = 0.3

    return {
        'primary_root_cause': primary,
        'contributing_factors': contributing,
        'confidence': confidence,
    }
