from __future__ import annotations

from typing import Any, Dict
from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract base class for vision / model providers."""

    @abstractmethod
    async def analyze_image(self, image_bytes: bytes, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    async def generate_response(self, prompt: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    async def classify_intent(self, text: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        raise NotImplementedError()

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        raise NotImplementedError()
"""Provider abstraction interface for AI models."""

from abc import ABC, abstractmethod

class BaseProvider(ABC):
    @abstractmethod
    def analyze_image(self, image_data: bytes, metadata: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def generate_response(self, prompt: str, context: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def classify_intent(self, content: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def health_check(self) -> dict:
        raise NotImplementedError
