from io import BytesIO
import base64
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.schemas import ScreenshotAnalyzeResponse

client = TestClient(app)


def _build_test_image(text: str, format_name: str = 'PNG') -> BytesIO:
    img = Image.new('RGB', (240, 120), color='white')
    img_bytes = BytesIO()
    img.save(img_bytes, format=format_name)
    img_bytes.seek(0)
    return img_bytes


def _make_analysis_response(content_type: str, issue_detected: bool) -> ScreenshotAnalyzeResponse:
    return ScreenshotAnalyzeResponse(
        analysis_id='analysis-test',
        intent='code',
        persona='developer',
        results={
            'recommendation': {
                'content_type': content_type,
                'issue_detected': issue_detected,
            }
        }
    )


@patch('app.services.screenshot_service.ScreenshotService.analyze_screenshot', new_callable=AsyncMock)
def test_analyze_upload_tsconfig_png_returns_configuration(mock_analyze):
    mock_analyze.return_value = _make_analysis_response('configuration', False)

    response = client.post(
        '/api/screenshots/analyze-upload',
        data={'persona': 'developer', 'source': 'tsconfig'},
        files={'image': ('tsconfig.png', _build_test_image('tsconfig', 'PNG'), 'image/png')},
    )

    assert response.status_code == 200
    result = response.json()
    assert result['results']['recommendation']['content_type'] == 'configuration'
    assert result['results']['recommendation']['issue_detected'] is False
    assert mock_analyze.await_count == 1
    payload = mock_analyze.call_args.args[0]
    assert payload.source == 'tsconfig'
    assert payload.persona == 'developer'


def test_analyze_upload_rejects_unsupported_file_type():
    response = client.post(
        '/api/screenshots/analyze-upload',
        data={'persona': 'developer', 'source': 'tsconfig'},
        files={'image': ('tsconfig.txt', BytesIO(b'test'), 'text/plain')},
    )

    assert response.status_code == 400
    assert response.json()['detail'] == 'Unsupported file type'


@patch('app.services.screenshot_service.ScreenshotService.analyze_screenshot', new_callable=AsyncMock)
def test_analyze_upload_python_traceback_png_returns_error_screen(mock_analyze):
    mock_analyze.return_value = _make_analysis_response('error_screen', True)

    response = client.post(
        '/api/screenshots/analyze-upload',
        data={'persona': 'developer', 'source': 'python_traceback'},
        files={'image': ('python_traceback.png', _build_test_image('traceback', 'PNG'), 'image/png')},
    )

    assert response.status_code == 200
    result = response.json()
    assert result['results']['recommendation']['content_type'] == 'error_screen'
    assert result['results']['recommendation']['issue_detected'] is True
    assert mock_analyze.await_count == 1
    payload = mock_analyze.call_args.args[0]
    assert payload.source == 'python_traceback'
    assert payload.persona == 'developer'


@patch('app.services.screenshot_service.ScreenshotService.analyze_screenshot', new_callable=AsyncMock)
def test_analyze_upload_and_base64_return_identical_response_schema(mock_analyze):
    expected_response = _make_analysis_response('configuration', False)
    mock_analyze.return_value = expected_response

    image_file = _build_test_image('tsconfig', 'PNG')
    image_bytes = image_file.getvalue()
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')

    # POST /analyze-upload
    upload_response = client.post(
        '/api/screenshots/analyze-upload',
        data={'persona': 'developer', 'source': 'tsconfig'},
        files={'image': ('tsconfig.png', BytesIO(image_bytes), 'image/png')},
    )

    # POST /analyze with Base64
    base64_payload = {
        'image_base64': image_base64,
        'source': 'tsconfig',
        'persona': 'developer',
        'meta': {},
    }
    base64_response = client.post('/api/screenshots/analyze', json=base64_payload)

    assert upload_response.status_code == base64_response.status_code == 200
    assert upload_response.json() == base64_response.json()
    assert mock_analyze.await_count == 2
