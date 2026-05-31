import asyncio
import base64
import functools
import json
import logging
import os
import re
from typing import Any, Dict, Optional

from app.providers.base_provider import BaseProvider

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    genai = None  # type: ignore[assignment]
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class GeminiProvider(BaseProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: int = 30,
        retry_attempts: int = 2,
        retry_backoff: float = 1.0,
    ):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.model = model or os.environ.get('GEMINI_MODEL', 'gemini-2.5-flash')
        self.timeout_seconds = timeout_seconds
        self.retry_attempts = retry_attempts
        self.retry_backoff = retry_backoff
        super().__init__('gemini', ['analyze_image', 'generate_response', 'classify_intent'])

        if self.api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
            except Exception as exc:
                logger.warning('Gemini configuration failed: %s', exc)

    @staticmethod
    def _build_data_url(image_bytes: bytes) -> str:
        encoded = base64.b64encode(image_bytes).decode('ascii')
        return f'data:image/png;base64,{encoded}'

    @staticmethod
    def _strip_json_markers(text: str) -> str:
        text = text.strip()
        text = re.sub(r'^```json\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'```$', '', text).strip()
        return text

    @staticmethod
    def _parse_json_response(text: str) -> Dict[str, Any]:
        cleaned = GeminiProvider._strip_json_markers(text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(f'Unable to parse JSON response: {exc}; response="{cleaned[:200]}"')

    @staticmethod
    def _get_response_text(response: Any) -> str:
        if response is None:
            return ''
        if hasattr(response, 'text'):
            return getattr(response, 'text') or ''
        if hasattr(response, 'output_text'):
            return getattr(response, 'output_text') or ''
        if hasattr(response, 'output'):
            output = getattr(response, 'output')
            if isinstance(output, str):
                return output
            texts = []
            for item in output:
                content = getattr(item, 'content', None)
                if content is None:
                    continue
                if isinstance(content, list):
                    for part in content:
                        texts.append(getattr(part, 'text', str(part)))
                else:
                    texts.append(str(content))
            return ' '.join(texts)
        return str(response)

    @staticmethod
    def _is_rate_limit_error(exc: Exception) -> bool:
        message = str(exc).lower()
        if 'rate limit' in message or 'rate_limit' in message or '429' in message or 'quota' in message:
            return True
        status_code = getattr(exc, 'status_code', None)
        return status_code == 429

    async def _run_sync(self, fn, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, functools.partial(fn, *args, **kwargs))

    async def _execute_with_retry(self, fn, *args, **kwargs):
        last_error: Optional[Exception] = None
        for attempt in range(self.retry_attempts + 1):
            try:
                coro = self._run_sync(fn, *args, **kwargs)
                if self.timeout_seconds:
                    return await asyncio.wait_for(coro, timeout=self.timeout_seconds)
                return await coro
            except asyncio.TimeoutError as exc:
                last_error = exc
                logger.warning('GeminiProvider timeout on attempt %s/%s', attempt + 1, self.retry_attempts + 1)
                if attempt == self.retry_attempts:
                    raise
            except Exception as exc:
                last_error = exc
                if self._is_rate_limit_error(exc) and attempt < self.retry_attempts:
                    delay = self.retry_backoff * (2 ** attempt)
                    logger.warning('GeminiProvider rate limit detected; retrying after %.1fs', delay)
                    await asyncio.sleep(delay)
                    continue
                raise
        raise last_error or RuntimeError('GeminiProvider failed without exception')

    def _prepare_input(self, prompt: str, image_data_url: Optional[str] = None) -> Any:
        # For Gemini SDK we construct parts compatible with genai.types
        # When provided with raw image bytes (or a data URL), create an inline blob dict
        if image_data_url:
            # Accept raw bytes or data URL strings
            if isinstance(image_data_url, (bytes, bytearray)):
                image_bytes = bytes(image_data_url)
            elif isinstance(image_data_url, str) and image_data_url.startswith('data:'):
                try:
                    _, encoded = image_data_url.split(',', 1)
                    import base64 as _b64

                    image_bytes = _b64.b64decode(encoded)
                except Exception:
                    image_bytes = image_data_url.encode('utf-8')
            else:
                image_bytes = image_data_url

            # Try to guess mime type from header bytes
            mime = 'application/octet-stream'
            try:
                if isinstance(image_bytes, (bytes, bytearray)):
                    if image_bytes[:4].startswith(b'\x89PNG'):
                        mime = 'image/png'
                    elif image_bytes[:3] == b"\xff\xd8\xff":
                        mime = 'image/jpeg'
            except Exception:
                pass

            # Construct a content dict using 'parts' where inline_data is a blob dict
            return [
                {
                    'parts': [
                        {'inline_data': {'mime_type': mime, 'data': image_bytes}},
                        {'text': prompt},
                    ]
                }
            ]
        return prompt

    def _build_model(self) -> Any:
        if not GENAI_AVAILABLE:
            raise RuntimeError('google.generativeai SDK is not installed')
        return genai.GenerativeModel(self.model)

    def _generate_sync(self, prompt: str, image_bytes: Optional[bytes] = None) -> Any:
        model = self._build_model()
        contents = self._prepare_input(prompt, image_bytes)
        return model.generate_content(
            contents,
            generation_config={'temperature': 0.2},
        )

    async def analyze_image(self, image_bytes: bytes, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.api_key or not GENAI_AVAILABLE:
            return {
                'provider': 'gemini',
                'model': self.model,
                'caption': 'Gemini provider not available',
                'labels': [],
                'objects': [],
                'text': {
                    'full_text': meta.get('extracted_text') if meta else '',
                    'blocks': meta.get('bounding_boxes') if meta else [],
                },
                'suggested_actions': [],
                'reasoning': 'gemini_sdk_missing_or_api_key_missing',
                'raw': {},
            }

        prompt = (
            'Analyze the screenshot. Return only valid JSON with keys: caption, labels, objects, text, suggested_actions, reasoning. '
            'The text key should contain full_text and blocks, and labels should be a short list of detected concepts.'
        )

        try:
            # Pass raw bytes directly; _prepare_input will convert to an inline blob dict
            response = await self._execute_with_retry(self._generate_sync, prompt, image_bytes)
            raw_text = self._get_response_text(response)
            parsed = self._parse_json_response(raw_text)
            parsed.setdefault('provider', 'gemini')
            parsed.setdefault('model', self.model)
            parsed.setdefault('raw', {})
            return parsed
        except Exception as exc:
            logger.exception('Gemini analyze_image failed')
            return {
                'provider': 'gemini',
                'model': self.model,
                'error': 'analyze_image_failed',
                'error_message': str(exc),
                'raw_response': self._get_response_text(exc) if isinstance(exc, Exception) else str(exc),
            }

    async def generate_response(self, prompt: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.api_key or not GENAI_AVAILABLE:
            return {'provider': 'gemini', 'result': 'not_implemented', 'prompt': prompt}

        combined_prompt = prompt
        if meta:
            combined_prompt += f"\n\nContext: {json.dumps(meta)}"

        try:
            response = await self._execute_with_retry(self._generate_sync, combined_prompt)
            output = self._get_response_text(response)
            return {'provider': 'gemini', 'result': output, 'model': self.model}
        except Exception as exc:
            logger.exception('Gemini generate_response failed')
            return {'provider': 'gemini', 'error': 'generate_response_failed', 'error_message': str(exc)}

    async def classify_intent(self, text: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.api_key or not GENAI_AVAILABLE:
            return {'intent': 'unknown', 'confidence': 0.0, 'reasoning': 'gemini_sdk_missing_or_api_key_missing'}

        prompt = (
            'Classify the following text into a single category: error_bug, product, ui_design, question_text, code, chart_graph, or unknown. '
            'Return only JSON with keys: intent, confidence, reasoning, suggested_actions.'
            f'\n\nText:\n{text}'
        )

        if meta:
            prompt += f"\n\nMeta: {json.dumps(meta)}"

        try:
            response = await self._execute_with_retry(self._generate_sync, prompt)
            parsed = self._parse_json_response(self._get_response_text(response))
            parsed.setdefault('intent', 'unknown')
            parsed.setdefault('confidence', 0.0)
            parsed.setdefault('reasoning', '')
            parsed.setdefault('suggested_actions', [])
            return parsed
        except Exception as exc:
            logger.exception('Gemini classify_intent failed')
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'reasoning': str(exc),
                'error': 'classify_intent_failed',
            }

    async def health_check(self) -> Dict[str, Any]:
        if not self.api_key or not GENAI_AVAILABLE:
            return {
                'ok': False,
                'provider': 'gemini',
                'model': self.model,
                'error': 'missing_api_key_or_sdk',
            }

        try:
            response = await self._execute_with_retry(self._generate_sync, 'Say hello in one short sentence.')
            text = self._get_response_text(response)
            return {'ok': True, 'provider': 'gemini', 'model': self.model, 'probe_output': text}
        except Exception as exc:
            logger.exception('Gemini health_check failed')
            return {
                'ok': False,
                'provider': 'gemini',
                'model': self.model,
                'error': 'health_check_failed',
                'error_message': str(exc),
            }
