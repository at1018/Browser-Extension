import asyncio
import json
import pytest
from unittest.mock import MagicMock, patch

from app.providers.gemini_provider import GeminiProvider


def run_async(coro):
    return asyncio.run(coro)


def test_gemini_provider_mock_health_and_analyze():
    prov = GeminiProvider(api_key=None)
    h = run_async(prov.health_check())
    assert h.get('provider') == 'gemini'
    assert h.get('ok') is False

    res = run_async(prov.analyze_image(b'fakebytes', meta={'extracted_text': 'hello'}))
    assert res.get('provider') == 'gemini'
    assert 'text' in res


def test_gemini_provider_generate_response_mocked():
    pytest.importorskip('google.generativeai')

    prov = GeminiProvider(api_key='test-key', model='test-model')
    mock_response = MagicMock()
    mock_response.text = 'Hello world'

    with patch('app.providers.gemini_provider.genai.GenerativeModel.generate_content', return_value=mock_response):
        res = run_async(prov.generate_response('Hello prompt', meta={'source': 'test'}))
        assert res['provider'] == 'gemini'
        assert 'Hello world' in res['result']
        assert res['model'] == 'test-model'


def test_gemini_provider_analyze_image_mocked():
    pytest.importorskip('google.generativeai')

    prov = GeminiProvider(api_key='test-key', model='test-model')
    json_output = json.dumps({
        'caption': 'Mocked caption',
        'labels': ['test'],
        'objects': [],
        'text': {'full_text': 'hello', 'blocks': []},
        'suggested_actions': ['inspect'],
        'reasoning': 'mocked',
    })
    mock_response = MagicMock()
    mock_response.text = json_output

    with patch('app.providers.gemini_provider.genai.GenerativeModel.generate_content', return_value=mock_response) as mocked:
        res = run_async(prov.analyze_image(b'fakebytes', meta={'extracted_text': 'hello'}))
        assert res['caption'] == 'Mocked caption'
        assert res['labels'] == ['test']
        assert res['provider'] == 'gemini'

        # Ensure generate_content was called with a contents list containing an inline blob
        assert mocked.called
        call_args = mocked.call_args[0]
        assert len(call_args) >= 1
        contents = call_args[0]
        assert isinstance(contents, list)
        content_item = contents[0]
        assert 'parts' in content_item
        parts = content_item['parts']
        inline_parts = [p for p in parts if isinstance(p, dict) and 'inline_data' in p]
        assert inline_parts, 'no inline_data part found in contents parts'
        inline = inline_parts[0]['inline_data']
        assert inline['data'] == b'fakebytes'


def test_gemini_provider_classify_intent_mocked():
    pytest.importorskip('google.generativeai')

    prov = GeminiProvider(api_key='test-key', model='test-model')
    mock_response = MagicMock()
    mock_response.text = json.dumps({
        'intent': 'code',
        'confidence': 0.88,
        'reasoning': 'mocked',
        'suggested_actions': ['review code'],
    })

    with patch('app.providers.gemini_provider.genai.GenerativeModel.generate_content', return_value=mock_response):
        res = run_async(prov.classify_intent('def foo(): pass', meta={'source': 'unit'}))
        assert res['intent'] == 'code'
        assert res['confidence'] == 0.88
        assert res['suggested_actions'] == ['review code']


def test_gemini_provider_health_check_mocked():
    pytest.importorskip('google.generativeai')

    prov = GeminiProvider(api_key='test-key', model='test-model')
    mock_response = MagicMock()
    mock_response.text = 'Hello'

    with patch('app.providers.gemini_provider.genai.GenerativeModel.generate_content', return_value=mock_response):
        res = run_async(prov.health_check())
        assert res['ok'] is True
        assert res['provider'] == 'gemini'
