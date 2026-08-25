from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime, date


class FarmBoundaryBase(BaseModel):
    geojson: Dict[str, Any]
    perimeter_meters: Optional[float] = None
    calculated_area_hectares: Optional[float] = None


class FarmBoundaryRead(FarmBoundaryBase):
    id: str
    farm_id: str
    verified_by_officer: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FarmCreate(BaseModel):
    name: str
    survey_number: Optional[str] = None
    area_hectares: float
    soil_type: str = "Black Cotton Soil"
    irrigation_source: str = "Borewell"
    center_latitude: float
    center_longitude: float
    boundary_geojson: Optional[Dict[str, Any]] = None


class FarmCropRead(BaseModel):
    id: str
    crop_name: str
    variety: str
    season: str
    sowing_date: date
    current_growth_stage: str
    notified_sum_insured_per_ha: float
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class FarmRead(BaseModel):
    id: str
    farmer_id: str
    farm_code: str
    name: str
    survey_number: Optional[str] = None
    area_hectares: float
    soil_type: str
    irrigation_source: str
    center_latitude: float
    center_longitude: float
    is_active: bool
    created_at: datetime
    boundary: Optional[FarmBoundaryRead] = None
    crops: List[FarmCropRead] = []

    model_config = ConfigDict(from_attributes=True)


class FarmGISSummary(BaseModel):
    id: str
    farm_code: str
    name: str
    farmer_name: str
    village: str
    district: str
    state: str
    crop_name: str
    area_hectares: float
    center_latitude: float
    center_longitude: float
    boundary_geojson: Optional[Dict[str, Any]] = None
    health_score: float = 85.0
    active_risk_level: str = "LOW"
