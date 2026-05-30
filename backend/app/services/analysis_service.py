from app.schemas import ScreenshotAnalyzeRequest, ScreenshotAnalyzeResponse
from app.ocr.ocr_service import OCRService
from typing import Dict
from app.providers.base_provider import BaseProvider


class AnalysisService:
    @staticmethod
    async def run_analysis(payload: ScreenshotAnalyzeRequest, provider: BaseProvider) -> ScreenshotAnalyzeResponse:
        # Run OCR first
        ocr_result: Dict = OCRService.extract_from_base64(payload.image_base64, preprocess=True)

        # Prepare image bytes for provider; decode base64
        data_url = payload.image_base64
        raw_bytes = None
        try:
            if data_url.startswith('data:'):
                _, encoded = data_url.split(',', 1)
                import base64 as _b64

                raw_bytes = _b64.b64decode(encoded)
            else:
                import base64 as _b64

                raw_bytes = _b64.b64decode(data_url)
        except Exception:
            raw_bytes = None

        provider_result = {}
        if raw_bytes is not None:
            provider_result = await provider.analyze_image(raw_bytes, meta=ocr_result)

        # Let Gemini classify intent using the provider implementation.
        intent_info = await provider.classify_intent(
            ocr_result.get('extracted_text', ''),
            meta=ocr_result,
        )

        results = {
            'message': 'Analysis pipeline (OCR + provider) executed.',
            'ocr': ocr_result,
            'provider': provider_result,
            'intent_info': intent_info,
            'meta': payload.meta,
        }

        return ScreenshotAnalyzeResponse(
            analysis_id='analysis-' + (payload.source or 'unknown'),
            intent=intent_info.get('intent', 'unknown'),
            persona=payload.persona or 'unknown',
            results=results,
        )
