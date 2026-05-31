import asyncio
from typing import Any, Dict

from app.router.model_router import ModelRouter
from app.router.provider_registry import ProviderRegistry
from app.router.routing_strategy import RoutingStrategy
from app.router.schemas import (
    ProviderHealthStatus,
    ProviderMetadata,
    ProviderRegistration,
    RouterConfig,
)
from app.providers.base_provider import BaseProvider


class DummyProvider(BaseProvider):
    def __init__(self, name: str, healthy: bool = True, fail: bool = False):
        super().__init__(name, ['analyze_image', 'classify_intent'])
        self.name = name
        self.healthy = healthy
        self.fail = fail

    async def analyze_image(self, image_bytes: bytes, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        if self.fail:
            raise RuntimeError('analyze failed')
        return {'provider': self.name, 'analyzed': True}

    async def generate_response(self, prompt: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {'provider': self.name, 'response': prompt}

    async def classify_intent(self, text: str, meta: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return {'intent': self.name, 'confidence': 1.0}

    async def health_check(self) -> Dict[str, Any]:
        return {'ok': self.healthy, 'provider': self.name}


def test_provider_registry_registration():
    registry = ProviderRegistry()
    registry.register(
        'gemini',
        DummyProvider('gemini'),
        supported_capabilities=['analyze_image', 'classify_intent'],
        priority=10,
        cost_score=20.0,
        latency_score=15.0,
        health_status=ProviderHealthStatus.healthy,
    )

    registration = registry.get('gemini')
    assert registration is not None
    assert registration.metadata.provider_name == 'gemini'
    assert registration.metadata.priority == 10
    assert registration.metadata.health_status == ProviderHealthStatus.healthy


def test_routing_strategy_selects_default_provider():
    config = RouterConfig(
        default_provider='gemini',
        fallback_chain=['gemini', 'openai'],
        routing_strategy='weighted',
        provider_weights={'priority': 1.0, 'cost_score': 1.0, 'latency_score': 1.0, 'health_status': 1.0},
    )
    strategy = RoutingStrategy(config)
    providers = [
        ProviderMetadata(
            provider_name='gemini',
            supported_capabilities=['analyze_image'],
            priority=10,
            cost_score=30.0,
            latency_score=20.0,
            health_status=ProviderHealthStatus.healthy,
        ),
        ProviderMetadata(
            provider_name='openai',
            supported_capabilities=['analyze_image'],
            priority=5,
            cost_score=10.0,
            latency_score=10.0,
            health_status=ProviderHealthStatus.healthy,
        ),
    ]

    decision = strategy.select_provider(providers, required_capability='analyze_image')
    assert decision.selected_provider == 'gemini'
    assert decision.reason == 'default_provider'


def test_health_aggregation_returns_degraded_when_any_unhealthy():
    registry = ProviderRegistry()
    registry.register('gemini', DummyProvider('gemini'), health_status=ProviderHealthStatus.healthy)
    registry.register('openai', DummyProvider('openai', healthy=False), health_status=ProviderHealthStatus.unhealthy)

    aggregated = registry.aggregate_health()
    assert aggregated['overall_status'] == ProviderHealthStatus.degraded
    assert any(provider.provider_name == 'openai' for provider in aggregated['provider_statuses'])


def test_execute_with_fallback_uses_next_provider_after_failure():
    config = RouterConfig(
        default_provider='gemini',
        fallback_chain=['gemini', 'openai'],
        routing_strategy='weighted',
        provider_weights={'priority': 1.0, 'cost_score': 1.0, 'latency_score': 1.0, 'health_status': 1.0},
    )
    registry = ProviderRegistry()
    registry.register(
        'gemini',
        DummyProvider('gemini', healthy=True, fail=True),
        supported_capabilities=['analyze_image'],
        priority=10,
        cost_score=20.0,
        latency_score=20.0,
        health_status=ProviderHealthStatus.healthy,
    )
    registry.register(
        'openai',
        DummyProvider('openai', healthy=True, fail=False),
        supported_capabilities=['analyze_image'],
        priority=5,
        cost_score=40.0,
        latency_score=40.0,
        health_status=ProviderHealthStatus.healthy,
    )

    router = ModelRouter(registry, RoutingStrategy(config), config)
    result = asyncio.run(
        router.execute_with_fallback(
            'analyze_image',
            b'fake',
            meta={'source': 'test'},
            required_capability='analyze_image',
        )
    )

    assert result['provider'] == 'openai'
    assert result['result']['provider'] == 'openai'


def test_model_router_selects_healthiest_provider_by_score():
    config = RouterConfig(
        default_provider='claude',
        fallback_chain=['claude', 'gemini'],
        routing_strategy='weighted',
        provider_weights={'priority': 1.0, 'cost_score': 1.0, 'latency_score': 1.0, 'health_status': 1.0},
    )
    strategy = RoutingStrategy(config)
    providers = [
        ProviderMetadata(
            provider_name='claude',
            supported_capabilities=['analyze_image'],
            priority=5,
            cost_score=50.0,
            latency_score=60.0,
            health_status=ProviderHealthStatus.degraded,
        ),
        ProviderMetadata(
            provider_name='gemini',
            supported_capabilities=['analyze_image'],
            priority=10,
            cost_score=20.0,
            latency_score=20.0,
            health_status=ProviderHealthStatus.healthy,
        ),
    ]

    decision = strategy.select_provider(providers, required_capability='analyze_image')
    assert decision.selected_provider == 'gemini'
    assert decision.reason == 'score_based'


def test_provider_metadata_includes_health_metrics():
    provider = DummyProvider('openai')
    metadata = provider.get_provider_metadata()
    assert metadata['provider_name'] == 'openai'
    assert 'success_rate' in metadata
    assert 'failure_rate' in metadata
    assert 'average_latency_ms' in metadata
    assert metadata['last_health_check'] is None


def test_model_router_updates_metrics_on_provider_failure():
    config = RouterConfig(
        default_provider='gemini',
        fallback_chain=['gemini', 'claude'],
        routing_strategy='weighted',
        provider_weights={'priority': 1.0, 'cost_score': 1.0, 'latency_score': 1.0, 'health_status': 1.0},
    )
    registry = ProviderRegistry()
    failing_provider = DummyProvider('gemini', healthy=True, fail=True)
    registry.register(
        'gemini',
        failing_provider,
        supported_capabilities=['analyze_image'],
        priority=10,
        cost_score=20.0,
        latency_score=20.0,
        health_status=ProviderHealthStatus.healthy,
    )
    success_provider = DummyProvider('claude', healthy=True, fail=False)
    registry.register(
        'claude',
        success_provider,
        supported_capabilities=['analyze_image'],
        priority=5,
        cost_score=10.0,
        latency_score=10.0,
        health_status=ProviderHealthStatus.healthy,
    )

    router = ModelRouter(registry, RoutingStrategy(config), config)
    result = asyncio.run(
        router.execute_with_fallback(
            'analyze_image',
            b'fake',
            meta={'source': 'test'},
            required_capability='analyze_image',
        )
    )

    assert result['provider'] == 'claude'
    assert registry.get('gemini').metadata.health_status == ProviderHealthStatus.unhealthy
    assert registry.get('gemini').metadata.failure_rate == 1.0
    assert registry.get('gemini').metadata.success_rate == 0.0
