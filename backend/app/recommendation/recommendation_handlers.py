"""
Persona-specific recommendation handlers.

Each handler generates domain-specific recommendations based on:
- detected persona
- content type
- intent
- issues detected
- OCR/vision provider confidence
"""
from typing import Dict, List, Any
from .recommendation_models import RecommendationContext


class BaseRecommendationHandler:
    """Base class for all persona-specific recommendation handlers."""

    persona_name: str = 'generic'

    def generate(self, context: RecommendationContext, issue_detected: bool, issue_type: str) -> Dict[str, Any]:
        """
        Generate persona-specific recommendations.
        
        Returns dict with:
        - summary: brief recommendation summary
        - insights: list of insights specific to this persona
        - possible_actions: actionable steps
        - fixes: specific fixes (if issue_detected)
        - alternative_solutions: alternatives to consider
        """
        if issue_detected:
            return self._generate_issue_recommendations(context, issue_type)
        else:
            return self._generate_noissue_insights(context)

    def _generate_issue_recommendations(self, context: RecommendationContext, issue_type: str) -> Dict[str, Any]:
        """Generate recommendations for detected issues."""
        return {
            'summary': f'{self.persona_name.title()} perspective: {issue_type}',
            'insights': [],
            'possible_actions': [],
            'fixes': [],
            'alternative_solutions': [],
        }

    def _generate_noissue_insights(self, context: RecommendationContext) -> Dict[str, Any]:
        """Generate insights when no issue is detected."""
        return {
            'summary': f'No issues detected from {self.persona_name} perspective.',
            'insights': [],
            'possible_actions': [],
            'fixes': [],
            'alternative_solutions': [],
        }


class DesignerRecommendationHandler(BaseRecommendationHandler):
    """Generates design-specific recommendations."""

    persona_name = 'designer'

    def _generate_issue_recommendations(self, context: RecommendationContext, issue_type: str) -> Dict[str, Any]:
        """Design-specific issue handling."""
        insights = []
        fixes = []
        possible_actions = []
        alternatives = []

        if issue_type in ('alignment_issue', 'spacing_issue', 'color_issue', 'typography_issue'):
            insights = [
                'Design system compliance issue detected.',
                'Visual consistency check needed.',
            ]
            fixes = [
                'Review spacing tokens and apply consistently.',
                'Verify component alignment with grid system.',
                'Check color contrast ratios for accessibility.',
            ]
            possible_actions = [
                'Audit design file for inconsistencies.',
                'Use design system validator.',
                'Compare against design tokens library.',
            ]
            alternatives = [
                'Apply grid-based alignment system.',
                'Use spacing scale consistently.',
                'Implement automated design checks.',
            ]
        elif issue_type == 'accessibility_issue':
            insights = [
                'Accessibility concern identified.',
                'WCAG compliance review recommended.',
            ]
            fixes = [
                'Add proper ARIA labels.',
                'Improve color contrast ratios.',
                'Ensure keyboard navigation support.',
            ]
            possible_actions = [
                'Test with screen readers.',
                'Run accessibility audit tools.',
                'Review WCAG guidelines.',
            ]
            alternatives = [
                'Use accessible component library.',
                'Implement automated a11y testing.',
            ]
        elif issue_type == 'ux_issue':
            insights = [
                'Potential UX improvement opportunity.',
                'User flow enhancement possible.',
            ]
            fixes = [
                'Simplify user interaction steps.',
                'Improve visual hierarchy.',
                'Add clearer call-to-action.',
            ]
            possible_actions = [
                'Conduct user testing.',
                'Analyze user feedback.',
                'Create improved wireframes.',
            ]
            alternatives = [
                'A/B test variations.',
                'Implement progressive disclosure.',
            ]
        else:
            insights = [
                'Design review recommended for the detected screen type.',
                f"Use the {context.content_category or 'visual'} context to focus the review.",
            ]
            fixes = [
                'Review component spacing relative to the detected layout.',
                'Check contrast and hierarchy for the current screen type.',
            ]
            possible_actions = [
                'Validate the layout against the most likely page type.',
                'Confirm text clarity and CTA prominence.',
            ]

        return {
            'summary': 'Design System & UX Review',
            'insights': insights,
            'possible_actions': possible_actions,
            'fixes': fixes,
            'alternative_solutions': alternatives,
        }

    def _generate_noissue_insights(self, context: RecommendationContext) -> Dict[str, Any]:
        """Design insights when no issues detected."""
        category = context.content_category or 'unknown'
        if category == 'login_screen':
            possible_actions = [
                'Ensure the login CTA is visible and the form is uncluttered.',
                'Confirm password field accessibility and label clarity.',
                'Use strong visual hierarchy for input fields and action buttons.',
            ]
            insights = [
                'Login screen layout appears stable.',
                'Ensure user focus remains on primary sign-in action.',
            ]
        elif category == 'dashboard':
            possible_actions = [
                'Verify that the top KPI cards are prioritized correctly.',
                'Confirm charts use consistent color and labels.',
                'Review spacing between sections for scannability.',
            ]
            insights = [
                'Dashboard elements appear well-structured.',
                'Focus on readability and data hierarchy.',
            ]
        elif category == 'ecommerce_product_page':
            possible_actions = [
                'Emphasize product value with a clear price and CTA.',
                'Ensure reviews and trust signals are visible near purchase actions.',
                'Simplify product information and remove distractions.',
            ]
            insights = [
                'Product page layout is appropriate for conversion review.',
                'Focus on trust and clarity around purchase actions.',
            ]
        else:
            possible_actions = [
                'Review spacing and alignment consistency.',
                'Check typography hierarchy.',
                'Verify color palette consistency.',
                'Audit accessibility compliance.',
            ]
            insights = [
                'Visual design appears consistent.',
                'Consider proactive design improvements.',
            ]

        return {
            'summary': 'Design review completed.',
            'insights': insights,
            'possible_actions': possible_actions,
            'fixes': [],
            'alternative_solutions': [],
        }


