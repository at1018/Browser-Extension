# Provider architecture

This document explains the provider abstraction layer (Phase 5) used to
integrate multimodal model providers such as Gemini, OpenAI, Claude, Bedrock,
and Ollama.

Key points:
- `app/providers/base_provider.py` defines the `BaseProvider` abstract class.
- Each provider implements async methods: `analyze_image`, `generate_response`,
  `classify_intent`, and `health_check`.
- Providers are injected into API endpoints using the `get_provider` factory
  in `app/providers/__init__.py`.

This layer is intentionally thin and provider-agnostic; business workflows and
orchestration are implemented at the service layer (`AnalysisService`).
