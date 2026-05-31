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
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = 'gemini-2.5-flash'
    gemini_timeout_seconds: int = 30
    gemini_retry_attempts: int = 2
    gemini_retry_backoff: float = 1.0
    tesseract_cmd: str | None = None
    # tesseract_cmd: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    tesseract_lang: str = 'eng'

    model_config = ConfigDict(env_file='.env', case_sensitive=True)


settings = Settings()
