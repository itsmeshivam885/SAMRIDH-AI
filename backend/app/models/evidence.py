import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class DamageEvidence(Base):
    __tablename__ = "damage_evidence"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    damage_report_id = Column(String(36), ForeignKey("damage_reports.id"), nullable=False, index=True)
    file_path = Column(String(255), nullable=False)
    file_name = Column(String(255), nullable=False)
    mime_type = Column(String(50), default="image/jpeg")
    file_size_bytes = Column(Float, nullable=False)
    file_sha256 = Column(String(64), nullable=False, index=True)
    phash = Column(String(64), nullable=True, index=True)
    
    # Metadata extracted at submission
    gps_latitude = Column(Float, nullable=False)
    gps_longitude = Column(Float, nullable=False)
    gps_accuracy_meters = Column(Float, default=5.0)
    device_model = Column(String(100), nullable=True)
    captured_at = Column(DateTime, default=get_utc_now)
    uploaded_at = Column(DateTime, default=get_utc_now)
    is_primary = Column(Boolean, default=True)

    damage_report = relationship("DamageReport", back_populates="evidence_items")
    validation = relationship("EvidenceValidation", back_populates="evidence", uselist=False, cascade="all, delete-orphan")
    fraud_check = relationship("FraudCheck", back_populates="evidence", uselist=False, cascade="all, delete-orphan")


class EvidenceValidation(Base):
    __tablename__ = "evidence_validation"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    evidence_id = Column(String(36), ForeignKey("damage_evidence.id"), unique=True, nullable=False)
    
    # Quality Gate parameters
    blur_score = Column(Float, nullable=False) # Laplacian variance
    is_blurry = Column(Boolean, default=False)
    mean_luminance = Column(Float, nullable=False)
    is_exposure_acceptable = Column(Boolean, default=True)
    resolution_width = Column(Float, nullable=False)
    resolution_height = Column(Float, nullable=False)
    passed_quality_gate = Column(Boolean, default=True)
    validation_remarks = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    evidence = relationship("DamageEvidence", back_populates="validation")
