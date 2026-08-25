import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class DamageReport(Base):
    __tablename__ = "damage_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    disaster_event_id = Column(String(36), ForeignKey("disaster_events.id"), nullable=True)
    report_code = Column(String(50), unique=True, nullable=False, index=True) # e.g. DMG-2026-0081
    loss_category = Column(String(50), nullable=False) # FLOOD, LODGING, HAIL, DROUGHT, PEST, FIRE
    farmer_reported_loss_percentage = Column(Float, nullable=False)
    incident_date = Column(DateTime, default=get_utc_now)
    reported_at = Column(DateTime, default=get_utc_now)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="SUBMITTED") # SUBMITTED, VALIDATING, AI_ASSESSED, CLAIM_CREATED
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    farm = relationship("Farm", back_populates="damage_reports")
    disaster_event = relationship("DisasterEvent", back_populates="damage_reports")
    evidence_items = relationship("DamageEvidence", back_populates="damage_report", cascade="all, delete-orphan")
    assessment = relationship("DamageAssessment", back_populates="damage_report", uselist=False, cascade="all, delete-orphan")
    claim = relationship("Claim", back_populates="damage_report", uselist=False)


class DamageAssessment(Base):
    __tablename__ = "damage_assessments"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    damage_report_id = Column(String(36), ForeignKey("damage_reports.id"), unique=True, nullable=False)
    ai_model_name = Column(String(100), default="SAMRIDH-SegFormer-Agri-v2")
    ai_model_version = Column(String(20), default="2.1.0")
    
    # Pixel & Polygon Segmentation Metrics
    total_analyzed_area_px = Column(Float, nullable=False)
    healthy_canopy_area_px = Column(Float, nullable=False)
    damaged_area_px = Column(Float, nullable=False)
    damage_percentage = Column(Float, nullable=False) # e.g. 68.4%
    primary_damage_type = Column(String(50), nullable=False) # LODGING, SUBMERGED_FLOOD, HAIL_SHRED, SCORCHED
    confidence_score = Column(Float, nullable=False) # 0.0 - 1.0 (e.g., 0.93)
    
    # Mask & Geo Overlays
    segmentation_mask_url = Column(String(255), nullable=True)
    segment_breakdown = Column(JSON, default=dict) # {"lodged": 52.0, "submerged": 16.4, "healthy": 31.6}
    processing_time_ms = Column(Float, default=145.0)
    warnings = Column(JSON, default=list)
    created_at = Column(DateTime, default=get_utc_now)

    damage_report = relationship("DamageReport", back_populates="assessment")
