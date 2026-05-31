from __future__ import annotations

from typing import Dict, List, Optional

from app.router.schemas import ProviderHealthStatus, ProviderMetadata, RouterConfig, RoutingDecision


class RoutingStrategy:
    def __init__(self, config: RouterConfig) -> None:
        self.config = config

    def _health_multiplier(self, status: ProviderHealthStatus) -> float:
        return {
            ProviderHealthStatus.healthy: 1.0,
            ProviderHealthStatus.degraded: 0.6,
            ProviderHealthStatus.unknown: 0.5,
            ProviderHealthStatus.unhealthy: 0.0,
        }[status]

    def _score_provider(self, metadata: ProviderMetadata, required_capability: Optional[str] = None) -> float:
        if required_capability and required_capability not in metadata.supported_capabilities:
            return -9999.0
        if metadata.health_status == ProviderHealthStatus.unhealthy:
            return -9999.0

        weights = self.config.provider_weights
        priority_weight = weights.get('priority', 1.0)
        cost_weight = weights.get('cost_score', 1.0)
        latency_weight = weights.get('latency_score', 1.0)
        health_weight = weights.get('health_status', 1.0)

        score = metadata.priority * priority_weight
        score += max(0.0, 100.0 - metadata.cost_score) * cost_weight
        score += max(0.0, 100.0 - metadata.latency_score) * latency_weight
        score += self._health_multiplier(metadata.health_status) * 100.0 * health_weight
        return score

    def select_provider(
        self,
        providers: List[ProviderMetadata],
        required_capability: str,
        intent: Optional[str] = None,
        persona: Optional[str] = None,
    ) -> RoutingDecision:
        scores: Dict[str, float] = {}
        for metadata in providers:
            scores[metadata.provider_name] = self._score_provider(metadata, required_capability)

        fallback_chain = [name.lower() for name in self.config.fallback_chain]
        selected = None
        reason = 'highest_score'

        default_name = self.config.default_provider.lower()
        # Prefer configured default provider if it is present and healthy
        default_meta = next((m for m in providers if m.provider_name.lower() == default_name), None)
        if default_meta is not None and default_meta.health_status == ProviderHealthStatus.healthy:
            if default_name in scores and scores[default_name] >= 0:
                selected = default_name
                reason = 'default_provider'
        else:
            # If routing_strategy is explicitly 'default', still try to use it when available
            if self.config.routing_strategy == 'default' and default_name in scores and scores[default_name] >= 0:
                selected = default_name
                reason = 'default_provider'
            else:
                # Default behavior: weighted scoring - select highest score provider
                candidate = max(scores.items(), key=lambda item: item[1]) if scores else (None, -9999.0)
                if candidate[0] and candidate[1] >= 0:
                    selected = candidate[0]
                    reason = 'score_based'

        if selected is None:
            for provider_name in fallback_chain:
                if scores.get(provider_name, -9999.0) >= 0:
                    selected = provider_name
                    reason = 'fallback_chain'
                    break

        if selected is None and scores:
            selected = max(scores.items(), key=lambda item: item[1])[0]
            reason = 'fallback_no_healthy'

        return RoutingDecision(
            selected_provider=selected or '',
            reason=reason,
            candidate_scores=scores,
            fallback_chain=fallback_chain,
        )
