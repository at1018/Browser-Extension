import base64
import io
import pytest

# Skip this test module if Pillow is not available in the environment.
pytest.importorskip('PIL')
from PIL import Image
from fastapi.testclient import TestClient
from app.main import app
from app.ocr.ocr_service import analyze_image_base64


def make_blank_png_base64():
    img = Image.new('RGB', (100, 40), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return 'data:image/png;base64,' + b64


def test_ocr_service_runs():
    data_url = make_blank_png_base64()
    result = analyze_image_base64(data_url)
    assert isinstance(result, dict)
    assert 'text' in result
    assert 'blocks' in result


def test_integration_analyze_endpoint():
    client = TestClient(app)
    payload = {
        'image_base64': make_blank_png_base64(),
        'source': 'unittest',
        'persona': 'developer',
        'meta': {'case': 'ocr-integration'},
    }
    resp = client.post('/api/screenshots/analyze', json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert 'ocr' in data['results']
