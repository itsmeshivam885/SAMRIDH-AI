from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.schemas.farm import FarmRead


class FarmerProfile(BaseModel):
    id: str
    user_id: str
    farmer_id_code: str
    full_name: str
    phone_number: str
    state: str
    district: str
    tehsil: Optional[str] = None
    village: str
    pincode: Optional[str] = None
    pmfby_policy_number: Optional[str] = None
    masked_aadhaar: Optional[str] = None
    farms: List[FarmRead] = []

    model_config = ConfigDict(from_attributes=True)


class FarmerCreate(BaseModel):
    state: str
    district: str
    tehsil: Optional[str] = None
    village: str
    pincode: Optional[str] = None
    pmfby_policy_number: Optional[str] = None
    masked_aadhaar: Optional[str] = None
