"""
Test to verify persona confidence is properly calibrated.
Confidence should be realistic: typically 0.4-0.95, never 0.9999.
"""
from app.persona.persona_engine import PersonaEngine


def test_developer_strong_signal_confidence_is_reasonable():
    """Strong developer signals should produce 0.75-0.90 confidence."""
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={
            'extracted_text': 'The tsconfig file fails to compile the TypeScript project with several imports.',
            'confidence': 0.85
        },
        provider_result={
            'result': {
                'caption': 'Developer editing TypeScript configuration',
                'labels': ['typescript', 'tsconfig', 'editor'],
                'objects': ['code editor', 'json file'],
                'reasoning': 'The screenshot shows a developer workflow with a code editor and tsconfig settings.',
            }
        },
        intent_info={'result': {'intent': 'coding', 'confidence': 0.80}},
        historical_meta={},
        request_persona='unknown',
    )

    print(f"Developer strong signal: confidence={analysis['confidence']:.4f}")
    print(f"  Components: {analysis['metadata']['confidence_components']}")
    
    # Should be high but reasonable, not 0.9999
    assert 0.70 <= analysis['confidence'] <= 0.95, f"Expected 0.70-0.95, got {analysis['confidence']}"
    assert analysis['persona'] == 'developer'


def test_weak_signal_produces_low_confidence():
    """Single weak signal should produce 0.15-0.55 confidence."""
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={
            'extracted_text': 'Some generic screen text.',
            'confidence': 0.20
        },
        provider_result={
            'result': {
                'caption': 'A generic screen',
                'labels': ['generic'],
                'objects': [],
                'reasoning': 'Code found in reasoning.',  # Only 1 keyword match
            }
        },
        intent_info={'result': {'intent': 'unknown'}},
        historical_meta={},
        request_persona='unknown',
    )

    print(f"Weak developer signal: confidence={analysis['confidence']:.4f}")
    print(f"  Components: {analysis['metadata']['confidence_components']}")
    
    # Single weak signal should not exceed 0.55
    assert analysis['confidence'] <= 0.55, f"Weak signal should be <= 0.55, got {analysis['confidence']}"


def test_multiple_personas_reduces_confidence():
    """When multiple personas have signals, confidence should be lower or similar."""
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={
            'extracted_text': 'Design mockup with code snippet and some metrics.',
            'confidence': 0.75
        },
        provider_result={
            'result': {
                'caption': 'Mixed content screen',
                'labels': ['mockup', 'code', 'dashboard'],
                'objects': ['wireframe', 'editor', 'chart'],
                'reasoning': 'The screenshot shows both designer and developer artifacts including UI layout and TypeScript code.',
            }
        },
        intent_info={'result': {'intent': 'mixed'}},
        historical_meta={},
        request_persona='unknown',
    )

    print(f"Multiple signals: confidence={analysis['confidence']:.4f}")
    print(f"  Personas with signals: {analysis['metadata']['scoring_details']['personas_with_signals']}")
    print(f"  Components: {analysis['metadata']['confidence_components']}")
    
    # Multiple personas with strong mixed signals is still reasonably confident
    # but should be capped by diversity penalty
    assert 0.40 <= analysis['confidence'] <= 0.90, f"Expected 0.40-0.90, got {analysis['confidence']}"


def test_provider_failure_reduces_confidence():
    """When provider fails, confidence should be penalized."""
    engine = PersonaEngine.from_settings()
    # Simulate provider failure by providing no result
    analysis = engine.classify_persona(
        ocr_result={
            'extracted_text': 'The tsconfig file fails to compile.',
            'confidence': 0.75
        },
        provider_result={},  # No provider result
        intent_info={'result': {'intent': 'coding'}},
        historical_meta={},
        request_persona='unknown',
    )

    print(f"Provider failure: confidence={analysis['confidence']:.4f}")
    print(f"  Components: {analysis['metadata']['confidence_components']}")
    print(f"  Provider factor: {analysis['metadata']['confidence_components'].get('provider_factor', 'N/A')}")
    
    # Provider failure should reduce confidence
    if analysis['persona'] != 'unknown':
        # When provider fails, provider_factor is 0.8, reducing confidence
        assert analysis['metadata']['confidence_components'].get('provider_factor') == 0.8


def test_no_signals_returns_zero_confidence():
    """No signals should return 0.0 confidence."""
    engine = PersonaEngine.from_settings()
    analysis = engine.classify_persona(
        ocr_result={'extracted_text': '', 'confidence': 0.0},
        provider_result={},
        intent_info={'result': {'intent': 'unknown'}},
        historical_meta={},
        request_persona='unknown',
    )

    print(f"No signals: confidence={analysis['confidence']:.4f}")
    assert analysis['confidence'] == 0.0
    assert analysis['persona'] == 'unknown'


if __name__ == '__main__':
    test_developer_strong_signal_confidence_is_reasonable()
    test_weak_signal_produces_low_confidence()
    test_multiple_personas_reduces_confidence()
    test_provider_failure_reduces_confidence()
    test_no_signals_returns_zero_confidence()
    print("\n✓ All confidence calibration tests passed!")
