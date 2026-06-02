from app.recommendation.recommendation_engine import RecommendationEngine
from app.recommendation.recommendation_models import RecommendationContext


def test_figma_screenshot_no_issue_detected():
    engine = RecommendationEngine.from_settings()
    ctx = RecommendationContext(
        ocr_text='A conceptual UI screen showing a dashboard mockup with color palette and spacing examples.',
        vision_caption='Figma design preview',
        labels=['figma', 'design', 'ui'],
        detected_objects=[{'label': 'wireframe'}, {'label': 'layout'}],
        intent='design',
        persona='designer',
    )

    res = engine.analyze(ctx)
    assert res.issue_detected is False
    assert res.content_type == 'ui_screen'
    assert res.fixes == []
