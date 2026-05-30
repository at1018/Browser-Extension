# OCR Architecture (Phase 4)

Overview

- Purpose: Extract textual content and layout information from screenshots and images using Tesseract OCR with optional OpenCV preprocessing.
- Scope: Tesseract OCR, OCR Service, Preprocessing pipeline. No external vision/model SDKs in Phase 4.

Pipeline

1. Screenshot capture (extension) or image upload (API)
2. Image preprocessing (optional OpenCV): grayscale, denoise, contrast, thresholding
3. OCR extraction (Tesseract via `pytesseract`)
4. Structured OCR output returned to caller

Components

- `OCRService` (`backend/app/ocr/ocr_service.py`)
  - `extract_from_base64(data_url, lang='eng', preprocess=True)` — main entrypoint
  - Uses Pillow for I/O; optionally uses OpenCV (`cv2`) for advanced preprocessing
  - Returns structured JSON with `extracted_text`, `confidence`, `bounding_boxes`, `metadata`

- `AnalysisService` (`backend/app/services/analysis_service.py`)
  - Orchestrates OCRService and will later call intent detection and vision providers

Deployment notes

- Requires Tesseract binary installed on host. `pytesseract` is a Python wrapper and expects access to the `tesseract` executable.
- Optional: OpenCV (`opencv-python`) and `numpy` for preprocessing.
- Do not send images to external vision APIs in Phase 4.

Privacy

- Images are sensitive; avoid persisting them unless user consents.
- Metadata does not include raw image bytes by default.

Testing

- Unit tests for `OCRService` are in `backend/tests/test_ocr_service.py`.
- Integration tests for the OCR pipeline are in `backend/tests/test_ocr_pipeline.py`.

"""
