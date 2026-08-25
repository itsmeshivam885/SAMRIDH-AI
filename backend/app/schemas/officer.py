from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class OfficerRead(BaseModel):
    id: str
    user_id: str
    officer_badge_number: str
    designation: str
    assigned_state: str
    assigned_district: str
    assigned_tehsil: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FieldVerificationCreate(BaseModel):
    claim_id: str
    scheduled_date: datetime
    officer_notes: Optional[str] = None


class FieldVerificationRead(BaseModel):
    id: str
    claim_id: str
    officer_id: str
    scheduled_date: datetime
    conducted_date: Optional[datetime] = None
    status: str
    ground_damage_percentage: Optional[float] = None
    verified_gps_lat: Optional[float] = None
    verified_gps_lon: Optional[float] = None
    field_photos: List[str] = []
    officer_notes: Optional[str] = None
    discrepancy_found: bool

    model_config = ConfigDict(from_attributes=True)
