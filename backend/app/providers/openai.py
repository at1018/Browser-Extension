import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from app.providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'gpt-4.1-mini',
        base_url: Optional[str] = None,
    ):
        super().__init__('openai', ['analyze_image', 'generate_response', 'classify_intent'])
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        self.model = model
        self.base_url = base_url or os.environ.get('OPENAI_BASE_URL', 'https://api.openai.com')

    def _headers(self) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {self.api_key or ""}',
            'Content-Type': 'application/json',
        }

    async def _request(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('OpenAIProvider API key missing')

        url = f'{self.base_url}{path}'
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    async def _generate_text(self, prompt: str) -> str:
        payload = {
            'model': self.model,
            'input': prompt,
            'max_output_tokens': 300,
            'temperature': 0.2,
        }
        response = await self._request('/v1/responses', payload)
        output = response.get('output', [])
        if isinstance(output, list) and output:
            first = output[0]
            if isinstance(first, dict):
                return first.get('content', '') or ''.join(part.get('text', '') for part in first.get('content', []) if isinstance(part, dict))
        return str(response)

    async def analyze_image(self, image_bytes: bytes, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('OpenAIProvider is not configured')

        extracted_text = meta.get('extracted_text') if meta else ''
        prompt = (
            'Analyze the provided screenshot OCR text and return JSON with keys: caption, labels, objects, text, suggested_actions, reasoning. '
            'The text field should contain full_text and blocks. Use OCR text as the primary source.'
            f'\n\nOCR_TEXT: {extracted_text}'
        )
        try:
            output = await self._generate_text(prompt)
            return {
                'provider': 'openai',
                'model': self.model,
                'analysis': output,
            }
        except Exception as exc:
            logger.warning('OpenAIProvider analyze_image failed: %s', exc)
            raise RuntimeError('OpenAIProvider analyze_image failed') from exc

    async def generate_response(self, prompt: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('OpenAIProvider is not configured')

        combined_prompt = prompt
        if meta:
            combined_prompt += f'\n\nContext: {json.dumps(meta)}'
        try:
            output = await self._generate_text(combined_prompt)
            return {'provider': 'openai', 'result': output, 'model': self.model}
        except Exception as exc:
            logger.warning('OpenAIProvider generate_response failed: %s', exc)
            raise RuntimeError('OpenAIProvider generate_response failed') from exc

    async def classify_intent(self, text: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.api_key:
            raise RuntimeError('OpenAIProvider is not configured')

        prompt = (
            'Classify the following text into one of: error_bug, product, ui_design, question_text, code, chart_graph, unknown. '
            'Return only JSON with keys: intent, confidence, reasoning, suggested_actions.'
            f'\n\nText: {text}'
        )
        if meta:
            prompt += f'\n\nMeta: {json.dumps(meta)}'
        try:
            output = await self._generate_text(prompt)
            return {'provider': 'openai', 'model': self.model, 'classification': output}
        except Exception as exc:
            logger.warning('OpenAIProvider classify_intent failed: %s', exc)
            raise RuntimeError('OpenAIProvider classify_intent failed') from exc

    async def health_check(self) -> Dict[str, Any]:
        if not self.api_key:
            return {'ok': False, 'provider': 'openai', 'error': 'missing_api_key'}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f'{self.base_url}/v1/models', headers=self._headers())
                response.raise_for_status()
                return {'ok': True, 'provider': 'openai', 'model': self.model}
        except Exception as exc:
            logger.warning('OpenAIProvider health_check failed: %s', exc)
            return {'ok': False, 'provider': 'openai', 'error': str(exc)}
