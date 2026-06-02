from app.recommendation.recommendation_registry import register_handler, get_handler


def test_registry_register_and_get():
    def dummy(ctx):
        return {'recommendations': ['do X']}

    register_handler('dummy_issue', dummy)
    h = get_handler('dummy_issue')
    assert h is dummy