class FrontendDeveloperRecommendationHandler(BaseRecommendationHandler):
    """Generates frontend/React-specific recommendations."""

    persona_name = 'frontend_developer'

    def _generate_issue_recommendations(self, context: RecommendationContext, issue_type: str) -> Dict[str, Any]:
        """Frontend-specific issue handling."""
        insights = []
        fixes = []
        possible_actions = []
        alternatives = []

        if issue_type == 'typescript_error':
            insights = [
                'TypeScript compilation error detected.',
                'Type safety violation found.',
            ]
            fixes = [
                'Verify tsconfig.json compilerOptions.',
                'Check moduleResolution and isolatedModules settings.',
                'Run `tsc --noEmit` to surface compiler errors.',
                'Add missing type definitions.',
            ]
            possible_actions = [
                'Open tsconfig.json.',
                'Validate compilerOptions values.',
                'Run TypeScript compiler and inspect output.',
                'Fix reported errors and re-run build.',
            ]
            alternatives = [
                'Restore tsconfig from template.',
                'Install missing @types package.',
                'Use `any` type temporarily (not recommended).',
            ]
        elif issue_type == 'build_error':
            insights = [
                'Build process failure detected.',
                'Check webpack/bundler configuration.',
            ]
            fixes = [
                'Check build logs for detailed errors.',
                'Verify all dependencies are installed.',
                'Check for circular imports.',
                'Review loader configurations.',
            ]
            possible_actions = [
                'Clear node_modules and reinstall.',
                'Run build with verbose logging.',
                'Check for missing environment variables.',
            ]
            alternatives = [
                'Use different bundler (Vite, esbuild).',
                'Downgrade to known-good dependency version.',
            ]
        elif issue_type == 'runtime_error':
            insights = [
                'Runtime JavaScript error detected.',
                'Stack trace analysis recommended.',
            ]
            fixes = [
                'Inspect browser console for errors.',
                'Add error boundaries for React.',
                'Check for null/undefined references.',
                'Verify component lifecycle hooks.',
            ]
            possible_actions = [
                'Enable source maps for debugging.',
                'Add console logging and breakpoints.',
                'Use React DevTools to inspect component state.',
            ]
            alternatives = [
                'Add error logging service.',
                'Implement graceful error handling.',
            ]
        elif issue_type == 'component_optimization':
            insights = [
                'Performance optimization opportunity.',
                'Component rendering inefficiency detected.',
            ]
            fixes = [
                'Memoize components with React.memo.',
                'Use useMemo for expensive computations.',
                'Implement useCallback for stable references.',
                'Profile component with React DevTools Profiler.',
            ]
            possible_actions = [
                'Analyze rendering performance.',
                'Identify unnecessary re-renders.',
                'Implement code splitting.',
            ]
            alternatives = [
                'Use concurrent rendering features.',
                'Implement lazy loading.',
            ]
        else:
            insights = [
                'Frontend review recommended for the current content category.',
                f'Focus on {context.content_category or 'the detected'} frontend concerns.',
            ]
            fixes = [
                'Review the rendered UI structure for the detected page type.',
                'Confirm that interactive elements obey accessibility norms.',
            ]
            possible_actions = [
                'Inspect the relevant component tree for the current screen.',
                'Validate client-side data flow and event handling.',
            ]

        return {
            'summary': 'Frontend Development Review',
            'insights': insights,
            'possible_actions': possible_actions,
            'fixes': fixes,
            'alternative_solutions': alternatives,
        }

    def _generate_noissue_insights(self, context: RecommendationContext) -> Dict[str, Any]:
        """Frontend insights when no issues detected."""
        category = context.content_category or 'unknown'
        if category == 'source_code':
            possible_actions = [
                'Audit the source file for consistent formatting.',
                'Check for unused imports or dead code.',
                'Validate TypeScript types for the displayed module.',
            ]
            insights = [
                'Source code screenshot appears stable.',
                'Focus on code quality for the targeted file.',
            ]
        elif category == 'error_screen':
            possible_actions = [
                'Map the error screen back to the originating frontend route.',
                'Inspect console logs for the failing component.',
                'Check network requests for failed API calls.',
            ]
            insights = [
                'Error screen indicates a localized frontend failure.',
                'Review the associated route and component state.',
            ]
        elif category == 'dashboard':
            possible_actions = [
                'Confirm data visualizations update correctly on interaction.',
                'Audit chart rendering and responsive layout behavior.',
                'Validate filter and pagination usability.',
            ]
            insights = [
                'Dashboard UI looks consistent.',
                'Ensure performance remains smooth during updates.',
            ]
        else:
            possible_actions = [
                'Run performance profiling.',
                'Review component structure.',
                'Check bundle size.',
                'Audit TypeScript types.',
                'Run linter checks.',
            ]
            insights = [
                'Frontend code appears healthy.',
                'Consider proactive optimizations.',
            ]

        return {
            'summary': 'Frontend code review completed.',
            'insights': insights,
            'possible_actions': possible_actions,
            'fixes': [],
            'alternative_solutions': [],
        }


