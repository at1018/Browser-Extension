from app.recommendation.recommendation_engine import RecommendationEngine
from app.recommendation.recommendation_models import RecommendationContext


def test_error_screenshot_detects_issue():
    engine = RecommendationEngine.from_settings()
    ctx = RecommendationContext(
        ocr_text="""Traceback (most recent call last):
  File \"app.py\", line 10, in <module>
    main()
TypeError: unsupported operand type(s) for +: 'int' and 'str'""",
        vision_caption='Python traceback error',
        labels=['traceback', 'error'],
        detected_objects=[{'label': 'terminal'}],
        intent='unknown',
        persona='developer',
    )

    res = engine.analyze(ctx)
    assert res.issue_detected is True
    assert res.content_type == 'error_screen'
    assert res.issue_type == 'runtime_error'
    assert res.root_cause is not None
    assert res.severity in ('high', 'medium')
