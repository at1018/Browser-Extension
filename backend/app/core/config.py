from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = 'AI Visual Copilot Backend'
    api_prefix: str = '/api'
    backend_cors_origins: list[str] = ['*']
    supabase_url: str | None = None
    supabase_key: str | None = None
    stripe_api_key: str | None = None

    model_provider: str = 'gemini'
    default_provider: str = 'gemini'
    router_fallback_chain: list[str] = ['gemini', 'claude', 'openai', 'bedrock', 'ollama']
    router_strategy: str = 'weighted'
    provider_weights: dict[str, float] = {'priority': 1.0, 'cost_score': 1.0, 'latency_score': 1.0, 'health_status': 2.0}

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = 'gemini-2.5-flash'
    CLAUDE_API_KEY: str | None = None
    OPENAI_API_KEY: str | None = None
    ANTHROPIC_API_KEY: str | None = None
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    BEDROCK_REGION: str | None = None
    BEDROCK_API_KEY: str | None = None
    OLLAMA_API_KEY: str | None = None
    OLLAMA_BASE_URL: str | None = None
    gemini_timeout_seconds: int = 30
    gemini_retry_attempts: int = 2
    gemini_retry_backoff: float = 1.0
    tesseract_cmd: str | None = None
    # tesseract_cmd: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    tesseract_lang: str = 'eng'

    PERSONA_MIN_CONFIDENCE: float = 0.65
    PERSONA_RULE_WEIGHT: float = 0.6
    PERSONA_LLM_WEIGHT: float = 0.4
    PERSONA_INTENT_WEIGHT: float = 2.0

    model_config = ConfigDict(env_file='.env', case_sensitive=True)


settings = Settings()
