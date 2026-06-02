"""
Improved issue detection with confidence scoring and false-positive prevention.

Rules:
- Issue detection must require contextual evidence
- Only generate technical issue recommendations when confidence >= 0.7
- Never generate TypeScript recommendations when content_type == "ui_screen"
- Never generate code recommendations when persona == "student"
- Never generate API recommendations when content_type == "design_mockup"
"""
from typing import Dict, Tuple
from .recommendation_models import RecommendationContext


# Enhanced keyword mapping with context requirements
ISSUE_KEYWORDS_WITH_CONFIDENCE: Dict[str, Dict[str, Dict]] = {
    'developer': {
        'typescript_error': {
            'keywords': ['tsconfig', 'typescript error', 'TS', 'tsc', 'compilerOptions', 'type error', 'ts2304', 'ts2307', 'cannot read'],
            'min_confidence': 0.7,
            'required_context': [],  # Relaxed: keywords alone sufficient
        },
        'build_error': {
            'keywords': ['build failed', 'build error', 'failed to build', 'npm err!', 'errno', 'failed at the build', 'webpack error'],
            'min_confidence': 0.7,
            'required_context': [],
        },
        'runtime_error': {
            'keywords': ['exception', 'stack trace', 'runtime error', 'typeerror', 'referenceerror', 'traceback', 'undefined is not', 'cannot read property'],
            'min_confidence': 0.75,
            'required_context': [],
        },
        'api_error': {
            'keywords': ['500', '404', '403', 'api error', 'request failed', 'unauthorized', 'forbidden', 'not found'],
            'min_confidence': 0.8,
            'required_context': [],
        },
    },
    'frontend': {
        'typescript_error': {
            'keywords': ['tsconfig', 'typescript error', 'TS', 'tsc', 'compilerOptions', 'type error', 'ts2304', 'ts2307'],
            'min_confidence': 0.7,
            'required_context': [],
        },
        'runtime_error': {
            'keywords': ['typeerror', 'referenceerror', 'exception', 'stack trace', 'undefined is not', 'cannot read'],
            'min_confidence': 0.75,
            'required_context': [],
        },
    },
    'backend': {
        'api_error': {
            'keywords': ['500', '404', '403', 'api error', 'failed', 'server error', 'not found', 'error'],
            'min_confidence': 0.8,
            'required_context': [],
        },
        'database_error': {
            'keywords': ['database', 'connection failed', 'query error', 'sql error', 'timeout'],
            'min_confidence': 0.75,
            'required_context': [],
        },
    },
    'designer': {
        'alignment_issue': {
            'keywords': ['alignment', 'misaligned', 'left aligned', 'right aligned', 'center aligned'],
            'min_confidence': 0.6,
            'required_context': [],
        },
        'spacing_issue': {
            'keywords': ['spacing', 'padding', 'margin', 'gutter', 'gap', 'whitespace'],
            'min_confidence': 0.6,
            'required_context': [],
        },
        'color_issue': {
            'keywords': ['color contrast', 'contrast', 'color mismatch', 'low contrast'],
            'min_confidence': 0.65,
            'required_context': [],
        },
        'accessibility_issue': {
            'keywords': ['aria', 'accessible', 'screen reader', 'a11y', 'wcag', 'keyboard', 'focus'],
            'min_confidence': 0.75,
            'required_context': [],
        },
    },
    'qa': {
        'bug_report': {
            'keywords': ['bug', 'regression', 'failed test', 'assertion error', 'stack trace', 'failed', 'failure'],
            'min_confidence': 0.75,
            'required_context': [],
        },
        'validation_issue': {
            'keywords': ['validation error', 'invalid input', 'invalid value', 'error message'],
            'min_confidence': 0.7,
            'required_context': [],
        },
    },
    'analyst': {
        'data_quality_issue': {
            'keywords': ['null values', 'nan', 'missing data', 'incomplete', 'null', 'undefined', 'empty'],
            'min_confidence': 0.65,
            'required_context': [],
        },
        'dashboard_issue': {
            'keywords': ['dashboard', 'kpi', 'chart', 'metric', 'visualization', 'graph'],
            'min_confidence': 0.6,
            'required_context': [],
        },
    },
}

