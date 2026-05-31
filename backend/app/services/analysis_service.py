from app.router.model_router import ModelRouter
from app.schemas import ScreenshotAnalyzeRequest, ScreenshotAnalyzeResponse
from app.ocr.ocr_service import OCRService
from app.persona.persona_engine import PersonaEngine
from typing import Dict


class AnalysisService:
    @staticmethod
    async def run_analysis(payload: ScreenshotAnalyzeRequest, router: ModelRouter) -> ScreenshotAnalyzeResponse:
        # Run OCR first
        ocr_result: Dict = OCRService.extract_from_base64(payload.image_base64, preprocess=True)

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
            provider_result = await router.execute_with_fallback(
                'analyze_image',
                raw_bytes,
                meta=ocr_result,
                required_capability='analyze_image',
                intent=(payload.meta or {}).get('intent'),
                persona=payload.persona,
            )

        intent_info = await router.execute_with_fallback(
            'classify_intent',
            ocr_result.get('extracted_text', ''),
            meta=ocr_result,
            required_capability='classify_intent',
            intent=(payload.meta or {}).get('intent'),
            persona=payload.persona,
        )

        persona_engine = PersonaEngine.from_settings()
        persona_analysis = persona_engine.classify_persona(
            ocr_result=ocr_result,
            provider_result=provider_result,
            intent_info=intent_info,
            historical_meta=payload.meta or {},
            request_persona=payload.persona,
        )
        final_persona = persona_analysis['persona']

        results = {
            'message': 'Analysis pipeline (OCR + provider) executed.',
            'ocr': ocr_result,
            'provider': provider_result,
            'intent_info': intent_info,
            'persona_analysis': persona_analysis,
            'meta': payload.meta,
        }

        return ScreenshotAnalyzeResponse(
            analysis_id='analysis-' + (payload.source or 'unknown'),
            intent=intent_info.get('result', {}).get('intent', 'unknown') if isinstance(intent_info, dict) else 'unknown',
            persona=final_persona,
            results=results,
        )
