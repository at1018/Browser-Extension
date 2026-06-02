from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class PersonaDefinition(BaseModel):
    name: str
    description: str
    traits: List[str]
    common_tools: List[str]
    confidence_floor: float = Field(default=0.0)


class PersonaSignal(BaseModel):
    source: str
    persona: str
    score: float
    evidence: Optional[str] = None


class PersonaResult(BaseModel):
    persona: str
    confidence: float
    reasoning: str
    traits: List[str]
    signals: List[PersonaSignal]
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DetectObject(BaseModel):
    label: str
    box_2d: list
class PersonaContext(BaseModel):
    ocr_text: str
    caption: Optional[str]
    labels: List[str]
    objects: List[DetectObject]
    intent: Optional[str]
    provider_reasoning: Optional[str]
    ocr_confidence: float = 0.0
    provider_success: bool = False
    historical_meta: Dict[str, Any] = Field(default_factory=dict)
