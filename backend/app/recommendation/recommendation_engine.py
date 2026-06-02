from typing import Dict, Any, List
from .recommendation_models import RecommendationContext, RecommendationResult
from .recommendation_category_classifier import classify_content_category
from .recommendation_content_classifier import classify_content_type
from .recommendation_issue_evidence import evaluate_issue_evidence
from .root_cause_engine import infer_root_cause
from .severity_engine import assess_severity
from .issue_detector_improved import ImprovedIssueDetector
from .persona_router import PersonaAwareRecommendationRouter


class RecommendationEngine:
    def __init__(self, rule_weight: float = 1.0, intent_weight: float = 1.0):
        self.rule_weight = rule_weight
        self.intent_weight = intent_weight
        self.issue_detector = ImprovedIssueDetector()
        self.router = PersonaAwareRecommendationRouter()

    @classmethod
    def from_settings(cls):
        return cls()

    def analyze(self, context: RecommendationContext) -> RecommendationResult:
        # Classify content type
        content_type_result = classify_content_type(context)
        content_type = content_type_result.get('content_type', 'unknown')
        content_confidence = float(content_type_result.get('confidence', 0.0))

        category_result = classify_content_category(context)
        content_category = category_result.get('content_category', 'unknown')
        content_category_confidence = float(category_result.get('confidence', 0.0))

        context.content_type = content_type
        context.content_category = content_category
        context.content_category_confidence = content_category_confidence

        # Improved issue detection with confidence scoring
        issue_type, issue_confidence, detector_metadata = self.issue_detector.detect_issue_with_confidence(context)
        issue_detected = issue_type != 'unknown' and issue_confidence >= 0.5

        # Get issue evidence
        issue_evidence = evaluate_issue_evidence(context)

        ocr_confidence = float(getattr(context, 'ocr_confidence', 0.0) or 0.0)
        provider_success = bool(getattr(context, 'provider_success', False))

        # Determine analysis mode when vision provider analysis isn't available.
        analysis_mode = 'ocr_only' if not provider_success else 'hybrid'

        # Generate persona-aware recommendations
        recommendations_output = self.router.generate_recommendations(
            context,
            issue_detected,
            issue_type if issue_detected else 'none',
        )

        summary = recommendations_output.get('summary', '')
        insights = recommendations_output.get('insights', [])
        possible_actions = recommendations_output.get('possible_actions', [])
        recommendations = recommendations_output.get('recommendations', possible_actions)
        fixes = recommendations_output.get('fixes', []) if issue_detected else []
        alternatives = recommendations_output.get('alternative_solutions', [])

        # Calculate combined confidence
        if issue_detected:
            dominance = float(detector_metadata.get('dominance', 0.5)) if isinstance(detector_metadata, dict) else 0.5
            evidence_score = float(issue_evidence.get('error_score', 0)) / 5.0
            provider_factor = 1.0 if provider_success else 0.85
            combined_confidence = min(
                0.95,
                provider_factor * (
                    0.40 * issue_confidence
                    + 0.30 * min(1.0, evidence_score)
                    + 0.15 * content_confidence
                    + 0.15 * min(1.0, ocr_confidence)
                )
            )
            combined_confidence = max(0.1, combined_confidence)

            # Assess severity
            severity = assess_severity(issue_type, context, combined_confidence)

            # Infer root cause
            root = infer_root_cause(issue_type, context)
            root_cause = root.get('primary_root_cause') if root else None
        else:
            combined_confidence = min(
                0.90,
                max(
                    0.0,
                    (1.0 if provider_success else 0.8) * (
                        0.45 * content_confidence
                        + 0.30 * min(1.0, ocr_confidence)
                        + 0.25 * (1.0 - min(1.0, issue_evidence.get('error_score', 0) / 5.0))
                    )
                )
            )
            severity = None
            root_cause = None

        needs_human_review = combined_confidence < 0.4 or content_category == 'unknown'

        result = RecommendationResult(
            issue_detected=issue_detected,
            content_type=content_type,
            content_category=content_category,
            content_category_confidence=content_category_confidence,
            persona=context.persona,
            summary=summary,
            insights=insights,
            recommendations=recommendations,
            possible_actions=possible_actions,
            issue_type=issue_type if issue_detected else None,
            root_cause=root_cause,
            severity=severity,
            fixes=fixes,
            alternative_solutions=alternatives,
            step_by_step_fix=fixes,
            suggested_actions=possible_actions,
            confidence=combined_confidence,
            analysis_mode=analysis_mode,
            needs_human_review=needs_human_review,
            metadata={
                'detector_metadata': detector_metadata,
                'content_type_result': content_type_result,
                'content_category_result': category_result,
                'issue_evidence': issue_evidence,
                'issue_confidence': issue_confidence,
                'persona': context.persona,
                'intent': context.intent,
            },
        )

        return result
