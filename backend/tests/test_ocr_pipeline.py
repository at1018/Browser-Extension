import base64
import io
import pytest
from fastapi.testclient import TestClient

# Skip module if Pillow not installed
pytest.importorskip('PIL')
from PIL import Image
from app.main import app


def make_text_image(text: str = 'Integration 1'):
    img = Image.new('RGB', (300, 80), color=(255, 255, 255))
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.text((10, 10), text, fill=(0, 0, 0), font=font)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode('ascii')


def test_analyze_endpoint_returns_structured_ocr():
    pytest.importorskip('pytesseract')
    pytest.importorskip('PIL')

    client = TestClient(app)
    payload = {
        'image_base64': make_text_image('Integration OCR'),
        'source': 'unittest',
        'persona': 'tester',
        'meta': {'case': 'ocr-pipeline'},
    }
    resp = client.post('/api/screenshots/analyze', json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert 'ocr' in data['results']
    o = data['results']['ocr']
    assert 'extracted_text' in o
    assert 'bounding_boxes' in o
