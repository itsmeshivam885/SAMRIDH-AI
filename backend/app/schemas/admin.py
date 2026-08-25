from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.claim import ClaimRead
from app.schemas.officer import OfficerRead, FieldVerificationRead
from app.schemas.advisory import AdvisoryRead, AICropDoctorQuery, AICropDoctorResponse


class AdminDashboardStats(BaseModel):
    total_registered_farmers: int
    total_monitored_hectares: float
    active_soil_sensors: int
    active_disasters_count: int
    total_claims_submitted: int
    claims_under_review: int
    claims_approved: int
    claims_rejected: int
    total_estimated_loss_inr: float
    total_sanctioned_payout_inr: float
    high_risk_fraud_flags_count: int
    district_wise_claim_density: Dict[str, int] = {}
