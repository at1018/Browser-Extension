# Gemini Provider (Phase 5)

`GeminiProvider` is the first provider implementation. It adheres to the
`BaseProvider` interface and currently supports a mock/stub mode when the
`GEMINI_API_KEY` environment variable is not set. Real API integration will be
implemented in subsequent iterations.

Files:
- `backend/app/providers/gemini_provider.py`

Environment:
- `GEMINI_API_KEY` — when present, the provider will attempt (in future
  implementation) to call Gemini APIs.

Testing:
- Unit tests: `backend/tests/test_gemini_provider.py` (mock mode)
