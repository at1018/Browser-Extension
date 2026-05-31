import base64
import io
import json
import logging
import os
from typing import Any, Dict, Optional

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None  # type: ignore[assignment]
    BotoCoreError = Exception
    ClientError = Exception

from app.providers.base_provider import BaseProvider

logger = logging.getLogger(__name__)


class BedrockProvider(BaseProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = 'amazon.titan-3',
        region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        super().__init__('bedrock', ['analyze_image', 'generate_response', 'classify_intent'])
        self.api_key = api_key or os.environ.get('BEDROCK_API_KEY')
        self.region = region or os.environ.get('BEDROCK_REGION')
        self.aws_access_key_id = aws_access_key_id or os.environ.get('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = aws_secret_access_key or os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.model = model
        self.client = None
        if boto3 is not None and self.region:
            try:
                self.client = boto3.client(
                    'bedrock',
                    region_name=self.region,
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                )
            except Exception as exc:
                logger.warning('Bedrock client initialization failed: %s', exc)

    def _require_client(self) -> None:
        if boto3 is None or self.client is None:
            raise RuntimeError('BedrockProvider requires boto3 and AWS region to be configured')

    def _decode_body(self, body: Any) -> str:
        if isinstance(body, bytes):
            return body.decode('utf-8', errors='ignore')
        if hasattr(body, 'read'):
            return body.read().decode('utf-8', errors='ignore')
        return str(body)

    def _build_prompt(self, text: str) -> str:
        return (
            'Analyze the screenshot text and generate JSON with keys: caption, labels, objects, text, suggested_actions, reasoning. '
            f'Text: {text}'
        )

    def _invoke(self, prompt: str) -> str:
        self._require_client()
        try:
            response = self.client.invoke_model(
                modelId=self.model,
                contentType='application/json',
                accept='application/json',
                body=json.dumps({'inputText': prompt}).encode('utf-8'),
            )
            body = response.get('body')
            return self._decode_body(body)
        except (BotoCoreError, ClientError, Exception) as exc:
            logger.warning('Bedrock invoke_model failed: %s', exc)
            raise

    async def analyze_image(self, image_bytes: bytes, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError('BedrockProvider is not configured')

        extracted_text = meta.get('extracted_text') if meta else ''
        prompt = self._build_prompt(extracted_text)
        try:
            result = await self._run_in_executor(self._invoke, prompt)
            return {'provider': 'bedrock', 'model': self.model, 'analysis': result}
        except Exception as exc:
            logger.warning('BedrockProvider analyze_image failed: %s', exc)
            raise RuntimeError('BedrockProvider analyze_image failed') from exc

    async def generate_response(self, prompt: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError('BedrockProvider is not configured')

        full_prompt = prompt
        if meta:
            full_prompt += f'\n\nContext: {json.dumps(meta)}'
        try:
            result = await self._run_in_executor(self._invoke, full_prompt)
            return {'provider': 'bedrock', 'result': result, 'model': self.model}
        except Exception as exc:
            logger.warning('BedrockProvider generate_response failed: %s', exc)
            raise RuntimeError('BedrockProvider generate_response failed') from exc

    async def classify_intent(self, text: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError('BedrockProvider is not configured')

        prompt = (
            'Classify the following text into one of: error_bug, product, ui_design, question_text, code, chart_graph, unknown. '
            'Return JSON with keys: intent, confidence, reasoning, suggested_actions.'
            f'\n\nText: {text}'
        )
        if meta:
            prompt += f'\n\nMeta: {json.dumps(meta)}'
        try:
            result = await self._run_in_executor(self._invoke, prompt)
            return {'provider': 'bedrock', 'model': self.model, 'classification': result}
        except Exception as exc:
            logger.warning('BedrockProvider classify_intent failed: %s', exc)
            raise RuntimeError('BedrockProvider classify_intent failed') from exc

    async def health_check(self) -> Dict[str, Any]:
        if not self.client:
            return {'ok': False, 'provider': 'bedrock', 'error': 'missing_boto3_or_region'}

        try:
            models = self.client.list_models()
            return {'ok': True, 'provider': 'bedrock', 'model': self.model, 'model_count': len(models.get('modelSummaries', []))}
        except Exception as exc:
            logger.warning('BedrockProvider health_check failed: %s', exc)
            return {'ok': False, 'provider': 'bedrock', 'error': str(exc)}

    async def _run_in_executor(self, fn, *args, **kwargs) -> Any:
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, fn, *args, **kwargs)
