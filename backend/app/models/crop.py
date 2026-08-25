import uuid
from datetime import datetime, date, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Date, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class CropSeason(Base):
    __tablename__ = "crop_seasons"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), nullable=False)  # Kharif 2026, Rabi 2026-27, Zaid 2026
    season_type = Column(String(20), nullable=False)  # Kharif, Rabi, Zaid
    year = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)


class FarmCrop(Base):
    __tablename__ = "farm_crops"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    crop_name = Column(String(100), nullable=False, index=True)  # Soybean, Wheat, Paddy, Cotton, Mustard
    variety = Column(String(100), default="JS-9560 / High Yield Hybrid")
    season = Column(String(50), default="Kharif 2026")
    sowing_date = Column(Date, nullable=False)
    expected_harvest_date = Column(Date, nullable=True)
    current_growth_stage = Column(String(50), default="Vegetative / Flowering")  # Germination, Vegetative, Flowering, Podding, Maturity, Harvest
    notified_sum_insured_per_ha = Column(Float, default=48000.0)  # INR/ha standard PMFBY scale
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    farm = relationship("Farm", back_populates="crops")
    baselines = relationship("BaselineRecord", back_populates="crop", cascade="all, delete-orphan")
