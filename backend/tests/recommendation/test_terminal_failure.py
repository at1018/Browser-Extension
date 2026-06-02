from app.recommendation.recommendation_engine import RecommendationEngine
from app.recommendation.recommendation_models import RecommendationContext


def test_terminal_failure_detects_issue():
    engine = RecommendationEngine.from_settings()
    ctx = RecommendationContext(
        ocr_text='npm ERR! code ELIFECYCLE\nnpm ERR! errno 1\nFailed at the build script.',
        vision_caption='Terminal build failure output',
        labels=['terminal', 'build', 'error'],
        detected_objects=[{'label': 'terminal'}],
        intent='unknown',
        persona='developer',
    )

    res = engine.analyze(ctx)
    assert res.issue_detected is True
    assert res.content_type == 'terminal_output'
    assert res.issue_type == 'build_error'
    assert res.fixes != []
