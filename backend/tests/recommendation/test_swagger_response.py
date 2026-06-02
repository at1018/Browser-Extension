from app.recommendation.recommendation_engine import RecommendationEngine
from app.recommendation.recommendation_models import RecommendationContext


def test_swagger_response_no_issue_detected():
    engine = RecommendationEngine.from_settings()
    ctx = RecommendationContext(
        ocr_text='GET /api/v1/users HTTP/1.1\nHost: example.com\nResponse: 200 OK\nContent-Type: application/json',
        vision_caption='Swagger API response documentation',
        labels=['swagger', 'api', 'documentation'],
        detected_objects=[{'label': 'api docs'}],
        intent='unknown',
        persona='analyst',
    )

    res = engine.analyze(ctx)
    assert res.issue_detected is False
    assert res.content_type == 'bug_report'
    assert res.fixes == []
