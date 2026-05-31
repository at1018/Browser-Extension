from app.persona.persona_engine import PersonaEngine


def test_persona_engine_detects_developer_from_code_context():
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': 'Fix the code bug in the terminal and update the API request.'},
        provider_result={'result': {'caption': 'A developer reviewing code', 'labels': ['code', 'terminal'], 'objects': ['editor'], 'reasoning': 'This appears to be a developer workflow with code and debug context.'}},
        intent_info={'result': {'intent': 'debugging'}},
        historical_meta={},
        request_persona='unknown',
    )

    assert analysis['persona'] == 'developer'
    assert analysis['confidence'] > 0.5
    assert analysis['source'] == 'persona_engine'


def test_persona_engine_returns_unknown_for_low_confidence():
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': 'A generic screenshot with no strong persona signals.'},
        provider_result={'result': {'caption': 'A screenshot of a generic dashboard', 'labels': ['screenshot', 'dashboard'], 'objects': [], 'reasoning': 'The content is broad and does not clearly match a specific role.'}},
        intent_info={'result': {'intent': 'unknown'}},
        historical_meta={},
        request_persona=None,
    )

    assert analysis['persona'] == 'unknown'
    assert analysis['confidence'] == 0.0


def test_persona_engine_preserves_request_persona_when_confidence_is_low():
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': 'A generic screenshot with no strong persona signals.'},
        provider_result={'result': {'caption': 'A screenshot of a generic dashboard', 'labels': ['screenshot', 'dashboard'], 'objects': [], 'reasoning': 'The content is broad and does not clearly match a specific role.'}},
        intent_info={'result': {'intent': 'unknown'}},
        historical_meta={},
        request_persona='student',
    )

    assert analysis['persona'] == 'student'
    assert analysis['confidence'] == 0.0
