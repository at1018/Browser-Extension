import base64
import io
import logging
from typing import Dict, Any, List, Tuple, Optional

from PIL import Image, UnidentifiedImageError, ImageOps

try:
    import pytesseract
    from pytesseract import Output
    TESSERACT_AVAILABLE = True
except Exception:
    TESSERACT_AVAILABLE = False

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except Exception:
    CV2_AVAILABLE = False

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
    """

    @staticmethod
    def _preprocess_pil(img: Image.Image, use_cv: bool = True) -> Image.Image:
        # Convert to grayscale
        img = ImageOps.grayscale(img)

        if use_cv and CV2_AVAILABLE:
            # Convert to OpenCV image
            arr = np.array(img)
            # Noise reduction
            arr = cv2.fastNlMeansDenoising(arr, None, h=10)
            # Contrast enhancement via CLAHE
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            arr = clahe.apply(arr)
            # Adaptive thresholding
            arr = cv2.adaptiveThreshold(arr, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                        cv2.THRESH_BINARY, 11, 2)
            return Image.fromarray(arr)

        # Fallback simple enhancements with Pillow
        img = ImageOps.autocontrast(img)
        return img

    @staticmethod
    def _extract_with_tesseract(img: Image.Image, lang: str = 'eng') -> Tuple[str, List[Dict[str, Any]]]:
        if not TESSERACT_AVAILABLE:
            raise RuntimeError('pytesseract or Tesseract not available')

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

            box = {
                'text': txt,
                'left': int(data.get('left', [0])[i]),
                'top': int(data.get('top', [0])[i]),
                'width': int(data.get('width', [0])[i]),
                'height': int(data.get('height', [0])[i]),
                'confidence': conf,
            }
            boxes.append(box)

        return text, boxes

    @classmethod
    def extract_from_base64(cls, data_url: str, lang: str = 'eng', preprocess: bool = True) -> Dict[str, Any]:
        """Full OCR pipeline entrypoint.

        Steps:
        - decode base64
        - open image
        - optional preprocessing (OpenCV/Pillow)
        - run Tesseract OCR
        - compute overall confidence and return structured output
        """
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

        if not TESSERACT_AVAILABLE:
            logger.warning('pytesseract not available; returning placeholder result')
            return {
                'extracted_text': '',
                'confidence': 0.0,
                'bounding_boxes': [],
                'metadata': {'note': 'pytesseract missing'},
            }

        try:
            text, boxes = cls._extract_with_tesseract(img, lang=lang)
            # Compute average confidence across boxes that have non-negative confidence
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
                },
            }
        except Exception:
            logger.exception('OCR execution failed')
            return {'extracted_text': '', 'confidence': 0.0, 'bounding_boxes': [], 'metadata': {'error': 'ocr_failed'}}
