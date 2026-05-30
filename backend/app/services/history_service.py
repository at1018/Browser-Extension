from typing import List, Optional
from uuid import uuid4

from app.schemas import AnalysisResult, ScreenshotRecord, WorkflowExecuteRequest, WorkflowExecuteResponse
from app.services.screenshot_service import ScreenshotService

class HistoryService:
    _analysis_results: List[AnalysisResult] = []

    @classmethod
    def list_screenshots(cls) -> List[ScreenshotRecord]:
        return ScreenshotService.list_screenshots()

    @classmethod
    def get_analysis(cls, analysis_id: str) -> Optional[AnalysisResult]:
        return next((item for item in cls._analysis_results if item.analysis_id == analysis_id), None)

    @classmethod
    def execute_workflow(cls, payload: WorkflowExecuteRequest) -> WorkflowExecuteResponse:
        result = WorkflowExecuteResponse(
            execution_id=str(uuid4()),
            workflow_id=payload.workflow_id,
            screenshot_id=payload.screenshot_id,
            persona=payload.persona,
            status='completed',
            output={'message': 'Workflow execution is stubbed for Phase 3.'},
        )
        return result
