# OCR API Documentation

POST /api/screenshots/analyze

- Description: Accepts a base64-encoded image and runs the OCR pipeline. Returns structured OCR output in `results.ocr`.

Request JSON

{
  "image_base64": "data:image/png;base64,...",
  "source": "string",
  "persona": "string (optional)",
  "meta": { ... }
}

Response JSON (excerpt)

{
  "analysis_id": "analysis-...",
  "intent": "...",
  "persona": "...",
  "results": {
    "message": "Analysis pipeline (OCR) executed.",
    "ocr": {
      "extracted_text": "...",
      "confidence": 92.5,
      "bounding_boxes": [
        {"text":"Hello","left":10,"top":10,"width":30,"height":10,"confidence":95.0}
      ],
      "metadata": {"engine":"pytesseract","preprocessing":"opencv"}
    },
    "meta": { ... }
  }
}

Errors

- `400` for invalid payloads; `200` with `results.ocr.metadata.error` populated for OCR-specific failures.

Notes

- Tesseract must be installed and available to `pytesseract`.
- Preprocessing uses OpenCV when available; otherwise a Pillow fallback is used.
