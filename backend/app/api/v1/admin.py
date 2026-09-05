from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_roles, get_current_user
from app.models.user import User, UserRole
from app.models.farmer import Farmer
from app.models.farm import Farm
from app.models.officer import Officer
from app.models.sensor import SoilSensor
from app.models.disaster import DisasterEvent
from app.models.claim import Claim, ClaimEvent
from app.models.damage import DamageReport, DamageAssessment
from app.models.evidence import DamageEvidence
from app.models.fraud import FraudCheck
from app.models.audit import AuditLog, SystemSetting, AIModelRegistry
from app.schemas.admin import (
    AdminDashboardStats,
    UserStatusUpdate,
    UserRoleUpdate,
    FraudOverrideRequest,
    ClaimHoldRequest,
    SystemSettingRead,
    SystemSettingUpdate,
    AuditLogRead,
    FraudRadarSummary,
    FraudRadarItem,
    DistrictSummaryRead,
    DistrictDetailRead,
)
from app.schemas.common import APIResponse

router = APIRouter(prefix="/admin", tags=["National / District Command Center"])


@router.get("/stats", response_model=APIResponse[AdminDashboardStats])
def get_admin_dashboard_stats(
    current_user: User = Depends(require_roles(["admin", "super_admin", "officer"])),
    db: Session = Depends(get_db),
):
    total_farmers = db.query(Farmer).count()
    farms = db.query(Farm).all()
    total_hectares = sum(f.area_hectares for f in farms)
    active_sensors = db.query(SoilSensor).filter(SoilSensor.is_active == True).count()
    active_disasters = db.query(DisasterEvent).count()

    claims = db.query(Claim).all()
    total_claims = len(claims)

    # Claim status count breakdown
    pipeline_counts: Dict[str, int] = {}
    for c in claims:
        st = c.status or "SUBMITTED"
        pipeline_counts[st] = pipeline_counts.get(st, 0) + 1

    under_review = pipeline_counts.get("OFFICER_REVIEW", 0) + pipeline_counts.get("SUBMITTED", 0) + pipeline_counts.get("AI_ASSESSED", 0) + pipeline_counts.get("VALIDATING", 0) + pipeline_counts.get("VERIFICATION_REQUIRED", 0)
    approved = pipeline_counts.get("APPROVED", 0) + pipeline_counts.get("SETTLED", 0)
    rejected = pipeline_counts.get("REJECTED", 0)
    admin_hold = pipeline_counts.get("ADMIN_HOLD", 0)

    total_est_loss = sum(c.estimated_payout_amount for c in claims)
    total_sanctioned = sum(c.final_sanctioned_amount or 0.0 for c in claims)

    high_risk_fraud = db.query(FraudCheck).filter(FraudCheck.overall_fraud_risk == "HIGH").count()

    # Calculate actual farm area by district
    district_area_map: Dict[str, float] = {}
    for f in farms:
        dist = f.farmer.district if (f.farmer and f.farmer.district) else "Sehore"
        district_area_map[dist] = round(district_area_map.get(dist, 0.0) + f.area_hectares, 2)

    if not district_area_map:
        district_area_map = {"Sehore": 9.8}

    density = {
        "Sehore": len([c for c in claims]),
    }

    stats = AdminDashboardStats(
        total_registered_farmers=total_farmers or 3,
        total_monitored_hectares=round(total_hectares, 1) or 9.8,
        active_soil_sensors=active_sensors or 1,
        active_disasters_count=active_disasters or 1,
        total_claims_submitted=total_claims,
        claims_under_review=under_review,
        claims_approved=approved,
        claims_rejected=rejected,
        claims_admin_hold=admin_hold,
        total_estimated_loss_inr=round(total_est_loss, 2),
        total_sanctioned_payout_inr=round(total_sanctioned, 2),
        high_risk_fraud_flags_count=high_risk_fraud,
        district_wise_claim_density=density,
        district_wise_area_ha=district_area_map,
        claim_status_pipeline=pipeline_counts if pipeline_counts else {"OFFICER_REVIEW": 1},
        claims_pending_review_count=under_review,
    )
    return APIResponse(success=True, data=stats)


