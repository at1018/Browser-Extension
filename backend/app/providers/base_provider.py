from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List


class BaseProvider(ABC):
    """Abstract base class for vision / model providers."""

    def __init__(self, provider_name: str, supported_capabilities: List[str]) -> None:
        self.provider_name = provider_name.lower()
        self.supported_capabilities = supported_capabilities
        self.success_count = 0
        self.failure_count = 0
        self.total_latency_ms = 0.0
        self.last_health_check: str | None = None

    @property
    def total_requests(self) -> int:
        return self.success_count + self.failure_count

    @property
    def success_rate(self) -> float:
        return float(self.success_count) / self.total_requests if self.total_requests > 0 else 0.0

    @property
    def failure_rate(self) -> float:
        return float(self.failure_count) / self.total_requests if self.total_requests > 0 else 0.0

    @property
    def average_latency_ms(self) -> float:
        return float(self.total_latency_ms) / self.total_requests if self.total_requests > 0 else 0.0

    def _record_operation(self, duration_ms: float, success: bool) -> None:
        self.total_latency_ms += duration_ms
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def _record_health_check(self, success: bool) -> None:
        self.last_health_check = datetime.utcnow().isoformat() + 'Z'
        self._record_operation(0.0, success)

    def get_provider_metadata(self) -> Dict[str, Any]:
        return {
            'provider_name': self.provider_name,
            'supported_capabilities': self.supported_capabilities,
            'success_rate': round(self.success_rate, 3),
            'failure_rate': round(self.failure_rate, 3),
            'average_latency_ms': round(self.average_latency_ms, 2),
            'last_health_check': self.last_health_check,
        }

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
