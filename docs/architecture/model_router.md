# Model Router Architecture

This document describes the Model Router foundation for the AI Visual Copilot backend.

## Goal

Create a configuration-driven router layer that selects, tracks, and fails over between model providers without hardcoded selection logic.

## Components

### Provider Registry

The registry holds provider metadata and instances for all registered providers.

Metadata includes:

- `provider_name`
- `supported_capabilities`
- `priority`
- `cost_score`
- `latency_score`
- `health_status`

The registry is responsible for provider discovery, capability filtering, and health aggregation.

### Routing Strategy

The routing strategy computes scores for each provider using configured weights and health state.

Routing input includes:

- intent
- persona (future support)
- cost
- latency
- health

### Model Router

The router executes provider calls through the registry and strategy.

It supports:

- selecting the best provider dynamically
- using a configured `default_provider`
- honoring a configured `fallback_chain`
- failing over automatically if a provider call fails
- aggregating provider health

## Configuration

Router configuration is driven from `app.core.config.Settings`.

Supported values:

- `default_provider`
- `router_fallback_chain`
- `router_strategy`
- `provider_weights`

## Gemini Integration

Gemini is registered as the primary functional provider.

Remaining providers are registry-ready:

- Claude
- OpenAI
- Bedrock
- Ollama

These providers are registered with metadata and can be selected by the router, but they remain stubbed until full implementation.

## Health Management

The router refreshes health for every registered provider and updates provider metadata.

A health aggregation summary is available for monitoring and routing decisions.
