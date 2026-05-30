"""Claude Vision provider stub."""

from typing import Dict, Any

class ClaudeVisionProvider:
    @staticmethod
    def analyze_image(image_bytes: bytes, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {
            'provider': 'claude',
            'description': 'vision analysis stub',
            'objects': [],
            'labels': [],
            'meta': meta or {},
        }

    @staticmethod
    def health_check() -> Dict[str, Any]:
        return {'ok': True}
