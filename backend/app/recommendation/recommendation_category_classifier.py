from typing import Dict, List

CATEGORY_KEYWORDS: Dict[str, List[str]] = {
    'login_screen': ['login', 'sign in', 'email', 'password', 'remember me', 'forgot password', 'sign in button'],
    'signup_screen': ['sign up', 'register', 'create account', 'new account', 'join now'],
    'landing_page': ['hero', 'feature section', 'newsletter', 'subscribe', 'get started', 'product overview', 'value proposition'],
    'dashboard': ['dashboard', 'overview', 'analytics', 'metrics', 'kpi', 'reports', 'summary cards', 'chart'],
    'ecommerce_product_page': ['add to cart', 'buy now', 'product details', 'price', 'reviews', 'shipping', 'product description', 'variant'],
    'shopping_cart': ['cart', 'checkout', 'subtotal', 'items', 'remove', 'quantity', 'shopping bag'],
    'checkout_flow': ['checkout', 'payment', 'billing', 'order summary', 'shipping address', 'credit card', 'promo code'],
    'mobile_app_screen': ['tab bar', 'bottom navigation', 'mobile app', 'swipe', 'tap', 'iOS', 'android', 'mobile screen'],
    'design_system': ['design tokens', 'style guide', 'components', 'typography', 'spacing scale', 'color palette', 'component library'],
    'wireframe': ['wireframe', 'low fidelity', 'sketch', 'blocks', 'layout draft', 'placeholder'],
    'prototype': ['prototype', 'interactive', 'preview', 'clickable', 'prototype flow'],
    'source_code': ['function', 'class', 'import', 'def ', 'const ', 'let ', 'var ', 'public ', 'private ', 'return', 'console.log', 'printf', 'package ', 'namespace'],
    'error_screen': ['error', 'exception', 'traceback', 'stack trace', 'fatal', 'null pointer', 'segmentation fault', 'typeerror', 'referenceerror', 'runtime error', 'crash'],
    'ide_screenshot': ['vscode', 'ide', 'editor', 'code editor', 'intellisense', 'terminal', 'debugger', 'workspace', 'extensions'],
    'pull_request': ['pull request', 'merge request', 'review changes', 'approved', 'commented', 'diff'],
    'github_repository': ['github', 'repository', 'repo', 'README', 'issues', 'pull requests', 'stars'],
    'api_documentation': ['api documentation', 'swagger', 'openapi', 'endpoint', 'request body', 'response schema', 'api docs'],
    'architecture_diagram': ['architecture', 'system diagram', 'microservices', 'service mesh', 'component diagram', 'deployment diagram'],
    'bug_report': ['bug report', 'reproduction steps', 'expected', 'actual', 'severity', 'priority', 'jira', 'issue tracker'],
    'test_execution_report': ['test execution', 'passed', 'failed', 'skipped', 'duration', 'test suite', 'run results'],
    'automation_script': ['selenium', 'puppeteer', 'playwright', 'automation script', 'test automation', 'assert', 'webdriver'],
    'test_case': ['test case', 'steps to reproduce', 'preconditions', 'expected result', 'actual result'],
    'jira_ticket': ['jira', 'ticket', 'story', 'epic', 'issue type', 'acceptance criteria'],
    'lecture_notes': ['lecture', 'slide', 'notes', 'class', 'professor', 'seminar'],
    'assignment': ['assignment', 'homework', 'task', 'deadline', 'submission'],
    'research_paper': ['abstract', 'introduction', 'methodology', 'conclusion', 'references', 'citation'],
    'presentation_slides': ['slide', 'presentation', 'speaker notes', 'bullet points', 'agenda', 'title slide'],
    'exam_question': ['question', 'solve', 'answer', 'exam', 'test', 'problem statement'],
    'tutorial': ['tutorial', 'step-by-step', 'walkthrough', 'how to', 'guide'],
    'study_material': ['study material', 'summary', 'review', 'flashcards', 'concepts', 'learning'],
    'kpi_report': ['kpi', 'scorecard', 'performance indicators', 'trend analysis', 'benchmark'],
    'powerbi': ['power bi', 'powerbi', 'report page', 'visualization pane'],
    'tableau': ['tableau', 'dashboard view', 'worksheet', 'story'],
    'excel_sheet': ['excel', 'spreadsheet', 'cell', 'formula', 'pivot table', 'xlsx'],
    'charts': ['chart', 'graph', 'pie chart', 'bar chart', 'line chart', 'axis'],
    'metrics_report': ['metrics report', 'performance report', 'data insights', 'business metrics'],
    'resume': ['resume', 'cv', 'experience', 'skills', 'education', 'summary'],
    'job_description': ['job description', 'requirements', 'responsibilities', 'qualifications'],
    'product_requirement_document': ['product requirement', 'prd', 'requirements document', 'user story', 'acceptance criteria'],
    'meeting_notes': ['meeting notes', 'minutes', 'action items', 'agenda', 'discussion'],
    'business_proposal': ['business proposal', 'pitch', 'proposal', 'executive summary', 'value proposition'],
    'marketing_campaign': ['marketing campaign', 'audience', 'campaign', 'conversion', 'brand'],
    'cicd_pipeline': ['ci/cd', 'pipeline', 'build step', 'deployment', 'stages', 'workflow'],
    'kubernetes': ['kubernetes', 'k8s', 'pod', 'deployment', 'service', 'namespace'],
    'docker': ['docker', 'container', 'dockerfile', 'image', 'compose', 'registry'],
    'cloud_console': ['cloud console', 'azure portal', 'aws console', 'gcp console', 'cloud provider'],
    'monitoring_dashboard': ['monitoring dashboard', 'alerts', 'metrics', 'health check', 'uptime'],
    'logs': ['logs', 'log output', 'stdout', 'stderr', 'error log', 'trace'],
    'document': ['document', 'page', 'section', 'paragraph', 'content'],
    'spreadsheet': ['spreadsheet', 'sheet', 'cell', 'row', 'column', 'formula'],
    'form': ['form', 'input field', 'submit', 'label', 'checkbox', 'radio button'],
    'website': ['website', 'homepage', 'navigation', 'footer', 'header', 'banner'],
}

SOURCE_WEIGHTS: Dict[str, float] = {
    'ocr_text': 1.2,
    'caption': 1.1,
    'labels': 1.0,
    'objects': 0.9,
    'intent': 1.3,
    'provider_reasoning': 1.0,
}


def _match_keywords(text: str, keywords: List[str]) -> int:
    normalized = (text or '').lower()
    return sum(1 for kw in keywords if kw.lower() in normalized)


def classify_content_category(context) -> Dict[str, object]:
    text_sources = {
        'ocr_text': context.ocr_text or '',
        'caption': context.vision_caption or '',
        'labels': ' '.join(context.labels or []),
        'objects': ' '.join([obj.get('label', '') for obj in context.detected_objects or []]),
        'intent': context.intent or '',
        'provider_reasoning': context.provider_reasoning or '',
    }

    scores: Dict[str, float] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0.0
        for source_name, source_text in text_sources.items():
            weight = SOURCE_WEIGHTS.get(source_name, 1.0)
            score += _match_keywords(source_text, keywords) * weight
        scores[category] = score

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]
    total_score = sum(scores.values())
    confidence = 0.0
    if total_score > 0:
        confidence = min(0.95, best_score / total_score)

    if best_score == 0:
        best_category = 'unknown'
        confidence = 0.0

    return {
        'content_category': best_category,
        'confidence': confidence,
        'scores': scores,
    }