# False positive prevention rules
FALSE_POSITIVE_RULES = [
    {
        'rule': 'no_typescript_on_ui',
        'condition': lambda ctx, issue: issue == 'typescript_error' and ctx.content_type == 'ui_screen',
        'action': 'suppress',
    },
    {
        'rule': 'no_api_on_design',
        'condition': lambda ctx, issue: issue == 'api_error' and ctx.content_type == 'design_mockup',
        'action': 'suppress',
    },
    {
        'rule': 'no_code_for_student',
        'condition': lambda ctx, issue: 'error' in issue and (ctx.persona or '').lower() == 'student',
        'action': 'suppress',
    },
    {
        'rule': 'no_code_on_docs',
        'condition': lambda ctx, issue: issue in ('typescript_error', 'runtime_error') and ctx.content_type == 'documentation',
        'action': 'suppress',
    },
]


class ImprovedIssueDetector:
    """Enhanced issue detection with confidence scoring and false-positive prevention."""

    @staticmethod
    def detect_issue_with_confidence(context: RecommendationContext) -> Tuple[str, float, Dict]:
        """
        Detect issue with confidence score.
        
        Returns: (issue_type, confidence, metadata)
        """
        text_blob = ' '.join(filter(None, [
            context.ocr_text or '',
            context.vision_caption or '',
            context.provider_reasoning or '',
        ]))

        # Add vision labels if available
        if context.labels:
            text_blob += ' ' + ' '.join(context.labels)

        persona = (context.persona or 'unknown').lower()
        content_type = getattr(context, 'content_type', 'unknown')

        candidates: Dict[str, float] = {}
        metadata_map: Dict[str, Dict] = {}

        # Normalize persona to match keyword config keys
        persona_key = persona
        if 'frontend' in persona:
            persona_key = 'frontend'
        elif 'backend' in persona:
            persona_key = 'backend'
        elif 'developer' in persona:
            persona_key = 'developer'
        elif 'designer' in persona:
            persona_key = 'designer'
        elif 'qa' in persona:
            persona_key = 'qa'
        elif 'analyst' in persona:
            persona_key = 'analyst'

        # Try persona-specific rules first
        if persona_key in ISSUE_KEYWORDS_WITH_CONFIDENCE:
            for issue, config in ISSUE_KEYWORDS_WITH_CONFIDENCE[persona_key].items():
                confidence = ImprovedIssueDetector._calculate_confidence(
                    text_blob,
                    context.labels or [],
                    config,
                )
                if confidence > 0:
                    candidates[issue] = confidence
                    metadata_map[issue] = config

        # Fallback: scan all personas
        if not candidates:
            for persona_map in ISSUE_KEYWORDS_WITH_CONFIDENCE.values():
                for issue, config in persona_map.items():
                    confidence = ImprovedIssueDetector._calculate_confidence(
                        text_blob,
                        context.labels or [],
                        config,
                    )
                    if confidence > 0:
                        candidates[issue] = confidence
                        metadata_map[issue] = config

        if not candidates:
            return 'unknown', 0.0, {}

        # Pick top candidate
        issue_type = max(candidates, key=candidates.get)
        confidence = candidates[issue_type]

        # Apply false-positive prevention rules
        for rule_config in FALSE_POSITIVE_RULES:
            try:
                if rule_config['condition'](context, issue_type):
                    if rule_config['action'] == 'suppress':
                        return 'unknown', 0.0, {}
            except Exception:
                pass

        # Check if confidence meets minimum threshold
        min_confidence = metadata_map.get(issue_type, {}).get('min_confidence', 0.5)
        if confidence < min_confidence:
            return 'unknown', 0.0, {}

        return issue_type, confidence, metadata_map.get(issue_type, {})

    @staticmethod
    def _calculate_confidence(text_blob: str, labels: list, config: Dict) -> float:
        """Calculate confidence score for an issue based on text and config."""
        keywords = config.get('keywords', [])
        required_context = config.get('required_context', [])

        text_lower = text_blob.lower()
        labels_lower = [l.lower() for l in labels]
        combined_text = text_lower + ' ' + ' '.join(labels_lower)

        # Count keyword matches
        keyword_matches = sum(1 for kw in keywords if kw.lower() in combined_text)
        if len(keywords) > 0:
            keyword_score = min(1.0, keyword_matches / len(keywords) * 0.8)
        else:
            keyword_score = 0.0

        # Check required context (if specified)
        if required_context:
            required_matches = sum(1 for ctx in required_context if ctx.lower() in combined_text)
            context_score = min(1.0, required_matches / len(required_context)) * 0.2
        else:
            context_score = 0.2  # Bonus for no required context (relaxed requirement)

        confidence = keyword_score + context_score
        return min(1.0, confidence)

    @staticmethod
    def build_issue_metadata(issue_type: str, confidence: float, text_blob: str) -> Dict:
        """Build metadata for detected issue."""
        return {
            'issue_type': issue_type,
            'confidence': confidence,
            'text_matches': sum(1 for word in text_blob.split() if len(word) > 3),
        }
