import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class BaselineRecord(Base):
    __tablename__ = "baseline_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    crop_id = Column(String(36), ForeignKey("farm_crops.id"), nullable=True)
    recorded_at = Column(DateTime, default=get_utc_now)
    growth_stage = Column(String(50), default="Germination / Early Vegetative")
    canopy_density_score = Column(Float, default=85.0)  # 0 to 100
    notes = Column(Text, nullable=True)
    verified_by_officer = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)

    farm = relationship("Farm", back_populates="baselines")
    crop = relationship("FarmCrop", back_populates="baselines")
    images = relationship("BaselineImage", back_populates="baseline", cascade="all, delete-orphan")


class BaselineImage(Base):
    __tablename__ = "baseline_images"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    baseline_id = Column(String(36), ForeignKey("baseline_records.id"), nullable=False, index=True)
    file_path = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA-256
    phash = Column(String(64), nullable=True)       # Perceptual hash
    gps_latitude = Column(Float, nullable=False)
    gps_longitude = Column(Float, nullable=False)
    captured_at = Column(DateTime, default=get_utc_now)
    view_angle = Column(String(50), default="North-Facing Panoramic")  # North, South, Field Center, Landmark Tree/Well
    landmarks_detected = Column(JSON, default=list) # e.g. ["tube_well_corner", "shed_east", "tree_north"]
    created_at = Column(DateTime, default=get_utc_now)

    baseline = relationship("BaselineRecord", back_populates="images")
