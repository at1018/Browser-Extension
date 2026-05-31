from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.router.schemas import ProviderHealthStatus, ProviderMetadata, ProviderRegistration


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, ProviderRegistration] = {}

    def register(
        self,
        provider_name: str,
        provider: Optional[Any] = None,
        supported_capabilities: Optional[List[str]] = None,
        priority: int = 0,
        cost_score: float = 0.0,
        latency_score: float = 0.0,
        health_status: ProviderHealthStatus = ProviderHealthStatus.unknown,
    ) -> ProviderRegistration:
        provider_name = provider_name.lower()
        metadata = ProviderMetadata(
            provider_name=provider_name,
            supported_capabilities=supported_capabilities or [],
            priority=priority,
            cost_score=cost_score,
            latency_score=latency_score,
            health_status=health_status,
        )
        registration = ProviderRegistration(
            provider_name=provider_name,
            provider=provider,
            metadata=metadata,
        )
        self._providers[provider_name] = registration
        return registration

    def get(self, provider_name: str) -> Optional[ProviderRegistration]:
        return self._providers.get(provider_name.lower())

    def list_providers(self) -> List[ProviderRegistration]:
        return list(self._providers.values())

    def get_available_providers(self, required_capability: Optional[str] = None) -> List[ProviderRegistration]:
        providers = [registration for registration in self._providers.values()]
        if required_capability:
            providers = [
                registration
                for registration in providers
                if required_capability in registration.metadata.supported_capabilities
            ]
        return providers

    def update_health(self, provider_name: str, health_status: ProviderHealthStatus) -> None:
        registration = self.get(provider_name)
        if registration is None:
            return
        registration.metadata.health_status = health_status

    def aggregate_health(self) -> Dict[str, Any]:
        results = [registration.metadata for registration in self._providers.values()]
        overall = ProviderHealthStatus.unknown
        if all(metadata.health_status == ProviderHealthStatus.healthy for metadata in results):
            overall = ProviderHealthStatus.healthy
        elif any(metadata.health_status == ProviderHealthStatus.unhealthy for metadata in results):
            overall = ProviderHealthStatus.degraded
        elif any(metadata.health_status == ProviderHealthStatus.degraded for metadata in results):
            overall = ProviderHealthStatus.degraded
        elif results:
            overall = ProviderHealthStatus.unknown

        return {
            'overall_status': overall,
            'provider_statuses': results,
        }
