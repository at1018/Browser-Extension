from app.recommendation.severity_engine import assess_severity


def test_assess_severity_typescript_build():
    class C:
        ocr_text = 'build failed during CI in production'
        provider_reasoning = ''

    c = C()
    sev = assess_severity('build_error', c, 0.9)
    assert sev in ('critical', 'high', 'medium')
