from app.recommendation.recommendation_engine import RecommendationEngine
from app.recommendation.recommendation_models import RecommendationContext


def test_configuration_screenshot_no_issue_detected():
    engine = RecommendationEngine.from_settings()
    ctx = RecommendationContext(
        ocr_text="""{
  "compilerOptions": {
    "isolatedModules": true
  }
}""",
        vision_caption='TypeScript configuration file',
        labels=['tsconfig', 'configuration'],
        detected_objects=[{'label': 'configuration file'}],
        intent='unknown',
        persona='developer',
    )

    res = engine.analyze(ctx)
    assert res.issue_detected is False
    assert res.content_type == 'configuration'
    assert res.summary.startswith('Configuration content detected')
    assert res.fixes == []
    assert res.root_cause is None