class BackendDeveloperRecommendationHandler(BaseRecommendationHandler):
    """Generates backend/API-specific recommendations."""

    persona_name = 'backend_developer'

    def _generate_issue_recommendations(self, context: RecommendationContext, issue_type: str) -> Dict[str, Any]:
        """Backend-specific issue handling."""
        insights = []
        fixes = []
        possible_actions = []
        alternatives = []

        if issue_type == 'api_error':
            insights = [
                'API error detected.',
                'HTTP error status code identified.',
            ]
            fixes = [
                'Check server logs for detailed error.',
                'Verify API endpoint path and method.',
                'Check request authentication/authorization.',
                'Inspect request payload and headers.',
            ]
            possible_actions = [
                'Review API documentation.',
                'Test endpoint with curl or Postman.',
                'Check server uptime and health.',
                'Verify database connectivity.',
            ]
            alternatives = [
                'Use API gateway for debugging.',
                'Enable request/response logging.',
            ]
        elif issue_type == 'database_error':
            insights = [
                'Database operation failure detected.',
                'Connection or query issue identified.',
            ]
            fixes = [
                'Check database connection string.',
                'Verify database credentials.',
                'Review SQL query syntax.',
                'Check database schema and indexes.',
            ]
            possible_actions = [
                'Test database connectivity.',
                'Run slow query logs.',
                'Analyze query execution plan.',
                'Check database resource usage.',
            ]
            alternatives = [
                'Use connection pooling.',
                'Implement caching layer.',
                'Optimize indexes.',
            ]
        elif issue_type == 'authentication_error':
            insights = [
                'Authentication/authorization failure.',
                'Access control issue detected.',
            ]
            fixes = [
                'Verify JWT/token validity.',
                'Check CORS configuration.',
                'Review role-based access control.',
                'Inspect authorization headers.',
            ]
            possible_actions = [
                'Debug token generation.',
                'Trace request through middleware.',
                'Verify user permissions.',
            ]
            alternatives = [
                'Implement OAuth 2.0.',
                'Use API key rotation.',
            ]
        elif issue_type == 'server_error':
            insights = [
                'Server-side error detected.',
                'Application crash or exception found.',
            ]
            fixes = [
                'Check application logs.',
                'Review stack trace.',
                'Verify environment configuration.',
                'Check resource limits.',
            ]
            possible_actions = [
                'Enable debug logging.',
                'Monitor server metrics.',
                'Run integration tests.',
            ]
            alternatives = [
                'Implement graceful degradation.',
                'Add circuit breaker pattern.',
            ]
        else:
            insights = ['Backend code review recommended.']
            fixes = ['Review backend code and API design.']
            possible_actions = ['Run integration tests.']

        return {
            'summary': 'Backend Development Review',
            'insights': insights,
            'possible_actions': possible_actions,
            'fixes': fixes,
            'alternative_solutions': alternatives,
        }

    def _generate_noissue_insights(self, context: RecommendationContext) -> Dict[str, Any]:
        """Backend insights when no issues detected."""
        category = context.content_category or 'unknown'
        if category == 'api_documentation':
            possible_actions = [
                'Verify the documented endpoints match implementation.',
                'Check request and response schemas for accuracy.',
                'Ensure authentication flows are documented correctly.',
            ]
            insights = [
                'API documentation appears consistent with backend logic.',
                'Focus on contract accuracy and request validation.',
            ]
        elif category == 'architecture_diagram':
            possible_actions = [
                'Review service boundaries and API responsibilities.',
                'Confirm data flow and deployment topology.',
                'Validate third-party integration points.',
            ]
            insights = [
                'Architecture diagram provides context for backend review.',
                'Check for hidden dependencies and performance bottlenecks.',
            ]
        elif category == 'logs':
            possible_actions = [
                'Correlate log entries with request timestamps.',
                'Identify recurring error patterns.',
                'Validate log level and message detail.',
            ]
            insights = [
                'Logs can reveal operational issues before code changes.',
                'Focus on recurring warning and error patterns.',
            ]
        else:
            possible_actions = [
                'Review API performance.',
                'Audit database queries.',
                'Check server resource usage.',
                'Run security scan.',
                'Review error handling.',
            ]
            insights = [
                'Backend appears healthy.',
                'Consider proactive monitoring.',
            ]

        return {
            'summary': 'Backend code review completed.',
            'insights': insights,
            'possible_actions': possible_actions,
            'fixes': [],
            'alternative_solutions': [],
        }


