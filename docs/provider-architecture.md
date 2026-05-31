# Provider architecture

This document explains the provider abstraction layer for multi-provider routing in AI Visual Copilot.

## Phase 6 Enhancements

Phase 6 added support for the following providers:

- Gemini
- Claude / Anthropic
- OpenAI
- AWS Bedrock
- Ollama

The new implementation is centered on the router and the shared provider interface.

## Provider Interface

All providers now inherit from `app/providers/base_provider.py` and expose:

- `analyze_image(image_bytes, meta)`
- `generate_response(prompt, meta)`
- `classify_intent(text, meta)`
- `health_check()`
- `get_provider_metadata()`

Each provider also reports runtime metrics and health metadata.

## Provider Lifecycle

1. Providers are registered in `app/router/model_router.py` by `ModelRouter.from_settings()`.
2. Registration binds a provider name, implementation instance, supported capabilities, priority, cost score, latency score, and initial health state.
3. At startup, `app/main.py` calls `router.refresh_health()` to probe providers and update their health metadata.
4. During request execution, `ModelRouter.execute_with_fallback()` selects a provider and runs the requested operation.

## Routing Flow

The routing flow is:

1. Receive `/api/screenshots/analyze` request.
2. Run OCR via `AnalysisService`.
3. Route `analyze_image` through `ModelRouter`.
4. Route `classify_intent` through `ModelRouter`.

Routing uses `RoutingStrategy` to score available providers by:

- `priority`
- `cost_score`
- `latency_score`
- `health_status`

The selected provider is returned with its routing decision.

## Fallback Sequence

The default fallback chain is configured in `backend/app/core/config.py`:

- `gemini`
- `claude`
- `openai`
- `bedrock`
- `ollama`

If a provider fails during execution, the router logs the failure, marks the provider unhealthy, and continues to the next provider in the chain.

## Health Monitoring

Provider metadata now tracks:

- `success_rate`
- `failure_rate`
- `average_latency_ms`
- `last_health_check`

Health metrics are updated during both provider execution and explicit health probes.

## Configuration

Settings are loaded from `.env` via `backend/app/core/config.py`.

Supported environment variables include:

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_BASE_URL`
- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `BEDROCK_REGION`
- `BEDROCK_API_KEY`
- `OLLAMA_BASE_URL`
- `OLLAMA_API_KEY`

A sample file is available at `.env.example`.

## Backward Compatibility

The `/api/screenshots/analyze` endpoint remains unchanged. The new provider layer is an internal routing and orchestration improvement that preserves the existing API contract.
