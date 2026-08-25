from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class AdvisoryRead(BaseModel):
    id: str
    farm_id: str
    category: str
    priority: str
    title: str
    title_hi: Optional[str] = None
    message: str
    message_hi: Optional[str] = None
    reasoning: Dict[str, Any] = {}
    action_items: List[str] = []
    is_read: bool
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AICropDoctorQuery(BaseModel):
    farm_id: Optional[str] = None
    question: str
    language: str = "en"


class AICropDoctorResponse(BaseModel):
    answer: str
    answer_hi: Optional[str] = None
    grounded_context_used: Dict[str, Any] = {}
    confidence: float = 0.95
    recommended_action: Optional[str] = None