class QARecommendationHandler(BaseRecommendationHandler):
    """Generates QA/testing-specific recommendations."""

    persona_name = 'qa_engineer'

    def _generate_issue_recommendations(self, context: RecommendationContext, issue_type: str) -> Dict[str, Any]:
        """QA-specific issue handling."""
        insights = []
        fixes = []
        possible_actions = []
        alternatives = []

        if issue_type in ('bug_report', 'failed_test'):
            insights = [
                'Test failure detected.',
                'Reproduction steps needed.',
            ]
            fixes = [
                'Reproduce locally with minimal steps.',
                'Capture detailed error logs.',
                'Create regression test.',
                'Document expected vs actual behavior.',
            ]
            possible_actions = [
                'Run failing test with verbose output.',
                'Inspect stack trace.',
                'Isolate root cause in code.',
                'Create bug report with reproduction steps.',
            ]
            alternatives = [
                'Use test recording tools.',
                'Implement automated regression testing.',
            ]
        elif issue_type == 'validation_issue':
            insights = [
                'Input validation failure.',
                'Edge case scenario detected.',
            ]
            fixes = [
                'Add input boundary tests.',
                'Test with null/undefined values.',
                'Verify error message clarity.',
                'Test with special characters.',
            ]
            possible_actions = [
                'Create test cases for edge cases.',
                'Review validation rules.',
                'Test across browsers/devices.',
            ]
            alternatives = [
                'Implement fuzzing.',
                'Use property-based testing.',
            ]
        else:
            insights = ['Testing review recommended.']
            fixes = ['Review test coverage and strategy.']
            possible_actions = ['Run test suite.']

        return {
            'summary': 'QA & Testing Review',
            'insights': insights,
            'possible_actions': possible_actions,
            'fixes': fixes,
            'alternative_solutions': alternatives,
        }

    def _generate_noissue_insights(self, context: RecommendationContext) -> Dict[str, Any]:
        """QA insights when no issues detected."""
        return {
            'summary': 'QA review completed.',
            'insights': [
                'No obvious test failures detected.',
                'Consider expanding test coverage.',
            ],
            'possible_actions': [
                'Review test coverage metrics.',
                'Identify untested code paths.',
                'Add regression tests.',
                'Test edge cases.',
                'Run cross-browser testing.',
            ],
            'fixes': [],
            'alternative_solutions': [],
        }


