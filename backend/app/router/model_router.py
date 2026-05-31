from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.providers.base_provider import BaseProvider
from app.providers.bedrock import BedrockProvider
from app.providers.claude import ClaudeProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.ollama import OllamaProvider
from app.providers.openai import OpenAIProvider
from app.router.provider_registry import ProviderRegistry
from app.router.routing_strategy import RoutingStrategy
from app.router.schemas import (
    ProviderHealthStatus,
    ProviderMetadata,
    ProviderRegistration,
    ProviderHealthSummary,
    RouterConfig,
    RoutingDecision,
)

logger = logging.getLogger(__name__)

_router_instance: Optional[ModelRouter] = None


class ModelRouter:
    def __init__(
        self,
        registry: ProviderRegistry,
        strategy: RoutingStrategy,
        config: RouterConfig,
    ) -> None:
        self.registry = registry
        self.strategy = strategy
        self.config = config

    @classmethod
    def from_settings(cls) -> ModelRouter:
        config = RouterConfig(
            default_provider=settings.default_provider,
            fallback_chain=settings.router_fallback_chain,
            routing_strategy=settings.router_strategy,
            provider_weights=settings.provider_weights,
        )

        registry = ProviderRegistry()
        registry.register(
            'gemini',
            GeminiProvider(
                api_key=settings.GEMINI_API_KEY,
                model=settings.GEMINI_MODEL,
                timeout_seconds=settings.gemini_timeout_seconds,
                retry_attempts=settings.gemini_retry_attempts,
                retry_backoff=settings.gemini_retry_backoff,
            ),
            supported_capabilities=['analyze_image', 'generate_response', 'classify_intent'],
            priority=10,
            cost_score=20.0,
            latency_score=20.0,
            health_status=ProviderHealthStatus.unknown,
        )
        registry.register(
            'claude',
            ClaudeProvider(api_key=settings.CLAUDE_API_KEY if hasattr(settings, 'CLAUDE_API_KEY') else None),
            supported_capabilities=['analyze_image', 'generate_response', 'classify_intent'],
            priority=9,
            cost_score=30.0,
            latency_score=30.0,
            health_status=ProviderHealthStatus.unknown,
        )
        registry.register(
            'openai',
            OpenAIProvider(api_key=settings.OPENAI_API_KEY if hasattr(settings, 'OPENAI_API_KEY') else None),
            supported_capabilities=['analyze_image', 'generate_response', 'classify_intent'],
            priority=8,
            cost_score=35.0,
            latency_score=40.0,
            health_status=ProviderHealthStatus.unknown,
        )
        registry.register(
            'bedrock',
            BedrockProvider(
                api_key=settings.BEDROCK_API_KEY if hasattr(settings, 'BEDROCK_API_KEY') else None,
                region=settings.BEDROCK_REGION if hasattr(settings, 'BEDROCK_REGION') else None,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID if hasattr(settings, 'AWS_ACCESS_KEY_ID') else None,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY if hasattr(settings, 'AWS_SECRET_ACCESS_KEY') else None,
            ),
            supported_capabilities=['analyze_image', 'generate_response', 'classify_intent'],
            priority=7,
            cost_score=45.0,
            latency_score=35.0,
            health_status=ProviderHealthStatus.unknown,
        )
        registry.register(
            'ollama',
            OllamaProvider(
                api_key=settings.OLLAMA_API_KEY if hasattr(settings, 'OLLAMA_API_KEY') else None,
                base_url=settings.OLLAMA_BASE_URL if hasattr(settings, 'OLLAMA_BASE_URL') else None,
            ),
            supported_capabilities=['analyze_image', 'generate_response', 'classify_intent'],
            priority=6,
            cost_score=30.0,
            latency_score=20.0,
            health_status=ProviderHealthStatus.unknown,
        )

        return cls(registry, RoutingStrategy(config), config)

    async def refresh_health(self) -> ProviderHealthSummary:
        for registration in self.registry.list_providers():
            provider = registration.provider
            if provider is None:
                self.registry.update_health(registration.provider_name, ProviderHealthStatus.unhealthy)
                continue
            try:
                health = await provider.health_check()
                status = ProviderHealthStatus.healthy if health.get('ok', False) else ProviderHealthStatus.unhealthy
                self.registry.update_health(registration.provider_name, status)
                if isinstance(provider, BaseProvider):
                    provider._record_health_check(status == ProviderHealthStatus.healthy)
                    registration.metadata.success_rate = provider.success_rate
                    registration.metadata.failure_rate = provider.failure_rate
                    registration.metadata.average_latency_ms = provider.average_latency_ms
                    registration.metadata.last_health_check = provider.last_health_check
            except Exception as exc:
                logger.warning('Health check failed for %s: %s', registration.provider_name, exc)
                self.registry.update_health(registration.provider_name, ProviderHealthStatus.unhealthy)
                if isinstance(provider, BaseProvider):
                    provider._record_health_check(False)
                    registration.metadata.success_rate = provider.success_rate
                    registration.metadata.failure_rate = provider.failure_rate
                    registration.metadata.average_latency_ms = provider.average_latency_ms
                    registration.metadata.last_health_check = provider.last_health_check
        summary = self.registry.aggregate_health()
        return ProviderHealthSummary(
            overall_status=summary['overall_status'],
            provider_statuses=summary['provider_statuses'],
        )

    def select_provider(
        self,
        required_capability: str,
        intent: Optional[str] = None,
        persona: Optional[str] = None,
    ) -> RoutingDecision:
        available = self.registry.get_available_providers(required_capability)
        metadata_list = [registration.metadata for registration in available]
        return self.strategy.select_provider(metadata_list, required_capability, intent, persona)

    async def execute_with_fallback(
        self,
        method_name: str,
        *args: Any,
        required_capability: str,
        intent: Optional[str] = None,
        persona: Optional[str] = None,
        **kwargs: Any,
    ) -> Any:
        decision = self.select_provider(required_capability, intent, persona)
        fallback = [name for name in decision.fallback_chain if self.registry.get(name)]

        tried: List[str] = []
        last_exception: Optional[Exception] = None
        for provider_name in fallback:
            registration = self.registry.get(provider_name)
            if registration is None or registration.provider is None:
                continue
            if required_capability not in registration.metadata.supported_capabilities:
                continue
            if registration.metadata.health_status == ProviderHealthStatus.unhealthy:
                logger.info('Skipping unhealthy provider %s for %s', provider_name, method_name)
                continue

            tried.append(provider_name)
            provider = registration.provider
            start_time = time.perf_counter()
            try:
                provider_method = getattr(provider, method_name)
                result = await provider_method(*args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                if isinstance(provider, BaseProvider):
                    provider._record_operation(elapsed_ms, True)
                    registration.metadata.success_rate = provider.success_rate
                    registration.metadata.failure_rate = provider.failure_rate
                    registration.metadata.average_latency_ms = provider.average_latency_ms
                    registration.metadata.last_health_check = provider.last_health_check
                return {
                    'provider': provider_name,
                    'result': result,
                    'routing_decision': decision.model_dump(),
                }
            except Exception as exc:
                elapsed_ms = (time.perf_counter() - start_time) * 1000.0
                if isinstance(provider, BaseProvider):
                    provider._record_operation(elapsed_ms, False)
                    registration.metadata.success_rate = provider.success_rate
                    registration.metadata.failure_rate = provider.failure_rate
                    registration.metadata.average_latency_ms = provider.average_latency_ms
                    registration.metadata.last_health_check = provider.last_health_check

                logger.warning('Provider %s failed during %s: %s', provider_name, method_name, exc)
                self.registry.update_health(provider_name, ProviderHealthStatus.unhealthy)
                last_exception = exc
                continue

        raise RuntimeError(
            'No available providers could complete the request. Tried: %s' % ', '.join(tried)
        ) from last_exception

    def aggregate_health(self) -> ProviderHealthSummary:
        summary = self.registry.aggregate_health()
        return ProviderHealthSummary(
            overall_status=summary['overall_status'],
            provider_statuses=summary['provider_statuses'],
        )


def get_model_router() -> ModelRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = ModelRouter.from_settings()
    return _router_instance
