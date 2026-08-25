import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class WeatherRecord(Base):
    __tablename__ = "weather_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=True, index=True)
    recorded_at = Column(DateTime, default=get_utc_now, index=True)
    source = Column(String(50), default="IMD / Regional Automatic Weather Station")
    
    temperature_celsius = Column(Float, nullable=False)
    relative_humidity_percent = Column(Float, nullable=False)
    rainfall_mm = Column(Float, default=0.0)
    wind_speed_kmh = Column(Float, default=10.0)
    precipitation_probability = Column(Float, default=20.0)
    weather_condition = Column(String(50), default="Clear / Partly Cloudy")
    
    # Aggregated hazard indices
    heat_stress_index = Column(Float, default=0.0)
    flood_risk_level = Column(String(20), default="LOW")      # LOW, MEDIUM, HIGH, EXTREME
    hail_risk_level = Column(String(20), default="LOW")
    drought_risk_level = Column(String(20), default="LOW")
    created_at = Column(DateTime, default=get_utc_now)


class WeatherAlert(Base):
    __tablename__ = "weather_alerts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    district = Column(String(100), nullable=False, index=True)
    state = Column(String(100), nullable=False)
    alert_type = Column(String(50), nullable=False)  # HEAVY_RAINFALL, HAILSTORM, HIGH_WIND, HEATWAVE, FROST
    severity = Column(String(20), nullable=False)    # YELLOW, ORANGE, RED
    headline = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    valid_from = Column(DateTime, default=get_utc_now)
    valid_until = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=get_utc_now)
