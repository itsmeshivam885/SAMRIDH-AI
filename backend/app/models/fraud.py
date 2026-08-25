import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class FraudCheck(Base):
    __tablename__ = "fraud_checks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    evidence_id = Column(String(36), ForeignKey("damage_evidence.id"), unique=True, nullable=False)
    
    # 1. Geofence Signal
    is_inside_geofence = Column(Boolean, default=True)
    distance_to_boundary_meters = Column(Float, default=0.0)
    geofence_status = Column(String(30), default="INSIDE") # INSIDE, OUTSIDE, BORDERLINE
    
    # 2. Perceptual Duplicate Hash Signal
    duplicate_image_flag = Column(Boolean, default=False)
    min_phash_hamming_distance = Column(Float, default=24.0)
    matched_duplicate_evidence_id = Column(String(36), nullable=True)
    
    # 3. Baseline Consistency Signal
    baseline_match_score = Column(Float, default=0.88) # SIFT/ORB keypoint ratio
    landmarks_aligned = Column(Boolean, default=True)
    
    # 4. Temporal / Metadata Check
    temporal_consistency_score = Column(Float, default=0.95)
    
    # Multi-Signal Synthesis
    overall_fraud_risk = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH
    fraud_risk_score = Column(Float, default=0.08)          # 0.0 (Clean) to 1.0 (Definite Fraud Flag)
    flag_reasons = Column(JSON, default=list)
    requires_manual_audit = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)

    evidence = relationship("DamageEvidence", back_populates="fraud_check")
