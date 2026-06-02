from app.recommendation.recommendation_engine import RecommendationEngine
from app.recommendation.recommendation_models import RecommendationContext


def test_recommendation_engine_detects_typescript_error():
    engine = RecommendationEngine.from_settings()
    ctx = RecommendationContext(
        ocr_text='tsconfig.json error: compilerOptions incompatible with target',
        vision_caption='Editor showing tsconfig',
        labels=['typescript', 'tsconfig'],
        detected_objects=[{'label': 'editor'}],
        intent='coding',
        persona='developer',
    )
    res = engine.analyze(ctx)
    assert res.issue_detected is True
    assert res.issue_type == 'typescript_error'
    assert 0.45 <= res.confidence <= 0.95
    assert isinstance(res.fixes, list)


def test_recommendation_engine_handles_designer_issue():
    engine = RecommendationEngine.from_settings()
    ctx = RecommendationContext(
        ocr_text='spacing and margin look off, uneven padding',
        vision_caption='UI mockup',
        labels=['mockup', 'figma'],
        detected_objects=[{'label': 'wireframe'}],
        intent='design',
        persona='designer',
    )
    res = engine.analyze(ctx)
    assert res.issue_detected is False
    assert res.content_type == 'ui_screen'
    assert res.root_cause is None
    assert res.severity is None
    assert res.fixes == []
