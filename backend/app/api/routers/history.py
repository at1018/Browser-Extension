from fastapi import APIRouter, HTTPException
from app.services.history_service import HistoryService
from app.schemas import AnalysisResult, ScreenshotRecord

router = APIRouter(prefix='/api/history', tags=['history'])

@router.get('/screenshots', response_model=list[ScreenshotRecord], summary='Get screenshot history')
def screenshot_history() -> list[ScreenshotRecord]:
    return HistoryService.list_screenshots()

@router.get('/analysis/{analysis_id}', response_model=AnalysisResult, summary='Get detailed analysis result')
def analysis_detail(analysis_id: str) -> AnalysisResult:
    result = HistoryService.get_analysis(analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail='Analysis result not found')
    return result
