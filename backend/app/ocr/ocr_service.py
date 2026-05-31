import base64
import importlib.util
import io
import logging
import os
from typing import Dict, Any, List, Tuple, Optional

from PIL import Image, UnidentifiedImageError, ImageOps

try:
    import pytesseract
    from pytesseract import Output
    TESSERACT_AVAILABLE = True
except Exception:
    pytesseract = None  # type: ignore[assignment]
    Output = None  # type: ignore[assignment]
    TESSERACT_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except Exception:
    cv2 = None  # type: ignore[assignment]
    np = None  # type: ignore[assignment]
    CV2_AVAILABLE = False

from app.core.config import settings

logger = logging.getLogger(__name__)


def _decode_data_url(data_url: str) -> bytes:
    if data_url.startswith('data:'):
        try:
            header, encoded = data_url.split(',', 1)
            return base64.b64decode(encoded)
        except Exception:
            return base64.b64decode(data_url)
    return base64.b64decode(data_url)


class OCRService:
    """Service to run OCR using Tesseract with optional OpenCV preprocessing.

    Public methods:
    - `extract_from_base64(data_url, preprocess=True)` -> structured result
    - `diagnose()` -> environment diagnostics
    """

    @staticmethod
    def _preprocess_pil(img: Image.Image, use_cv: bool = True) -> Image.Image:
        img = ImageOps.grayscale(img)

        if use_cv and CV2_AVAILABLE and np is not None:
            arr = np.array(img)
            arr = cv2.fastNlMeansDenoising(arr, None, h=10)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            arr = clahe.apply(arr)
            arr = cv2.adaptiveThreshold(arr, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            return Image.fromarray(arr)

        return ImageOps.autocontrast(img)

    @staticmethod
    def _get_tesseract_cmd() -> Optional[str]:
        if TESSERACT_AVAILABLE and pytesseract is not None:
            try:
                return getattr(pytesseract.pytesseract, 'tesseract_cmd', None)
            except Exception:
                return None
        return os.environ.get('TESSERACT_CMD')

    @staticmethod
    def _configure_tesseract() -> None:
        if TESSERACT_AVAILABLE and pytesseract is not None and settings.tesseract_cmd:
            try:
                pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd
            except Exception:
                logger.exception('Failed to configure pytesseract.tesseract_cmd')

    @staticmethod
    def _probe_tesseract_version() -> Optional[str]:
        if not TESSERACT_AVAILABLE or pytesseract is None:
            return None
        try:
            return str(pytesseract.get_tesseract_version())
        except Exception as exc:
            logger.warning('Unable to probe Tesseract version: %s', exc)
            return None

    @staticmethod
    def _extract_with_tesseract(img: Image.Image, lang: str = 'eng') -> Tuple[str, List[Dict[str, Any]]]:
        if not TESSERACT_AVAILABLE or pytesseract is None or Output is None:
            raise RuntimeError('pytesseract or Tesseract not available')

        OCRService._configure_tesseract()
        text = pytesseract.image_to_string(img, lang=lang)
        data = pytesseract.image_to_data(img, output_type=Output.DICT)

        boxes: List[Dict[str, Any]] = []
        n = len(data.get('text', []))
        for i in range(n):
            txt = data['text'][i]
            if not txt or not txt.strip():
                continue
            conf_raw = data.get('conf', [])[i]
            try:
                conf = float(conf_raw)
            except Exception:
                try:
                    conf = float(conf_raw) if conf_raw else -1.0
                except Exception:
                    conf = -1.0

            boxes.append(
                {
                    'text': txt,
                    'left': int(data.get('left', [0])[i]),
                    'top': int(data.get('top', [0])[i]),
                    'width': int(data.get('width', [0])[i]),
                    'height': int(data.get('height', [0])[i]),
                    'confidence': conf,
                }
            )

        return text, boxes

    @classmethod
    def diagnose(cls) -> Dict[str, Any]:
        return {
            'pytesseract_installed': importlib.util.find_spec('pytesseract') is not None,
            'tesseract_cmd': cls._get_tesseract_cmd(),
            'tesseract_available': cls._probe_tesseract_version() is not None,
            'tesseract_version': cls._probe_tesseract_version(),
            'pillow_installed': importlib.util.find_spec('PIL') is not None,
            'opencv_installed': importlib.util.find_spec('cv2') is not None,
            'configured_tesseract_cmd': settings.tesseract_cmd,
        }

    @classmethod
    def extract_from_base64(cls, data_url: str, lang: str = 'eng', preprocess: bool = True) -> Dict[str, Any]:
        try:
            raw = _decode_data_url(data_url)
            img = Image.open(io.BytesIO(raw)).convert('RGB')
        except UnidentifiedImageError:
            logger.exception('Unable to parse image for OCR')
            return {'extracted_text': '', 'confidence': 0.0, 'bounding_boxes': [], 'metadata': {'error': 'unreadable_image'}}
        except Exception:
            logger.exception('Error decoding image base64')
            return {'extracted_text': '', 'confidence': 0.0, 'bounding_boxes': [], 'metadata': {'error': 'decode_error'}}

        if preprocess:
            try:
                img = cls._preprocess_pil(img, use_cv=CV2_AVAILABLE)
            except Exception:
                logger.exception('Preprocessing failed; continuing with original image')

        if not TESSERACT_AVAILABLE or pytesseract is None:
            logger.warning('pytesseract not available; returning placeholder result')
            return {
                'extracted_text': '',
                'confidence': 0.0,
                'bounding_boxes': [],
                'metadata': {
                    'note': 'pytesseract missing',
                    'tesseract_cmd': cls._get_tesseract_cmd(),
                },
            }

        try:
            text, boxes = cls._extract_with_tesseract(img, lang=lang)
            confs = [b.get('confidence', -1.0) for b in boxes if b.get('confidence', -1.0) >= 0]
            avg_conf = float(sum(confs) / len(confs)) if confs else 0.0

            return {
                'extracted_text': text,
                'confidence': round(avg_conf, 2),
                'bounding_boxes': boxes,
                'metadata': {
                    'engine': 'pytesseract',
                    'preprocessing': 'opencv' if CV2_AVAILABLE else 'pillow',
                    'box_count': len(boxes),
                    'tesseract_cmd': cls._get_tesseract_cmd(),
                    'tesseract_version': cls._probe_tesseract_version(),
                },
            }
        except Exception as exc:
            logger.exception('OCR execution failed')
            metadata = {
                'error': 'ocr_failed',
                'tesseract_cmd': cls._get_tesseract_cmd(),
                'tesseract_version': cls._probe_tesseract_version(),
                'exception': str(exc),
            }
            if hasattr(exc, 'message'):
                metadata['exception_message'] = getattr(exc, 'message')
            return {
                'extracted_text': '',
                'confidence': 0.0,
                'bounding_boxes': [],
                'metadata': metadata,
            }


def analyze_image_base64(data_url: str, lang: str = 'eng', preprocess: bool = True) -> Dict[str, Any]:
    """Compatibility wrapper for older tests: analyze image from a data URL base64.

    Delegates to `OCRService.extract_from_base64` and adds legacy keys `text` and `blocks`.
    """
    result = OCRService.extract_from_base64(data_url, lang=lang, preprocess=preprocess)
    # Add legacy fields expected by older tests
    result.setdefault('extracted_text', result.get('extracted_text', ''))
    result.setdefault('bounding_boxes', result.get('bounding_boxes', []))
    # legacy names
    result['text'] = result.get('extracted_text', '')
    result['blocks'] = result.get('bounding_boxes', [])
    return result
