from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.persona.persona_classifier import classify_with_signals
from app.persona.persona_models import PersonaContext, PersonaResult
from app.persona.persona_registry import get_persona_definition


class PersonaEngine:
    def __init__(self, rule_weight: float, llm_weight: float, min_confidence: float):
        self.rule_weight = rule_weight
        self.llm_weight = llm_weight
        self.min_confidence = min_confidence

    @classmethod
    def from_settings(cls) -> 'PersonaEngine':
        return cls(
            rule_weight=settings.PERSONA_RULE_WEIGHT,
            llm_weight=settings.PERSONA_LLM_WEIGHT,
            min_confidence=settings.PERSONA_MIN_CONFIDENCE,
        )

    def _normalize_objects(self, objects: List[Any]) -> List[Dict[str, Any]]:
        normalized = []
        for obj in objects or []:
            if isinstance(obj, dict):
                normalized.append({
                    'label': obj.get('label') or obj.get('name') or str(obj),
                    'box_2d': obj.get('box_2d', []),
                })
            elif isinstance(obj, str):
                normalized.append({'label': obj, 'box_2d': []})
            elif hasattr(obj, 'label'):
                normalized.append({'label': getattr(obj, 'label', ''), 'box_2d': getattr(obj, 'box_2d', [])})
            else:
                normalized.append({'label': str(obj), 'box_2d': []})
        return normalized

    def create_context(
        self,
        ocr_result: Dict[str, Any],
        provider_result: Dict[str, Any],
        intent_info: Dict[str, Any],
        historical_meta: Optional[Dict[str, Any]] = None,
    ) -> PersonaContext:
        ocr_text = ocr_result.get('extracted_text', '') or ''
        caption = provider_result.get('result', {}).get('caption') if provider_result else ''
        labels = provider_result.get('result', {}).get('labels', []) if provider_result else []
        objects = self._normalize_objects(provider_result.get('result', {}).get('objects', []) if provider_result else [])
        provider_reasoning = provider_result.get('result', {}).get('reasoning', '') if provider_result else ''
        intent = intent_info.get('result', {}).get('intent') if intent_info else ''

        return PersonaContext(
            ocr_text=ocr_text,
            caption=caption,
            labels=labels,
            objects=objects,
            intent=intent,
            provider_reasoning=provider_reasoning,
            ocr_confidence=float(ocr_result.get('confidence', 0.0) if ocr_result else 0.0),
            provider_success=bool(provider_result and provider_result.get('result')),
            historical_meta=historical_meta or {},
        )

    def classify_persona(
        self,
        ocr_result: Dict[str, Any],
        provider_result: Dict[str, Any],
        intent_info: Dict[str, Any],
        historical_meta: Optional[Dict[str, Any]] = None,
        request_persona: Optional[str] = None,
    ) -> Dict[str, Any]:
        context = self.create_context(ocr_result, provider_result, intent_info, historical_meta)
        result: PersonaResult = classify_with_signals(
            context,
            rule_weight=self.rule_weight,
            llm_weight=self.llm_weight,
        )

        fallback_persona = request_persona or 'unknown'
        final_persona = fallback_persona
        decision = 'fallback_to_request_persona'
        if result.confidence >= self.min_confidence and result.persona != 'unknown':
            final_persona = result.persona
            decision = 'selected_by_confidence'

        definition = get_persona_definition(final_persona)
        metadata = result.metadata.copy() if isinstance(result.metadata, dict) else {}
        metadata.update({
            'threshold': self.min_confidence,
            'decision': decision,
            'resolved_persona': final_persona,
        })

        return {
            'persona': final_persona,
            'confidence': result.confidence,
            'reasoning': result.reasoning,
            'traits': definition.traits,
            'signals': [signal.dict() for signal in result.signals],
            'metadata': metadata,
            'source': 'persona_engine',
        }
