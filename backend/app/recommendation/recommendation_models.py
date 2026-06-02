from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class RecommendationContext(BaseModel):
    ocr_text: str = ''
    vision_caption: Optional[str] = None
    labels: List[str] = Field(default_factory=list)
    detected_objects: List[Dict[str, Any]] = Field(default_factory=list)
    intent: Optional[str] = None
    persona: Optional[str] = None
    provider_reasoning: Optional[str] = None
    ocr_confidence: float = 0.0
    provider_success: bool = False
    content_type: str = 'unknown'
    content_category: str = 'unknown'
    content_category_confidence: float = 0.0
    historical_meta: Dict[str, Any] = Field(default_factory=dict)


class RecommendationResult(BaseModel):
    issue_detected: bool = False
    content_type: str = 'unknown'
    content_category: str = 'unknown'
    content_category_confidence: float = 0.0
    persona: Optional[str] = None
    summary: str = ''
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    possible_actions: List[str] = Field(default_factory=list)
    issue_type: Optional[str] = None
    root_cause: Optional[str] = None
    severity: Optional[str] = None
    fixes: List[str] = Field(default_factory=list)
    alternative_solutions: List[str] = Field(default_factory=list)
    step_by_step_fix: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    analysis_mode: str = 'hybrid'
    needs_human_review: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
