from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.damage import DamageReportRead


class ClaimEventRead(BaseModel):
    id: str
    event_type: str
    actor_role: str
    actor_id: Optional[str] = None
    message: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimDocumentRead(BaseModel):
    id: str
    doc_type: str
    file_path: str
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimRead(BaseModel):
    id: str
    claim_number: str
    damage_report_id: str
    farm_id: str
    farmer_id: str
    crop_season_name: str
    ai_damage_percentage: float
    ai_confidence_score: float
    ai_fraud_risk: str
    estimated_payout_amount: float
    status: str
    assigned_officer_id: Optional[str] = None
    officer_decision: Optional[str] = None
    officer_reviewed_at: Optional[datetime] = None
    officer_remarks: Optional[str] = None
    approved_loss_percentage: Optional[float] = None
    final_sanctioned_amount: Optional[float] = None
    settlement_status: str
    created_at: datetime
    updated_at: datetime
    damage_report: Optional[DamageReportRead] = None
    events: List[ClaimEventRead] = []
    documents: List[ClaimDocumentRead] = []

    model_config = ConfigDict(from_attributes=True)


class ClaimReviewAction(BaseModel):
    decision: str
    remarks: str
    approved_loss_percentage: Optional[float] = None
    sanctioned_payout_amount: Optional[float] = None


class SettlementStatusUpdate(BaseModel):
    settlement_status: str
    pmfby_application_id: Optional[str] = None
    pmfby_settlement_reference: Optional[str] = None
