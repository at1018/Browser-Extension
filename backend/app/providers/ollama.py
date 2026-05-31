import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

from app.providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'llama2',
        base_url: Optional[str] = None,
    ):
        super().__init__('ollama', ['analyze_image', 'generate_response', 'classify_intent'])
        self.api_key = api_key or os.environ.get('OLLAMA_API_KEY')
        self.model = model
        self.base_url = base_url or os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')

    def _headers(self) -> Dict[str, str]:
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f'{self.base_url.rstrip("/")}{path}'
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()

    async def _generate_text(self, prompt: str) -> str:
        payload = {
            'model': self.model,
            'input': prompt,
            'max_output_tokens': 300,
        }
        response = await self._post('/v1/completions', payload)
        if isinstance(response.get('choices'), list) and response['choices']:
            choice = response['choices'][0]
            return choice.get('message', {}).get('content', '') or str(choice.get('text', ''))
        return json.dumps(response)

    async def analyze_image(self, image_bytes: bytes, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        prompt = 'Analyze the screenshot and return JSON with keys: caption, labels, objects, text, suggested_actions, reasoning.'
        if meta and meta.get('extracted_text'):
            prompt += f"\n\nOCR text: {meta['extracted_text']}"
        try:
            output = await self._generate_text(prompt)
            return {'provider': 'ollama', 'model': self.model, 'analysis': output}
        except Exception as exc:
            logger.warning('OllamaProvider analyze_image failed: %s', exc)
            raise RuntimeError('OllamaProvider analyze_image failed') from exc

    async def generate_response(self, prompt: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        full_prompt = prompt
        if meta:
            full_prompt += f'\n\nContext: {json.dumps(meta)}'
        try:
            output = await self._generate_text(full_prompt)
            return {'provider': 'ollama', 'result': output, 'model': self.model}
        except Exception as exc:
            logger.warning('OllamaProvider generate_response failed: %s', exc)
            raise RuntimeError('OllamaProvider generate_response failed') from exc

    async def classify_intent(self, text: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        prompt = (
            'Classify the following text into one of: error_bug, product, ui_design, question_text, code, chart_graph, unknown. '
            'Return JSON with keys: intent, confidence, reasoning, suggested_actions.'
            f'\n\nText: {text}'
        )
        if meta:
            prompt += f'\n\nMeta: {json.dumps(meta)}'
        try:
            output = await self._generate_text(prompt)
            return {'provider': 'ollama', 'model': self.model, 'classification': output}
        except Exception as exc:
            logger.warning('OllamaProvider classify_intent failed: %s', exc)
            raise RuntimeError('OllamaProvider classify_intent failed') from exc

    async def health_check(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f'{self.base_url.rstrip("/")}/health', headers=self._headers())
                if response.status_code == 200:
                    return {'ok': True, 'provider': 'ollama', 'model': self.model}
                return {'ok': False, 'provider': 'ollama', 'status_code': response.status_code}
        except Exception as exc:
            logger.warning('OllamaProvider health_check failed: %s', exc)
            return {'ok': False, 'provider': 'ollama', 'error': str(exc)}
