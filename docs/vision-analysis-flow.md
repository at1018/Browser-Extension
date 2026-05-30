# Vision Analysis Flow

Sequence:

1. Screenshot received at `/api/screenshots/analyze`.
2. `AnalysisService` runs OCR via `OCRService`.
3. The configured provider (default: `GeminiProvider`) is invoked with image bytes
   and OCR metadata.
4. Provider returns structured multimodal output.
5. `AnalysisService` runs intent detection and assembles final response.

See `docs/ocr_sequence.md` for the OCR-only sequence diagram.
