import json
import logging
import os
import re
from typing import Any, Dict, Optional

import httpx

from app.providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(BaseProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'claude-3.5',
        base_url: Optional[str] = None,
    ):
        super().__init__('claude', ['analyze_image', 'generate_response', 'classify_intent'])
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        self.model = model
        self.base_url = base_url or os.environ.get('ANTHROPIC_BASE_URL', 'https://api.anthropic.com')

    def _headers(self) -> Dict[str, str]:
        return {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key or '',
        }

    def _strip_json(self, text: str) -> str:
        text = text.strip()
        text = re.sub(r'^```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```$', '', text).strip()
        return text

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('ClaudeProvider API key missing')

        url = f'{self.base_url}{path}'
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    async def _complete(self, prompt: str) -> str:
        payload = {
            'model': self.model,
            'prompt': prompt,
            'max_tokens_to_sample': 300,
            'temperature': 0.2,
        }
        response = await self._post('/v1/complete', payload)
        return response.get('completion', '')

    async def analyze_image(self, image_bytes: bytes, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('ClaudeProvider is not configured')

        extracted_text = meta.get('extracted_text') if meta else ''
        prompt = (
            'Analyze the screenshot and return only JSON with keys: caption, labels, objects, text, suggested_actions, reasoning. '
            'The text field should contain full_text and blocks. Use the provided OCR text when available.'
            f'\n\nOCR_TEXT: {extracted_text}'
        )
        try:
            output = await self._complete(prompt)
            cleaned = self._strip_json(output)
            parsed = json.loads(cleaned)
            parsed.setdefault('provider', 'claude')
            parsed.setdefault('model', self.model)
            return parsed
        except Exception as exc:
            logger.warning('ClaudeProvider analyze_image failed: %s', exc)
            raise RuntimeError('ClaudeProvider analyze_image failed') from exc

    async def generate_response(self, prompt: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('ClaudeProvider is not configured')

        full_prompt = prompt
        if meta:
            full_prompt += f'\n\nContext: {json.dumps(meta)}'
        try:
            output = await self._complete(full_prompt)
            return {'provider': 'claude', 'result': output, 'model': self.model}
        except Exception as exc:
            logger.warning('ClaudeProvider generate_response failed: %s', exc)
            raise RuntimeError('ClaudeProvider generate_response failed') from exc

    async def classify_intent(self, text: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('ClaudeProvider is not configured')

        prompt = (
            'Classify the following text into one of: error_bug, product, ui_design, question_text, code, chart_graph, unknown. '
            'Return only valid JSON with keys: intent, confidence, reasoning, suggested_actions.'
            f'\n\nText: {text}'
        )
        if meta:
            prompt += f'\n\nMeta: {json.dumps(meta)}'
        try:
            output = await self._complete(prompt)
            cleaned = self._strip_json(output)
            parsed = json.loads(cleaned)
            parsed.setdefault('intent', 'unknown')
            parsed.setdefault('confidence', 0.0)
            parsed.setdefault('reasoning', '')
            parsed.setdefault('suggested_actions', [])
            return parsed
        except Exception as exc:
            logger.warning('ClaudeProvider classify_intent failed: %s', exc)
            raise RuntimeError('ClaudeProvider classify_intent failed') from exc

    async def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {'ok': False, 'provider': 'claude', 'error': 'missing_api_key'}

        try:
            greeting = await self._complete('Say hello in one short sentence.')
            return {'ok': True, 'provider': 'claude', 'model': self.model, 'probe_output': greeting}
        except Exception as exc:
            logger.warning('ClaudeProvider health_check failed: %s', exc)
            return {'ok': False, 'provider': 'claude', 'error': str(exc)}
