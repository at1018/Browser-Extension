from app.persona.persona_engine import PersonaEngine


def test_persona_engine_detects_developer_from_tsconfig_and_github():
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': 'The tsconfig file fails to compile the TypeScript project with several imports.'},
        provider_result={
            'result': {
                'caption': 'Developer editing TypeScript configuration',
                'labels': ['typescript', 'tsconfig', 'editor'],
                'objects': ['code editor', 'json file'],
                'reasoning': 'The screenshot shows a developer workflow with a code editor and tsconfig settings.',
            }
        },
        intent_info={'result': {'intent': 'coding'}},
        historical_meta={},
        request_persona='unknown',
    )

    assert analysis['persona'] == 'developer'
    assert analysis['confidence'] > 0.65
    assert analysis['source'] == 'persona_engine'


def test_persona_engine_detects_designer_from_figma_wireframe():
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': 'A Figma artboard with a visual design mockup and component library annotations.'},
        provider_result={
            'result': {
                'caption': 'Designer working on prototype and UI layout',
                'labels': ['figma', 'mockup', 'design system'],
                'objects': ['figma canvas', 'wireframe', 'layout'],
                'reasoning': 'The scene shows a product designer reviewing a UI wireframe in Figma.',
            }
        },
        intent_info={'result': {'intent': 'design'}},
        historical_meta={},
        request_persona='unknown',
    )

    assert analysis['persona'] == 'designer'
    assert analysis['confidence'] > 0.65


def test_persona_engine_detects_qa_from_bug_report():
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': 'Regression test failed with assertion error and bug ticket created in Jira.'},
        provider_result={
            'result': {
                'caption': 'QA reviewing failed test and bug report',
                'labels': ['bug report', 'regression', 'jira'],
                'objects': ['error screenshot', 'jira ticket'],
                'reasoning': 'A quality assurance specialist is verifying a failed test case and bug report.',
            }
        },
        intent_info={'result': {'intent': 'testing'}},
        historical_meta={},
        request_persona='unknown',
    )

    assert analysis['persona'] == 'qa'
    assert analysis['confidence'] > 0.65


def test_persona_engine_detects_analyst_from_dashboard_spreadsheet():
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': 'The dashboard shows conversion metrics, revenue growth and engagement trends in a spreadsheet view.'},
        provider_result={
            'result': {
                'caption': 'Analytics dashboard with KPI chart',
                'labels': ['dashboard', 'analytics', 'kpi'],
                'objects': ['chart', 'spreadsheet', 'report'],
                'reasoning': 'An analyst is reviewing business intelligence metrics and revenue trends.',
            }
        },
        intent_info={'result': {'intent': 'dashboard'}},
        historical_meta={},
        request_persona='unknown',
    )

    assert analysis['persona'] == 'analyst'
    assert analysis['confidence'] > 0.65


def test_persona_engine_detects_student_from_tutorial_notes():
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': 'Study notes for the course include examples, explanations, and exam preparation tips.'},
        provider_result={
            'result': {
                'caption': 'Student studying lecture notes and practice materials',
                'labels': ['lecture', 'notes', 'tutorial'],
                'objects': ['notebook', 'flashcard', 'learning portal'],
                'reasoning': 'The screenshot illustrates a student reviewing educational material and assignment notes.',
            }
        },
        intent_info={'result': {'intent': 'learning'}},
        historical_meta={},
        request_persona='unknown',
    )

    assert analysis['persona'] == 'student'
    assert analysis['confidence'] > 0.65


def test_persona_engine_detects_shopper_from_ecommerce_page():
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': 'Compare prices and read product reviews before adding items to the shopping cart.'},
        provider_result={
            'result': {
                'caption': 'E-commerce product page with checkout and discount offers',
                'labels': ['product', 'price', 'checkout'],
                'objects': ['product card', 'shopping cart', 'coupon banner'],
                'reasoning': 'A shopper is browsing product listings and comparing prices on an online marketplace.',
            }
        },
        intent_info={'result': {'intent': 'buying'}},
        historical_meta={},
        request_persona='unknown',
    )

    assert analysis['persona'] == 'shopper'
    assert analysis['confidence'] > 0.65


def test_persona_engine_preserves_request_persona_on_weak_signal():
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': 'Some generic unrelated page with no strong role signals.'},
        provider_result={
            'result': {
                'caption': 'A generic screen with no clear focus',
                'labels': ['generic', 'screen'],
                'objects': [],
                'reasoning': 'The screenshot was ambiguous and did not match a strong persona profile.',
            }
        },
        intent_info={'result': {'intent': 'unknown'}},
        historical_meta={},
        request_persona='student',
    )

    assert analysis['persona'] == 'student'
    assert analysis['confidence'] == 0.0
