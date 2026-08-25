import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_number = Column(String(50), unique=True, nullable=False, index=True) # e.g. PMFBY-CLAIM-2026-MP-0042
    damage_report_id = Column(String(36), ForeignKey("damage_reports.id"), unique=True, nullable=False)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    farmer_id = Column(String(36), ForeignKey("farmers.id"), nullable=False, index=True)
    crop_season_name = Column(String(50), default="Kharif 2026")
    
    # AI-Derived Metrics (Decision-Support Only)
    ai_damage_percentage = Column(Float, nullable=False)
    ai_confidence_score = Column(Float, nullable=False) # Multimodal fused confidence
    ai_fraud_risk = Column(String(20), default="LOW")
    estimated_payout_amount = Column(Float, nullable=False) # INR
    
    # Official PMFBY Status Tracking
    status = Column(
        String(50), 
        default="OFFICER_REVIEW", 
        index=True
    ) # DRAFT, SUBMITTED, VALIDATING, AI_ASSESSED, OFFICER_REVIEW, VERIFICATION_REQUIRED, APPROVED, REJECTED, SETTLED
    
    # Officer Review Action
    assigned_officer_id = Column(String(36), ForeignKey("officers.id"), nullable=True)
    officer_decision = Column(String(50), nullable=True) # APPROVED, REJECTED, FIELD_VERIFICATION_REQUESTED, MORE_EVIDENCE_REQUESTED
    officer_reviewed_at = Column(DateTime, nullable=True)
    officer_remarks = Column(Text, nullable=True)
    approved_loss_percentage = Column(Float, nullable=True)
    final_sanctioned_amount = Column(Float, nullable=True)
    
    # PMFBY / PFMS Settlement Adapter info
    pmfby_application_id = Column(String(100), nullable=True)
    pmfby_settlement_reference = Column(String(100), nullable=True)
    settlement_status = Column(String(50), default="PENDING_APPROVAL") # PENDING_APPROVAL, PROCESSED_FOR_DBT, DISBURSED
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    damage_report = relationship("DamageReport", back_populates="claim")
    farm = relationship("Farm", back_populates="claims")
    assigned_officer = relationship("Officer", back_populates="assigned_claims")
    events = relationship("ClaimEvent", back_populates="claim", cascade="all, delete-orphan")
    documents = relationship("ClaimDocument", back_populates="claim", cascade="all, delete-orphan")
    verifications = relationship("FieldVerification", back_populates="claim", cascade="all, delete-orphan")


class ClaimEvent(Base):
    __tablename__ = "claim_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False, index=True)
    event_type = Column(String(100), nullable=False) # CREATED, AI_ASSESSMENT_COMPLETED, OFFICER_ASSIGNED, OFFICER_APPROVED, DBT_INITIATED
    actor_role = Column(String(50), default="SYSTEM") # FARMER, SYSTEM, OFFICER, ADMIN
    actor_id = Column(String(36), nullable=True)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=get_utc_now)

    claim = relationship("Claim", back_populates="events")


class ClaimDocument(Base):
    __tablename__ = "claim_documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False, index=True)
    doc_type = Column(String(50), default="AI_ASSESSMENT_CERTIFICATE")
    file_path = Column(String(255), nullable=False)
    generated_at = Column(DateTime, default=get_utc_now)

    claim = relationship("Claim", back_populates="documents")
