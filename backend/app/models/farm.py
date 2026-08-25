import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class Farm(Base):
    __tablename__ = "farms"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farmer_id = Column(String(36), ForeignKey("farmers.id"), nullable=False, index=True)
    farm_code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., FARM-001
    name = Column(String(150), nullable=False)
    survey_number = Column(String(100), nullable=True)  # Khasra / Khatauni number
    area_hectares = Column(Float, nullable=False)
    soil_type = Column(String(100), default="Black Cotton Soil")  # Alluvial, Red, Black, Sandy Loam, etc.
    irrigation_source = Column(String(100), default="Borewell")  # Canal, Borewell, Rainfed, Drip
    center_latitude = Column(Float, nullable=False)
    center_longitude = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    farmer = relationship("Farmer", back_populates="farms")
    boundary = relationship("FarmBoundary", back_populates="farm", uselist=False, cascade="all, delete-orphan")
    crops = relationship("FarmCrop", back_populates="farm", cascade="all, delete-orphan")
    sensors = relationship("SoilSensor", back_populates="farm", cascade="all, delete-orphan")
    baselines = relationship("BaselineRecord", back_populates="farm", cascade="all, delete-orphan")
    crop_scans = relationship("CropScan", back_populates="farm", cascade="all, delete-orphan")
    damage_reports = relationship("DamageReport", back_populates="farm", cascade="all, delete-orphan")
    claims = relationship("Claim", back_populates="farm", cascade="all, delete-orphan")


class FarmBoundary(Base):
    __tablename__ = "farm_boundaries"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), unique=True, nullable=False)
    # GeoJSON polygon representation: {"type": "Polygon", "coordinates": [[[lon, lat], ...]]}
    geojson = Column(JSON, nullable=False)
    perimeter_meters = Column(Float, nullable=True)
    calculated_area_hectares = Column(Float, nullable=True)
    verified_by_officer = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    farm = relationship("Farm", back_populates="boundary")
