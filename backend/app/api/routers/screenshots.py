from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from typing import List
import base64

from app.schemas import (
    ScreenshotUploadRequest,
    ScreenshotAnalyzeRequest,
    ScreenshotAnalyzeResponse,
    ScreenshotRecord,
)
from app.router import get_model_router
from app.router.model_router import ModelRouter
from app.services.screenshot_service import ScreenshotService

router = APIRouter(prefix='/api/screenshots', tags=['screenshots'])

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}


def _validate_file_extension(filename: str) -> None:
    if not filename:
        raise HTTPException(status_code=400, detail='Image file is required')

    ext = filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail='Unsupported file type')


@router.post('/upload', response_model=ScreenshotRecord, summary='Upload screenshot metadata')
def upload_screenshot(payload: ScreenshotUploadRequest, db=Depends(lambda: None)) -> ScreenshotRecord:
    record = ScreenshotService.create_screenshot(payload)
    return record

@router.post('/analyze', response_model=ScreenshotAnalyzeResponse, summary='Analyze screenshot via OCR and vision pipeline')
async def analyze_screenshot(payload: ScreenshotAnalyzeRequest, router: ModelRouter = Depends(get_model_router)) -> ScreenshotAnalyzeResponse:
    try:
        return await ScreenshotService.analyze_screenshot(payload, router)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post('/analyze-upload', response_model=ScreenshotAnalyzeResponse, summary='Analyze screenshot from file upload')
async def analyze_upload(
    image: UploadFile = File(...),
    persona: str = Form('unknown'),
    source: str = Form('upload'),
    router: ModelRouter = Depends(get_model_router),
) -> ScreenshotAnalyzeResponse:
    try:
        if not image.filename:
            raise HTTPException(status_code=400, detail='Image file is required')

        _validate_file_extension(image.filename)

        image_bytes = await image.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail='Image file is empty')

        image_base64 = base64.b64encode(image_bytes).decode('utf-8')

        request = ScreenshotAnalyzeRequest(
            image_base64=image_base64,
            source=source,
            persona=persona,
            meta={},
        )

        return await ScreenshotService.analyze_screenshot(request, router)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get('/history', response_model=List[ScreenshotRecord], summary='List screenshot history')
def list_screenshots() -> List[ScreenshotRecord]:
    return ScreenshotService.list_screenshots()
