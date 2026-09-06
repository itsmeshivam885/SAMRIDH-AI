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
    claims_admin_hold: int = 0
    total_estimated_loss_inr: float
    total_sanctioned_payout_inr: float
    high_risk_fraud_flags_count: int
    district_wise_claim_density: Dict[str, int] = {}
    district_wise_area_ha: Dict[str, float] = {}
    claim_status_pipeline: Dict[str, int] = {}
    claims_pending_review_count: int = 0


class UserStatusUpdate(BaseModel):
    is_active: bool
    reason: Optional[str] = "Admin account status update"


class UserRoleUpdate(BaseModel):
    role: str
    assigned_state: Optional[str] = None
    assigned_district: Optional[str] = None
    reason: Optional[str] = "Admin role/jurisdiction reassignment"


class FraudOverrideRequest(BaseModel):
    new_risk_level: str  # LOW, MEDIUM, HIGH
    justification_notes: str


class ClaimHoldRequest(BaseModel):
    action: str  # HOLD, RELEASE
    reason_notes: str


class SystemSettingRead(BaseModel):
    id: str
    key: str
    value: str
    description: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class SystemSettingUpdate(BaseModel):
    value: str
    reason: Optional[str] = "Administrative parameter adjustment"


class AuditLogRead(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = "127.0.0.1"
    details: Dict[str, Any] = {}
    timestamp: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class FraudRadarItem(BaseModel):
    claim_id: str
    claim_number: str
    farmer_name: str
    farm_code: str
    district: str
    overall_fraud_risk: str
    fraud_risk_score: float
    geofence_status: str
    distance_to_boundary_meters: float
    duplicate_image_flag: bool
    min_phash_hamming_distance: float
    baseline_match_score: float
    flag_reasons: List[str] = []
    resolution_status: str = "UNRESOLVED"
    resolution_notes: Optional[str] = None
    created_at: Optional[datetime] = None


class FraudRadarSummary(BaseModel):
    total_flagged_evidence: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    geofence_breach_count: int
    duplicate_phash_count: int
    unresolved_count: int
    items: List[FraudRadarItem] = []


class DistrictSummaryRead(BaseModel):
    district: str
    total_farmers: int
    total_farms: int
    total_claims: int
    pending_claims: int
    approved_claims: int
    rejected_claims: int
    high_risk_claims: int
    active_officers: int
    disaster_events: int
    total_claimed_amount: float = 0.0
    total_sanctioned_amount: float = 0.0


class DistrictDetailRead(BaseModel):
    district: str
    total_farmers: int
    total_farms: int
    total_hectares: float
    total_claims: int
    pending_claims: int
    approved_claims: int
    rejected_claims: int
    high_risk_claims: int
    total_est_loss_inr: float
    total_sanctioned_payout_inr: float
    active_officers: int
    disaster_events: int
    recent_audit_count: int
    claim_status_breakdown: Dict[str, int] = {}


class SeasonNotificationRead(BaseModel):
    season: str
    year: int
    state: str
    status: str
    published_date: Optional[str] = None
    districts_covered: int
    insurance_units_count: int
    notified_crops: List[str]
    insurer_name: str
    sum_insured_ha_inr: float
    indemnity_level_pct: float
    threshold_yield_kg_ha: float
    farmer_premium_rate_pct: float
    govt_subsidy_rate_pct: float


class CCEMonitoringRead(BaseModel):
    district: str
    insurance_unit: str
    crop_name: str
    cce_planned: int
    cce_scheduled: int
    cce_completed: int
    cce_pending: int
    data_submitted_count: int
    review_required_count: int
    last_survey_date: Optional[str] = None
    assigned_officer: str
    gps_lat_lng: str
    observed_yield_kg_ha: float
    threshold_yield_kg_ha: float
    yield_shortfall_pct: float
    indicative_claim_trigger: bool


class SLAMonitoringRead(BaseModel):
    grievance_id: str
    claim_reference: str
    district: str
    responsible_stakeholder: str
    received_date: str
    configured_due_date: str
    current_status: str  # OPEN, DUE_SOON, BREACHED, ESCALATED, RESOLVED
    delay_reason: Optional[str] = None
    timeline_days: int


class FinancialReconciliationRead(BaseModel):
    district: str
    season: str
    total_expected_premium_inr: float
    farmer_share_received_inr: float
    govt_subsidy_received_inr: float
    outstanding_subsidy_inr: float
    sanctioned_claim_payouts_inr: float
    net_variance_inr: float
    reconciliation_status: str  # MATCHED, PENDING, VARIANCE_DETECTED, UNDER_RECONCILIATION, RESOLVED




