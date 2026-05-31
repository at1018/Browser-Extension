from typing import List
from uuid import uuid4

from app.router.model_router import ModelRouter
from app.schemas import ScreenshotUploadRequest, ScreenshotAnalyzeRequest, ScreenshotAnalyzeResponse, ScreenshotRecord
from app.services.analysis_service import AnalysisService

class ScreenshotService:
    _screenshots: List[ScreenshotRecord] = []

    @classmethod
    def create_screenshot(cls, payload: ScreenshotUploadRequest) -> ScreenshotRecord:
        record = ScreenshotRecord(
            screenshot_id=str(uuid4()),
            user_id='anonymous',
            source=payload.source,
            uploaded_at='2026-01-01T00:00:00Z',
            status='uploaded',
            analysis_summary={'message': 'Waiting for analysis'},
        )
        cls._screenshots.append(record)
        return record

    @classmethod
    async def analyze_screenshot(cls, payload: ScreenshotAnalyzeRequest, router: ModelRouter) -> ScreenshotAnalyzeResponse:
        result = await AnalysisService.run_analysis(payload, router)
        cls._screenshots.append(
            ScreenshotRecord(
                screenshot_id=str(uuid4()),
                user_id='anonymous',
                source=payload.source,
                uploaded_at='2026-01-01T00:00:00Z',
                status='analyzed',
                analysis_summary=result.results,
            )
        )
        return result

    @classmethod
    def list_screenshots(cls) -> List[ScreenshotRecord]:
        return cls._screenshots