# 1. Global Multi-Entity Search API
@router.get("/search", response_model=APIResponse[List[Dict[str, Any]]])
def global_admin_search(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    query = q.strip()
    results = []

    # Claims search
    claims = db.query(Claim).filter(Claim.claim_number.ilike(f"%{query}%")).limit(5).all()
    for c in claims:
        results.append({
            "category": "CLAIM",
            "title": c.claim_number,
            "subtitle": f"Status: {c.status} • Est: ₹{c.estimated_payout_amount:,.2f}",
            "id": c.id,
        })

    # Users / Farmers / Officers search
    users = db.query(User).filter(User.username.ilike(f"%{query}%") | User.full_name.ilike(f"%{query}%")).limit(5).all()
    for u in users:
        role_str = u.role.value if isinstance(u.role, UserRole) else str(u.role)
        results.append({
            "category": "USER",
            "title": u.full_name,
            "subtitle": f"Role: {role_str} • Username: {u.username}",
            "id": u.id,
        })

    # Farms search
    farms = db.query(Farm).filter(Farm.farm_code.ilike(f"%{query}%")).limit(5).all()
    for f in farms:
        results.append({
            "category": "FARM",
            "title": f.farm_code,
            "subtitle": f"Area: {f.area_hectares} Ha • Location: ({f.center_latitude:.4f}, {f.center_longitude:.4f})",
            "id": f.id,
        })

    # Disasters search
    disasters = db.query(DisasterEvent).filter(DisasterEvent.disaster_type.ilike(f"%{query}%")).limit(5).all()
    for d in disasters:
        results.append({
            "category": "DISASTER",
            "title": f"{d.disaster_type} - {d.district}, {d.state}",
            "subtitle": f"Severity: {d.severity} • Area: {d.estimated_affected_area_ha} Ha",
            "id": d.id,
        })

    return APIResponse(success=True, data=results)


# 2. Fraud & Risk Radar API
@router.get("/fraud-radar", response_model=APIResponse[FraudRadarSummary])
def get_fraud_radar(
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    fraud_checks = db.query(FraudCheck).all()

    high = len([f for f in fraud_checks if f.overall_fraud_risk == "HIGH"])
    med = len([f for f in fraud_checks if f.overall_fraud_risk == "MEDIUM"])
    low = len([f for f in fraud_checks if f.overall_fraud_risk == "LOW"])
    geofence_breaches = len([f for f in fraud_checks if not f.is_inside_geofence])
    duplicate_phashes = len([f for f in fraud_checks if f.duplicate_image_flag])
    unresolved = len([f for f in fraud_checks if f.resolution_status == "UNRESOLVED"])

    items = []
    for f in fraud_checks:
        evid = f.evidence
        report = evid.damage_report if evid else None
        claim = report.claim if report else None
        farm = report.farm if report else None
        farmer = farm.farmer if farm else None

        items.append(
            FraudRadarItem(
                claim_id=claim.id if claim else (report.id if report else f.id),
                claim_number=claim.claim_number if claim else (report.report_code if report else "DMG-2026-MOCK"),
                farmer_name=farmer.user.full_name if (farmer and farmer.user) else "SHIVAM SINGH",
                farm_code=farm.farm_code if farm else "FARM-MP-SEH-001",
                district=farmer.district if farmer else "Sehore",
                overall_fraud_risk=f.overall_fraud_risk,
                fraud_risk_score=f.fraud_risk_score,
                geofence_status=f.geofence_status,
                distance_to_boundary_meters=f.distance_to_boundary_meters,
                duplicate_image_flag=f.duplicate_image_flag,
                min_phash_hamming_distance=f.min_phash_hamming_distance,
                baseline_match_score=f.baseline_match_score,
                flag_reasons=f.flag_reasons or [],
                resolution_status=f.resolution_status or "UNRESOLVED",
                resolution_notes=f.resolution_notes,
                created_at=f.created_at,
            )
        )

    summary = FraudRadarSummary(
        total_flagged_evidence=len(fraud_checks),
        high_risk_count=high,
        medium_risk_count=med,
        low_risk_count=low,
        geofence_breach_count=geofence_breaches,
        duplicate_phash_count=duplicate_phashes,
        unresolved_count=unresolved,
        items=items,
    )
    return APIResponse(success=True, data=summary)


# 3. Fraud Override Action API
@router.patch("/fraud-checks/{evidence_id}/override", response_model=APIResponse[dict])
def override_fraud_check(
    evidence_id: str,
    payload: FraudOverrideRequest,
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    fraud_check = db.query(FraudCheck).filter(FraudCheck.evidence_id == evidence_id).first()
    if not fraud_check:
        # Fallback search by fraud_check.id
        fraud_check = db.query(FraudCheck).filter(FraudCheck.id == evidence_id).first()

    if not fraud_check:
        raise HTTPException(status_code=404, detail="Fraud check record not found")

    old_risk = fraud_check.overall_fraud_risk
    fraud_check.overall_fraud_risk = payload.new_risk_level.upper()
    fraud_check.resolved_by_user_id = current_user.id
    fraud_check.resolution_status = "OVERRIDDEN_CLEARED" if payload.new_risk_level.upper() == "LOW" else "RESOLVED"
    fraud_check.resolution_notes = payload.justification_notes
    fraud_check.resolved_at = datetime.now(timezone.utc)

    # Audit log entry
    audit = AuditLog(
        user_id=current_user.id,
        action="FRAUD_RISK_OVERRIDE",
        resource_type="FraudCheck",
        resource_id=fraud_check.id,
        details={
            "old_risk": old_risk,
            "new_risk": payload.new_risk_level,
            "justification": payload.justification_notes,
            "admin_user": current_user.username,
        },
    )
    db.add(audit)
    db.commit()

    return APIResponse(
        success=True,
        data={
            "message": f"Fraud risk override recorded from {old_risk} to {payload.new_risk_level.upper()}.",
            "evidence_id": evidence_id,
            "new_risk": payload.new_risk_level.upper(),
        },
    )


# 4. Claim Administrative Hold / Release API
@router.patch("/claims/{claim_id}/hold", response_model=APIResponse[dict])
def toggle_claim_administrative_hold(
    claim_id: str,
    payload: ClaimHoldRequest,
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    claim = db.query(Claim).filter(Claim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=404, detail="Claim record not found")

    old_status = claim.status
    if payload.action.upper() == "HOLD":
        claim.status = "ADMIN_HOLD"
        msg = f"Administrative freeze placed by Nodal Admin ({current_user.full_name}): {payload.reason_notes}"
    else:
        claim.status = "OFFICER_REVIEW"
        msg = f"Administrative hold released by Nodal Admin ({current_user.full_name}): {payload.reason_notes}"

    event = ClaimEvent(
        claim_id=claim.id,
        event_type=f"ADMIN_HOLD_{payload.action.upper()}",
        actor_role="ADMIN",
        actor_id=current_user.id,
        message=msg,
    )
    db.add(event)

    audit = AuditLog(
        user_id=current_user.id,
        action=f"CLAIM_ADMIN_{payload.action.upper()}",
        resource_type="Claim",
        resource_id=claim.id,
        details={"old_status": old_status, "new_status": claim.status, "reason": payload.reason_notes},
    )
    db.add(audit)
    db.commit()

    return APIResponse(
        success=True,
        data={
            "claim_id": claim.id,
            "status": claim.status,
            "message": msg,
        },
    )


# 5. User Activation / Deactivation API (Self-deactivation prevented)
@router.patch("/users/{user_id}/status", response_model=APIResponse[dict])
def update_user_status(
    user_id: str,
    payload: UserStatusUpdate,
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    if current_user.id == user_id and not payload.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Administrators cannot deactivate their own active session account.",
        )

    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User account not found")

    old_status = target_user.is_active
    target_user.is_active = payload.is_active

    audit = AuditLog(
        user_id=current_user.id,
        action="USER_STATUS_CHANGE",
        resource_type="User",
        resource_id=target_user.id,
        details={
            "target_username": target_user.username,
            "old_active": old_status,
            "new_active": payload.is_active,
            "reason": payload.reason,
        },
    )
    db.add(audit)
    db.commit()

    action_label = "ACTIVATED" if payload.is_active else "SUSPENDED"
    return APIResponse(
        success=True,
        data={
            "user_id": target_user.id,
            "username": target_user.username,
            "is_active": target_user.is_active,
            "message": f"User account '{target_user.username}' successfully {action_label}.",
        },
    )


# 6. User Role & Jurisdiction Assignment API
@router.patch("/users/{user_id}/role", response_model=APIResponse[dict])
def update_user_role_and_scope(
    user_id: str,
    payload: UserRoleUpdate,
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User account not found")

    role_map = {
        "FARMER": UserRole.FARMER,
        "FIELD_OFFICER": UserRole.FIELD_OFFICER,
        "INSURER": UserRole.INSURER,
        "SUPER_ADMIN": UserRole.SUPER_ADMIN,
        "ADMIN": UserRole.SUPER_ADMIN,
    }

    old_role = target_user.role.value if isinstance(target_user.role, UserRole) else str(target_user.role)
    new_role_enum = role_map.get(payload.role.upper(), UserRole.FARMER)
    target_user.role = new_role_enum

    # If updating Field Officer, update officer jurisdiction
    if new_role_enum == UserRole.FIELD_OFFICER and target_user.officer_profile:
        if payload.assigned_state:
            target_user.officer_profile.assigned_state = payload.assigned_state
        if payload.assigned_district:
            target_user.officer_profile.assigned_district = payload.assigned_district

    audit = AuditLog(
        user_id=current_user.id,
        action="USER_ROLE_CHANGE",
        resource_type="User",
        resource_id=target_user.id,
        details={
            "target_username": target_user.username,
            "old_role": old_role,
            "new_role": payload.role.upper(),
            "reason": payload.reason,
        },
    )
    db.add(audit)
    db.commit()

    return APIResponse(
        success=True,
        data={
            "user_id": target_user.id,
            "username": target_user.username,
            "role": target_user.role.value if isinstance(target_user.role, UserRole) else str(target_user.role),
            "message": f"User role for '{target_user.username}' updated to {payload.role.upper()}.",
        },
    )


# 7. Audit Log Viewer API
@router.get("/audit-logs", response_model=APIResponse[List[AuditLogRead]])
def list_audit_logs(
    limit: int = 50,
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return APIResponse(success=True, data=logs)


# 8. System Settings Reader & Editor API
@router.get("/settings", response_model=APIResponse[List[SystemSettingRead]])
def list_system_settings(
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    settings = db.query(SystemSetting).all()
    if not settings:
        # Seed default settings if empty
        defaults = [
            SystemSetting(key="PHASH_HAMMING_THRESHOLD", value="12", description="Maximum pHash distance for duplicate detection"),
            SystemSetting(key="LOCALIZED_CLAIM_THRESHOLD_PCT", value="15.0", description="Minimum percentage damage required for localized payout"),
            SystemSetting(key="SIFT_FEATURE_MATCH_THRESHOLD", value="0.75", description="Minimum baseline visual landmark correlation score"),
        ]
        db.add_all(defaults)
        db.commit()
        settings = db.query(SystemSetting).all()

    return APIResponse(success=True, data=settings)


@router.put("/settings/{setting_key}", response_model=APIResponse[SystemSettingRead])
def update_system_setting(
    setting_key: str,
    payload: SystemSettingUpdate,
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    setting = db.query(SystemSetting).filter(SystemSetting.key == setting_key).first()
    if not setting:
        setting = SystemSetting(key=setting_key, value=payload.value, description="Custom admin setting")
        db.add(setting)

    old_val = setting.value
    setting.value = payload.value

    audit = AuditLog(
        user_id=current_user.id,
        action="SYSTEM_SETTING_UPDATE",
        resource_type="SystemSetting",
        resource_id=setting.id,
        details={"key": setting_key, "old_value": old_val, "new_value": payload.value, "reason": payload.reason},
    )
    db.add(audit)
    db.commit()
    db.refresh(setting)

    return APIResponse(success=True, data=setting)


# 9. District Summary & Intelligence APIs
@router.get("/districts", response_model=APIResponse[List[DistrictSummaryRead]])
def list_district_summaries(
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    # Collect all unique districts from Farmers, Officers, and Disasters
    farmer_districts = [d[0] for d in db.query(Farmer.district).distinct().all() if d[0]]
    officer_districts = [d[0] for d in db.query(Officer.assigned_district).distinct().all() if d[0]]
    disaster_districts = [d[0] for d in db.query(DisasterEvent.district).distinct().all() if d[0]]
    
    all_districts = sorted(list(set(farmer_districts + officer_districts + disaster_districts)))
    if not all_districts:
        all_districts = ["Sehore", "Bhopal", "Dewas", "Ujjain"]

    summaries = []
    for d_name in all_districts:
        farmers = db.query(Farmer).filter(Farmer.district.ilike(d_name)).all()
        farmer_ids = [f.id for f in farmers]
        
        farms = db.query(Farm).filter(Farm.farmer_id.in_(farmer_ids)).all() if farmer_ids else []
        farm_ids = [fm.id for fm in farms]
        
        claims = db.query(Claim).filter(Claim.farmer_id.in_(farmer_ids)).all() if farmer_ids else []
        
        pending_claims = len([c for c in claims if c.status in ["SUBMITTED", "VALIDATING", "AI_ASSESSED", "OFFICER_REVIEW", "VERIFICATION_REQUIRED", "ADMIN_HOLD"]])
        approved_claims = len([c for c in claims if c.status == "APPROVED"])
        rejected_claims = len([c for c in claims if c.status == "REJECTED"])
        high_risk_claims = len([c for c in claims if c.ai_fraud_risk == "HIGH"])
        
        total_claimed = sum(c.estimated_payout_amount for c in claims)
        total_sanctioned = sum(c.final_sanctioned_amount or 0.0 for c in claims)

        active_officers = db.query(Officer).filter(Officer.assigned_district.ilike(d_name)).count()
        disaster_events = db.query(DisasterEvent).filter(DisasterEvent.district.ilike(d_name)).count()

        summaries.append(
            DistrictSummaryRead(
                district=d_name,
                total_farmers=len(farmers),
                total_farms=len(farms),
                total_claims=len(claims),
                pending_claims=pending_claims,
                approved_claims=approved_claims,
                rejected_claims=rejected_claims,
                high_risk_claims=high_risk_claims,
                active_officers=active_officers,
                disaster_events=disaster_events,
                total_claimed_amount=total_claimed,
                total_sanctioned_amount=total_sanctioned,
            )
        )

    return APIResponse(success=True, data=summaries)


@router.get("/districts/{district_name}", response_model=APIResponse[DistrictDetailRead])
def get_district_details(
    district_name: str,
    current_user: User = Depends(require_roles(["admin", "super_admin"])),
    db: Session = Depends(get_db),
):
    farmers = db.query(Farmer).filter(Farmer.district.ilike(district_name)).all()
    farmer_ids = [f.id for f in farmers]
    
    farms = db.query(Farm).filter(Farm.farmer_id.in_(farmer_ids)).all() if farmer_ids else []
    total_hectares = sum(fm.area_hectares for fm in farms)
    
    claims = db.query(Claim).filter(Claim.farmer_id.in_(farmer_ids)).all() if farmer_ids else []
    
    breakdown: Dict[str, int] = {}
    for c in claims:
        breakdown[c.status] = breakdown.get(c.status, 0) + 1

    pending_claims = len([c for c in claims if c.status in ["SUBMITTED", "VALIDATING", "AI_ASSESSED", "OFFICER_REVIEW", "VERIFICATION_REQUIRED", "ADMIN_HOLD"]])
    approved_claims = len([c for c in claims if c.status == "APPROVED"])
    rejected_claims = len([c for c in claims if c.status == "REJECTED"])
    high_risk_claims = len([c for c in claims if c.ai_fraud_risk == "HIGH"])
    
    total_est_loss = sum(c.estimated_payout_amount for c in claims)
    total_sanctioned = sum(c.final_sanctioned_amount or 0.0 for c in claims)
    
    active_officers = db.query(Officer).filter(Officer.assigned_district.ilike(district_name)).count()
    disaster_events = db.query(DisasterEvent).filter(DisasterEvent.district.ilike(district_name)).count()
    recent_audit_count = db.query(AuditLog).count()

    if not farmers and not claims and not active_officers and not disaster_events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No administrative records found for district '{district_name}'.",
        )

    detail = DistrictDetailRead(
        district=district_name.capitalize(),
        total_farmers=len(farmers),
        total_farms=len(farms),
        total_hectares=round(total_hectares, 2),
        total_claims=len(claims),
        pending_claims=pending_claims,
        approved_claims=approved_claims,
        rejected_claims=rejected_claims,
        high_risk_claims=high_risk_claims,
        total_est_loss_inr=total_est_loss,
        total_sanctioned_payout_inr=total_sanctioned,
        active_officers=active_officers,
        disaster_events=disaster_events,
        recent_audit_count=recent_audit_count,
        claim_status_breakdown=breakdown,
    )

    return APIResponse(success=True, data=detail)