class StudentRecommendationHandler(BaseRecommendationHandler):
    """Generates study and learning-specific recommendations."""

    persona_name = 'student'

    def _generate_issue_recommendations(self, context: RecommendationContext, issue_type: str) -> Dict[str, Any]:
        """Student-specific issue handling."""
        insights = [
            'Learning material identified.',
            'Study opportunity detected.',
        ]
        fixes = [
            'Extract key concepts from screenshot.',
            'Create flashcards for important terms.',
            'Write summary of main ideas.',
        ]
        possible_actions = [
            'Highlight key concepts.',
            'Create study notes.',
            'Generate quiz questions.',
            'Form study group discussion points.',
        ]
        alternatives = [
            'Create mind map.',
            'Record explanation video.',
        ]

        return {
            'summary': 'Learning & Study Material Review',
            'insights': insights,
            'possible_actions': possible_actions,
            'fixes': fixes,
            'alternative_solutions': alternatives,
        }

    def _generate_noissue_insights(self, context: RecommendationContext) -> Dict[str, Any]:
        """Student insights when no issues detected."""
        return {
            'summary': 'Study material review completed.',
            'insights': [
                'Educational material identified.',
                'Learning opportunity available.',
            ],
            'possible_actions': [
                'Extract main concepts.',
                'Create study guide.',
                'Generate practice questions.',
                'Prepare for discussion.',
                'Review related topics.',
            ],
            'fixes': [],
            'alternative_solutions': [],
        }


class DataAnalystRecommendationHandler(BaseRecommendationHandler):
    """Generates analytics and data-specific recommendations."""

    persona_name = 'analyst'

    def _generate_issue_recommendations(self, context: RecommendationContext, issue_type: str) -> Dict[str, Any]:
        """Analyst-specific issue handling."""
        insights = []
        fixes = []
        possible_actions = []
        alternatives = []

        if issue_type == 'data_quality_issue':
            insights = [
                'Data quality concern detected.',
                'Missing or anomalous data identified.',
            ]
            fixes = [
                'Investigate source of missing data.',
                'Check for outliers or anomalies.',
                'Verify data collection process.',
                'Review data validation rules.',
            ]
            possible_actions = [
                'Analyze data distribution.',
                'Run data quality checks.',
                'Interview data collectors.',
                'Review data pipeline logs.',
            ]
            alternatives = [
                'Implement automated data validation.',
                'Use outlier detection algorithms.',
            ]
        elif issue_type == 'dashboard_issue':
            insights = [
                'Dashboard metric issue.',
                'Data visualization concern.',
            ]
            fixes = [
                'Verify data source and refresh rate.',
                'Check calculation formulas.',
                'Review dashboard filters.',
                'Validate chart configurations.',
            ]
            possible_actions = [
                'Compare dashboard vs source data.',
                'Check for stale data.',
                'Review calculation logic.',
            ]
            alternatives = [
                'Implement real-time updates.',
                'Add drill-down capabilities.',
            ]
        else:
            insights = ['Analytics review recommended.']
            fixes = ['Review data and metrics.']
            possible_actions = ['Analyze data quality.']

        return {
            'summary': 'Analytics & Data Review',
            'insights': insights,
            'possible_actions': possible_actions,
            'fixes': fixes,
            'alternative_solutions': alternatives,
        }

    def _generate_noissue_insights(self, context: RecommendationContext) -> Dict[str, Any]:
        """Analyst insights when no issues detected."""
        return {
            'summary': 'Analytics review completed.',
            'insights': [
                'Data metrics appear healthy.',
                'Consider deeper analysis.',
            ],
            'possible_actions': [
                'Identify key trends.',
                'Calculate KPIs.',
                'Create trend analysis.',
                'Build predictive models.',
                'Review data anomalies.',
            ],
            'fixes': [],
            'alternative_solutions': [],
        }


