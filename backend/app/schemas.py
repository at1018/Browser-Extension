from pydantic import BaseModel
from typing import Any, Dict, List, Optional

class ScreenshotUploadRequest(BaseModel):
    source: str
    user_id: Optional[str] = 'anonymous'
    meta: Optional[Dict[str, Any]] = {}

class ScreenshotAnalyzeRequest(BaseModel):
    image_base64: str
    source: str
    persona: Optional[str] = 'unknown'
    meta: Optional[Dict[str, Any]] = {}

class ScreenshotAnalyzeResponse(BaseModel):
    analysis_id: str
    intent: str
    persona: str
    results: Dict[str, Any]

class ScreenshotRecord(BaseModel):
    screenshot_id: str
    user_id: str
    source: str
    uploaded_at: str
    status: str
    analysis_summary: Dict[str, Any]

class UserProfile(BaseModel):
    user_id: str
    email: str
    full_name: str
    persona: str
    subscription_plan: str
    created_at: str

class AnalysisResult(BaseModel):
    analysis_id: str
    intent: str
    persona: str
    results: Dict[str, Any]
    created_at: Optional[str] = None

class WorkflowExecuteRequest(BaseModel):
    workflow_id: str
    screenshot_id: str
    persona: str
    input: Optional[Dict[str, Any]] = {}

class WorkflowExecuteResponse(BaseModel):
    execution_id: str
    workflow_id: str
    screenshot_id: str
    persona: str
    status: str
    output: Dict[str, Any]
