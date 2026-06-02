from app.router.model_router import ModelRouter
from app.schemas import ScreenshotAnalyzeRequest, ScreenshotAnalyzeResponse
from app.ocr.ocr_service import OCRService
from app.persona.persona_engine import PersonaEngine
from typing import Dict
from app.recommendation.recommendation_engine import RecommendationEngine
from app.recommendation.recommendation_intent_fallback import fallback_intent
from app.recommendation.recommendation_content_classifier import classify_content_type
from app.recommendation.recommendation_models import RecommendationContext


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

        intent_value = None
        intent_confidence = 0.0
        if isinstance(intent_info, dict):
            result_data = intent_info.get('result', {})
            intent_value = result_data.get('intent')
            intent_confidence = float(result_data.get('confidence', 0.0) or 0.0)

        rec_context_for_intent = RecommendationContext(
            ocr_text=ocr_result.get('extracted_text', ''),
            vision_caption=provider_result.get('result', {}).get('caption') if isinstance(provider_result, dict) else None,
            labels=provider_result.get('result', {}).get('labels', []) if isinstance(provider_result, dict) else [],
            detected_objects=provider_result.get('result', {}).get('objects', []) if isinstance(provider_result, dict) else [],
            intent=intent_value,
            persona=payload.persona,
            provider_reasoning=provider_result.get('result', {}).get('reasoning') if isinstance(provider_result, dict) else None,
            historical_meta=payload.meta or {},
        )

        if not intent_value or intent_value == 'unknown' or intent_confidence < 0.5:
            intent_value = fallback_intent(rec_context_for_intent)
            intent_info = {'result': {'intent': intent_value, 'confidence': intent_confidence}}

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

        # Run recommendation engine using collected signals
        rec_engine = RecommendationEngine.from_settings()
        
        # Classify content type for false-positive prevention
        temp_context = RecommendationContext(
            ocr_text=ocr_result.get('extracted_text', ''),
            vision_caption=provider_result.get('result', {}).get('caption') if isinstance(provider_result, dict) else None,
            labels=provider_result.get('result', {}).get('labels', []) if isinstance(provider_result, dict) else [],
            persona=final_persona,
        )
        content_type_result = classify_content_type(temp_context)
        content_type = content_type_result.get('content_type', 'unknown')
        
        rec_context = RecommendationContext(
            ocr_text=ocr_result.get('extracted_text', ''),
            vision_caption=provider_result.get('result', {}).get('caption') if isinstance(provider_result, dict) else None,
            labels=provider_result.get('result', {}).get('labels', []) if isinstance(provider_result, dict) else [],
            detected_objects=provider_result.get('result', {}).get('objects', []) if isinstance(provider_result, dict) else [],
            intent=intent_info.get('result', {}).get('intent') if isinstance(intent_info, dict) else None,
            persona=final_persona,
            provider_reasoning=provider_result.get('result', {}).get('reasoning') if isinstance(provider_result, dict) else None,
            ocr_confidence=float(ocr_result.get('confidence', 0.0)),
            provider_success=bool(provider_result.get('result') if isinstance(provider_result, dict) else False),
            content_type=content_type,
            historical_meta=payload.meta or {},
        )

        recommendation = rec_engine.analyze(rec_context)
        results['recommendation'] = recommendation.dict()

        return ScreenshotAnalyzeResponse(
            analysis_id='analysis-' + (payload.source or 'unknown'),
            intent=intent_info.get('result', {}).get('intent', 'unknown') if isinstance(intent_info, dict) else 'unknown',
            persona=final_persona,
            results=results,
        )
