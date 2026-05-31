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


class PersonaContext(BaseModel):
    ocr_text: str
    caption: Optional[str]
    labels: List[str]
    objects: List[str]
    intent: Optional[str]
    provider_reasoning: Optional[str]
    historical_meta: Dict[str, Any] = Field(default_factory=dict)
