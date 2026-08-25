from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class EvidenceValidationRead(BaseModel):
    id: str
    blur_score: float
    is_blurry: bool
    mean_luminance: float
    is_exposure_acceptable: bool
    resolution_width: float
    resolution_height: float
    passed_quality_gate: bool
    validation_remarks: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FraudCheckRead(BaseModel):
    id: str
    is_inside_geofence: bool
    distance_to_boundary_meters: float
    geofence_status: str
    duplicate_image_flag: bool
    min_phash_hamming_distance: float
    baseline_match_score: float
    landmarks_aligned: bool
    overall_fraud_risk: str
    fraud_risk_score: float
    flag_reasons: List[str] = []
    requires_manual_audit: bool

    model_config = ConfigDict(from_attributes=True)


class DamageEvidenceRead(BaseModel):
    id: str
    damage_report_id: str
    file_path: str
    file_name: str
    file_size_bytes: float
    gps_latitude: float
    gps_longitude: float
    captured_at: datetime
    uploaded_at: datetime
    is_primary: bool
    validation: Optional[EvidenceValidationRead] = None
    fraud_check: Optional[FraudCheckRead] = None

    model_config = ConfigDict(from_attributes=True)


class DamageAssessmentRead(BaseModel):
    id: str
    damage_report_id: str
    ai_model_name: str
    ai_model_version: str
    damage_percentage: float
    primary_damage_type: str
    confidence_score: float
    segment_breakdown: Dict[str, float] = {}
    segmentation_mask_url: Optional[str] = None
    processing_time_ms: float
    warnings: List[str] = []

    model_config = ConfigDict(from_attributes=True)


class DamageReportCreate(BaseModel):
    farm_id: str
    disaster_event_id: Optional[str] = None
    loss_category: str
    farmer_reported_loss_percentage: float
    description: Optional[str] = None
    incident_date: Optional[datetime] = None


class DamageReportRead(BaseModel):
    id: str
    farm_id: str
    report_code: str
    loss_category: str
    farmer_reported_loss_percentage: float
    incident_date: datetime
    reported_at: datetime
    description: Optional[str] = None
    status: str
    evidence_items: List[DamageEvidenceRead] = []
    assessment: Optional[DamageAssessmentRead] = None

    model_config = ConfigDict(from_attributes=True)
