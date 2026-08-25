import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.claim import Claim, ClaimEvent, ClaimDocument
from app.models.damage import DamageReport, DamageAssessment
from app.models.farm import Farm
from app.models.farmer import Farmer
from app.models.officer import Officer
from app.models.audit import AuditLog
from app.schemas.damage import DamageReportCreate
from app.schemas.claim import ClaimReviewAction, SettlementStatusUpdate
from app.integrations.pmfby.mock import pmfby_adapter
from app.integrations.satellite.mock import satellite_provider
from app.integrations.weather.mock import weather_provider
from app.ai.risk_prediction import risk_prediction_ai


class ClaimService:
    def create_damage_report(self, db: Session, farmer_id: str, payload: DamageReportCreate) -> DamageReport:
        count = db.query(DamageReport).count() + 1
        report_code = f"DMG-2026-{count:04d}"

        report = DamageReport(
            farm_id=payload.farm_id,
            disaster_event_id=payload.disaster_event_id,
            report_code=report_code,
            loss_category=payload.loss_category,
            farmer_reported_loss_percentage=payload.farmer_reported_loss_percentage,
            description=payload.description,
            incident_date=payload.incident_date or datetime.now(timezone.utc),
            status="SUBMITTED",
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    def create_claim_from_damage_report(self, db: Session, damage_report_id: str) -> Claim:
        report = db.query(DamageReport).filter(DamageReport.id == damage_report_id).first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "REPORT_NOT_FOUND", "message": "Damage report not found"})

        farm = db.query(Farm).filter(Farm.id == report.farm_id).first()
        farmer = farm.farmer if farm else None

        # Check assessment
        assessment = report.assessment
        damage_pct = assessment.damage_percentage if assessment else report.farmer_reported_loss_percentage
        visual_conf = assessment.confidence_score if assessment else 0.85

        # Cross-reference with satellite & weather
        sat_obs = satellite_provider.get_latest_observation(farm.id, farm.center_latitude, farm.center_longitude)
        weath_obs = weather_provider.get_current_weather(farm.center_latitude, farm.center_longitude)

        # Multi-modal fusion
        fused = risk_prediction_ai.compute_multimodal_claim_confidence(
            visual_damage_percentage=damage_pct,
            visual_confidence=visual_conf,
            satellite_anomaly=sat_obs.get("anomaly_detected", True),
            satellite_drop_percentage=sat_obs.get("change_rate_percent", -25.0),
            weather_hazard_level=weath_obs.get("flood_risk_level", "HIGH"),
            fraud_risk_score=0.08,
        )

        # PMFBY Payout Estimate
        payout_calc = pmfby_adapter.calculate_estimated_payout(
            sum_insured_per_ha=48000.0,
            farm_area_ha=farm.area_hectares,
            damage_percentage=damage_pct,
            loss_category=report.loss_category,
        )

        claim_count = db.query(Claim).count() + 1
        claim_number = f"PMFBY-CLAIM-2026-MP-{claim_count:04d}"

        claim = Claim(
            claim_number=claim_number,
            damage_report_id=report.id,
            farm_id=farm.id,
            farmer_id=farmer.id if farmer else "unknown",
            crop_season_name="Kharif 2026",
            ai_damage_percentage=damage_pct,
            ai_confidence_score=fused["fused_confidence_score"],
            ai_fraud_risk="LOW",
            estimated_payout_amount=payout_calc["estimated_payout_inr"],
            status="OFFICER_REVIEW",
            pmfby_application_id=f"PMFBY-APP-{uuid.uuid4().hex[:8].upper()}",
        )
        db.add(claim)
        db.flush()

        # Add initial timeline event
        event1 = ClaimEvent(
            claim_id=claim.id,
            event_type="CLAIM_INITIATED",
            actor_role="FARMER",
            actor_id=farmer.user_id if farmer else None,
            message=f"Claim intimation initiated by farmer for {report.loss_category} damage ({report.farmer_reported_loss_percentage}% claimed).",
        )
        event2 = ClaimEvent(
            claim_id=claim.id,
            event_type="AI_MULTIMODAL_ASSESSMENT_COMPLETED",
            actor_role="SYSTEM",
            message=f"AI Computer Vision + Sentinel-2 NDVI + IMD Weather fused assessment: {damage_pct}% loss (Confidence: {fused['fused_confidence_score'] * 100:.0f}%).",
        )
        db.add(event1)
        db.add(event2)

        report.status = "CLAIM_CREATED"
        db.commit()
        db.refresh(claim)
        return claim

    def review_claim_by_officer(
        self,
        db: Session,
        claim_id: str,
        officer: Officer,
        action: ClaimReviewAction
    ) -> Claim:
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "CLAIM_NOT_FOUND", "message": "Claim not found"})

        claim.assigned_officer_id = officer.id
        claim.officer_decision = action.decision
        claim.officer_reviewed_at = datetime.now(timezone.utc)
        claim.officer_remarks = action.remarks

        if action.decision == "APPROVED":
            claim.status = "APPROVED"
            claim.approved_loss_percentage = action.approved_loss_percentage or claim.ai_damage_percentage
            claim.final_sanctioned_amount = action.sanctioned_payout_amount or claim.estimated_payout_amount
            claim.settlement_status = "PROCESSED_FOR_DBT"
            msg = f"Claim approved by Officer {officer.officer_badge_number} with sanctioned amount of ₹{claim.final_sanctioned_amount:,.2f}."
        elif action.decision == "REJECTED":
            claim.status = "REJECTED"
            msg = f"Claim rejected by Officer: {action.remarks}"
        elif action.decision == "FIELD_VERIFICATION_REQUESTED":
            claim.status = "VERIFICATION_REQUIRED"
            msg = f"Officer requested on-site field verification: {action.remarks}"
        else:
            claim.status = "MORE_EVIDENCE_REQUESTED"
            msg = f"Additional ground evidence requested by Officer: {action.remarks}"

        event = ClaimEvent(
            claim_id=claim.id,
            event_type=f"OFFICER_{action.decision}",
            actor_role="OFFICER",
            actor_id=officer.user_id,
            message=msg,
        )
        db.add(event)

        audit = AuditLog(
            user_id=officer.user_id,
            action="OFFICER_CLAIM_DECISION",
            resource_type="Claim",
            resource_id=claim.id,
            details={"decision": action.decision, "sanctioned_amount": claim.final_sanctioned_amount},
        )
        db.add(audit)

        db.commit()
        db.refresh(claim)
        return claim

    def get_all_claims(
        self,
        db: Session,
        status_filter: Optional[str] = None,
        district_filter: Optional[str] = None
    ) -> List[Claim]:
        query = db.query(Claim)
        if status_filter:
            query = query.filter(Claim.status == status_filter)
        return query.order_by(Claim.created_at.desc()).all()


claim_service = ClaimService()
