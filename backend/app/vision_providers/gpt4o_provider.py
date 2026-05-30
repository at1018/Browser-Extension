"""GPT-4o Vision provider stub."""

from typing import Dict, Any

class GPT4OVisionProvider:
    @staticmethod
    def analyze_image(image_bytes: bytes, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        # Placeholder: in production this would call GPT-4o Vision API
        return {
            'provider': 'gpt4o',
            'description': 'vision analysis not implemented',
            'objects': [],
            'labels': [],
            'meta': meta or {},
        }

    @staticmethod
    def health_check() -> Dict[str, Any]:
        return {'ok': True}