class SecurityEngineerRecommendationHandler(BaseRecommendationHandler):
    """Generates security-specific recommendations."""

    persona_name = 'security_engineer'

    def _generate_issue_recommendations(self, context: RecommendationContext, issue_type: str) -> Dict[str, Any]:
        """Security-specific issue handling."""
        insights = [
            'Security concern identified.',
            'Risk assessment needed.',
        ]
        fixes = [
            'Review authentication mechanism.',
            'Check authorization logic.',
            'Scan for known vulnerabilities.',
            'Verify encryption in transit/at rest.',
        ]
        possible_actions = [
            'Run dependency security scan.',
            'Conduct code review for security issues.',
            'Check for hardcoded secrets.',
            'Review access control lists.',
        ]
        alternatives = [
            'Implement security testing in CI/CD.',
            'Use security headers.',
            'Enable audit logging.',
        ]

        return {
            'summary': 'Security Assessment',
            'insights': insights,
            'possible_actions': possible_actions,
            'fixes': fixes,
            'alternative_solutions': alternatives,
        }

    def _generate_noissue_insights(self, context: RecommendationContext) -> Dict[str, Any]:
        """Security insights when no issues detected."""
        return {
            'summary': 'Security review completed.',
            'insights': [
                'No obvious security issues detected.',
                'Continuous security monitoring recommended.',
            ],
            'possible_actions': [
                'Run security audit.',
                'Check for outdated dependencies.',
                'Review access permissions.',
                'Audit error messages.',
                'Check for information leakage.',
            ],
            'fixes': [],
            'alternative_solutions': [],
        }


class GenericRecommendationHandler(BaseRecommendationHandler):
    """Generic recommendation handler for unknown personas."""

    persona_name = 'generic'

    def _generate_issue_recommendations(self, context: RecommendationContext, issue_type: str) -> Dict[str, Any]:
        """Generic issue handling."""
        category = context.content_category or 'unknown'
        possible_actions = [
            'Review the screenshot with the detected content category in mind.',
            'Map the issue to the most relevant workflow for the content type.',
        ]
        if category != 'unknown':
            possible_actions.append(f'Apply recommendations for {category.replace("_", " ")}.')

        return {
            'summary': f'Issue detected: {issue_type}',
            'insights': [
                f'An issue has been detected in the {category} context.',
                'Use the detected content category to narrow the remediation.',
            ],
            'possible_actions': possible_actions,
            'fixes': [
                'Further investigation required.',
            ],
            'alternative_solutions': [],
        }

    def _generate_noissue_insights(self, context: RecommendationContext) -> Dict[str, Any]:
        """Generic insights when no issues detected."""
        return {
            'summary': 'Screenshot analysis completed.',
            'insights': [
                'No obvious issues detected.',
            ],
            'possible_actions': [
                'Review screenshot for context.',
                'Consult specialized reviewer if needed.',
            ],
            'fixes': [],
            'alternative_solutions': [],
        }
