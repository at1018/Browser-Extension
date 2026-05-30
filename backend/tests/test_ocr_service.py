import base64
import io
import pytest

# Skip entire module if Pillow is not installed
pytest.importorskip('PIL')
from PIL import Image

from app.ocr.ocr_service import OCRService


def make_text_image(text: str = 'Hello 123'):
    img = Image.new('RGB', (200, 60), color=(255, 255, 255))
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


def test_ocrservice_extract_runs():
    pytest.importorskip('pytesseract')
    pytest.importorskip('PIL')

    img_b64 = make_text_image('Test OCR')
    res = OCRService.extract_from_base64(img_b64, preprocess=False)
    assert isinstance(res, dict)
    assert 'extracted_text' in res
    assert 'confidence' in res
    assert 'bounding_boxes' in res


def test_ocrservice_with_preprocessing():
    pytest.importorskip('pytesseract')
    pytest.importorskip('PIL')
    # cv2 is optional
    img_b64 = make_text_image('Preprocess Test')
    res = OCRService.extract_from_base64(img_b64, preprocess=True)
    assert isinstance(res, dict)
    assert 'extracted_text' in res
