from fastapi import APIRouter
from app.schemas import WorkflowExecuteRequest, WorkflowExecuteResponse
from app.services.history_service import HistoryService

router = APIRouter(prefix='/api/workflows', tags=['workflows'])

@router.post('/execute', response_model=WorkflowExecuteResponse, summary='Execute a LangGraph workflow')
def execute_workflow(payload: WorkflowExecuteRequest) -> WorkflowExecuteResponse:
    result = HistoryService.execute_workflow(payload)
    return result
