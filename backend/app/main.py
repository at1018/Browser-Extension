import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_router
from app.core.config import settings
from app.ocr.ocr_service import OCRService
from app.providers import get_provider

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version='0.1.0',
    description='FastAPI backend for AI Visual Copilot',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.on_event('startup')
async def startup_health_checks() -> None:
    provider = get_provider()
    health = await provider.health_check()
    if not health.get('ok', False):
        logger.warning('Gemini health check failed: %s', health)
    else:
        logger.info('Gemini provider startup healthy: %s', health)

    diagnostics = OCRService.diagnose()
    if not diagnostics.get('pytesseract_installed', False) or not diagnostics.get('tesseract_available', False):
        logger.warning('OCR diagnostics detected issues: %s', diagnostics)
    else:
        logger.info('OCR diagnostics healthy: %s', diagnostics)

app.include_router(api_router)
