from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProviderHealthStatus(str, Enum):
    healthy = 'healthy'
    degraded = 'degraded'
    unhealthy = 'unhealthy'
    unknown = 'unknown'


class ProviderMetadata(BaseModel):
    provider_name: str
    supported_capabilities: List[str] = Field(default_factory=list)
    priority: int = 0
    cost_score: float = 0.0
    latency_score: float = 0.0
    health_status: ProviderHealthStatus = ProviderHealthStatus.unknown
    success_rate: float = 0.0
    failure_rate: float = 0.0
    average_latency_ms: float = 0.0
    last_health_check: str | None = None


class ProviderRegistration(BaseModel):
    provider_name: str
    provider: Optional[Any] = None
    metadata: ProviderMetadata


class RouterConfig(BaseModel):
    default_provider: str = 'gemini'
    fallback_chain: List[str] = Field(default_factory=lambda: ['gemini', 'claude', 'openai', 'bedrock', 'ollama'])
    routing_strategy: str = 'weighted'
    provider_weights: Dict[str, float] = Field(default_factory=lambda: {
        'priority': 1.0,
        'cost_score': 1.0,
        'latency_score': 1.0,
        'health_status': 2.0,
    })


class RoutingDecision(BaseModel):
    selected_provider: str
    reason: str
    candidate_scores: Dict[str, float] = Field(default_factory=dict)
    fallback_chain: List[str] = Field(default_factory=list)


class ProviderHealthSummary(BaseModel):
    overall_status: ProviderHealthStatus
    provider_statuses: List[ProviderMetadata] = Field(default_factory=list)
