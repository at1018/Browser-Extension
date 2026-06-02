from app.recommendation.root_cause_engine import infer_root_cause


def test_infer_root_cause_for_tsconfig():
    class C: pass
    c = C()
    c.ocr_text = 'tsconfig.json contains isolatedModules and compilerOptions'
    c.provider_reasoning = ''
    root = infer_root_cause('typescript_error', c)
    assert 'tsconfig' in root['primary_root_cause'] or root['confidence'] > 0
