import os
from app.core.config import settings
from app.providers.base_provider import BaseProvider
from app.providers.gemini_provider import GeminiProvider


def get_provider() -> BaseProvider:
    """Factory dependency to return the configured provider.

    Uses `PROVIDER` env var to pick provider. Defaults to GeminiProvider.
    """
    provider_name = os.environ.get('PROVIDER', settings.model_provider).lower()
    if provider_name == 'gemini':
        return GeminiProvider(
            api_key=settings.GEMINI_API_KEY,
            model=settings.GEMINI_MODEL,
            timeout_seconds=settings.gemini_timeout_seconds,
            retry_attempts=settings.gemini_retry_attempts,
            retry_backoff=settings.gemini_retry_backoff,
        )
    # Future providers can be wired here
    return GeminiProvider(
        api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL,
        timeout_seconds=settings.gemini_timeout_seconds,
        retry_attempts=settings.gemini_retry_attempts,
        retry_backoff=settings.gemini_retry_backoff,
    )
