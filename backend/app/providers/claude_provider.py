import os
from typing import Any, Dict
from app.providers.base_provider import BaseProvider


class ClaudeProvider(BaseProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.environ.get('CLAUDE_API_KEY')

    async def analyze_image(self, image_bytes: bytes, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {'provider': 'claude', 'note': 'not_implemented'}

    async def generate_response(self, prompt: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {'provider': 'claude', 'note': 'not_implemented'}

    async def classify_intent(self, text: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {'intent': 'unknown', 'confidence': 0.0}

    async def health_check(self) -> Dict[str, Any]:
        return {'ok': False, 'provider': 'claude', 'note': 'not_implemented'}
"""Claude provider adapter stub."""

from .base_provider import BaseProvider

class ClaudeProvider(BaseProvider):
    def analyze_image(self, image_data: bytes, metadata: dict) -> dict:
        pass

    def generate_response(self, prompt: str, context: dict) -> dict:
        pass

    def classify_intent(self, content: dict) -> dict:
        pass

    def health_check(self) -> dict:
        pass
