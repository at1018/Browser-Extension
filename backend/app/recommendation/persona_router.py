"""
Content-type and persona-based routing for recommendations.

Maps content type + persona to the appropriate recommendation handler.
"""
from typing import Dict, Type
from .recommendation_models import RecommendationContext
from .recommendation_handlers import (
    BaseRecommendationHandler,
    DesignerRecommendationHandler,
    FrontendDeveloperRecommendationHandler,
    BackendDeveloperRecommendationHandler,
    QARecommendationHandler,
    StudentRecommendationHandler,
    DataAnalystRecommendationHandler,
    SecurityEngineerRecommendationHandler,
    GenericRecommendationHandler,
)

# Registry of persona handlers
PERSONA_HANDLERS: Dict[str, Type[BaseRecommendationHandler]] = {
    'designer': DesignerRecommendationHandler,
    'frontend_developer': FrontendDeveloperRecommendationHandler,
    'frontend': FrontendDeveloperRecommendationHandler,
    'backend_developer': BackendDeveloperRecommendationHandler,
    'backend': BackendDeveloperRecommendationHandler,
    'qa_engineer': QARecommendationHandler,
    'qa': QARecommendationHandler,
    'student': StudentRecommendationHandler,
    'analyst': DataAnalystRecommendationHandler,
    'data_analyst': DataAnalystRecommendationHandler,
    'security_engineer': SecurityEngineerRecommendationHandler,
    'security': SecurityEngineerRecommendationHandler,
}


class PersonaAwareRecommendationRouter:
    """Routes recommendations based on persona and content type."""

    @staticmethod
    def get_handler(persona: str) -> BaseRecommendationHandler:
        """Get recommendation handler for persona."""
        persona_lower = (persona or 'unknown').lower().strip()

        # Try exact match
        if persona_lower in PERSONA_HANDLERS:
            return PERSONA_HANDLERS[persona_lower]()

        # Try partial match
        for registered_persona, handler_class in PERSONA_HANDLERS.items():
            if registered_persona in persona_lower or persona_lower in registered_persona:
                return handler_class()

        # Default to generic
        return GenericRecommendationHandler()

    @staticmethod
    def generate_recommendations(
        context: RecommendationContext,
        issue_detected: bool,
        issue_type: str,
    ) -> Dict:
        """
        Generate persona-specific recommendations based on content type and issue.

        Returns dict with:
        - summary: brief recommendation summary
        - insights: list of insights specific to persona
        - possible_actions: actionable steps
        - fixes: specific fixes (if issue_detected)
        - alternative_solutions: alternatives to consider
        """
        handler = PersonaAwareRecommendationRouter.get_handler(context.persona or 'unknown')
        result = handler.generate(context, issue_detected, issue_type)
        return result

    @staticmethod
    def get_content_type_summary(content_type: str) -> str:
        """Get summary description for content type."""
        summaries = {
            'ui_screen': 'User Interface Screenshot',
            'source_code': 'Source Code',
            'terminal_output': 'Terminal/Console Output',
            'documentation': 'Documentation',
            'student_material': 'Student Material',
            'dashboard': 'Analytics Dashboard',
            'design_mockup': 'Design Mockup',
            'configuration': 'Configuration File',
            'error_screen': 'Error Screen',
            'bug_report': 'Bug Report',
        }
        return summaries.get(content_type, content_type)
