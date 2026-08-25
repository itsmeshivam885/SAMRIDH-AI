import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class SoilSensor(Base):
    __tablename__ = "soil_sensors"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    device_id = Column(String(100), unique=True, nullable=False, index=True)  # e.g., ESP32-SOIL-MP-001
    model_type = Column(String(100), default="TwinBit SoilNode Pro (NPK+EC+pH)")
    installation_date = Column(DateTime, default=get_utc_now)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    depth_cm = Column(Float, default=15.0)  # sensor probe depth
    battery_level_percent = Column(Float, default=95.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    farm = relationship("Farm", back_populates="sensors")
    readings = relationship("SoilReading", back_populates="sensor", cascade="all, delete-orphan")


class SoilReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    sensor_id = Column(String(36), ForeignKey("soil_sensors.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=get_utc_now, index=True)
    
    # Agronomic metrics
    soil_moisture_percent = Column(Float, nullable=False)   # Ideal: 40-70% for Soybean/Paddy
    soil_temperature_celsius = Column(Float, nullable=False) # Soil root zone temp
    nitrogen_mg_kg = Column(Float, nullable=True)           # N (Available)
    phosphorus_mg_kg = Column(Float, nullable=True)         # P
    potassium_mg_kg = Column(Float, nullable=True)          # K
    ph_level = Column(Float, nullable=True)                 # Soil pH (6.5 - 7.5)
    electrical_conductivity_us_cm = Column(Float, nullable=True) # Salinity / EC (uS/cm)
    
    # Computed risk indicators
    water_stress_index = Column(Float, default=0.0)         # 0.0 (Optimal) to 1.0 (Critical Drought Stress)
    nutrient_stress_flag = Column(Boolean, default=False)
    status_label = Column(String(50), default="OPTIMAL")    # OPTIMAL, WATER_DEFICIT, WATERLOGGED, NUTRIENT_LOW
    created_at = Column(DateTime, default=get_utc_now)

    sensor = relationship("SoilSensor", back_populates="readings")
