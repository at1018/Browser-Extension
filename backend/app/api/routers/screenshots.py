from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.schemas import (
    ScreenshotUploadRequest,
    ScreenshotAnalyzeRequest,
    ScreenshotAnalyzeResponse,
    ScreenshotRecord,
)
from app.services.screenshot_service import ScreenshotService
from app.providers import get_provider
from app.providers.base_provider import BaseProvider
from fastapi import Depends

router = APIRouter(prefix='/api/screenshots', tags=['screenshots'])

@router.post('/upload', response_model=ScreenshotRecord, summary='Upload screenshot metadata')
def upload_screenshot(payload: ScreenshotUploadRequest, db=Depends(lambda: None)) -> ScreenshotRecord:
    record = ScreenshotService.create_screenshot(payload)
    return record

@router.post('/analyze', response_model=ScreenshotAnalyzeResponse, summary='Analyze screenshot via OCR and vision pipeline')
async def analyze_screenshot(payload: ScreenshotAnalyzeRequest, provider: BaseProvider = Depends(get_provider)) -> ScreenshotAnalyzeResponse:
    try:
        return await ScreenshotService.analyze_screenshot(payload, provider)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get('/history', response_model=List[ScreenshotRecord], summary='List screenshot history')
def list_screenshots() -> List[ScreenshotRecord]:
    return ScreenshotService.list_screenshots()
