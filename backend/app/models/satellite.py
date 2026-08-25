import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class SatelliteObservation(Base):
    __tablename__ = "satellite_observations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    satellite_source = Column(String(50), default="Sentinel-2 MSI / ISRO Bhuvan")
    acquisition_date = Column(DateTime, default=get_utc_now, index=True)
    cloud_cover_percentage = Column(Float, default=5.0)
    resolution_meters = Column(Float, default=10.0)
    
    # Vegetation Indices
    mean_ndvi = Column(Float, nullable=False)     # Normalized Difference Vegetation Index (-1 to +1)
    min_ndvi = Column(Float, nullable=True)
    max_ndvi = Column(Float, nullable=True)
    mean_ndwi = Column(Float, nullable=True)     # Normalized Difference Water Index
    mean_evi = Column(Float, nullable=True)      # Enhanced Vegetation Index
    
    # Anomaly tracking against historical baseline
    vegetation_health_status = Column(String(50), default="HEALTHY_CANOPY")  # HEALTHY, MODERATE_VIGOR, SUDDEN_DROP, ANOMALY
    anomaly_detected = Column(Boolean, default=False)
    change_rate_percent = Column(Float, default=0.0)  # e.g. -25.4% drop in 7 days
    raw_tile_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)


class NDVIRecord(Base):
    __tablename__ = "ndvi_records"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    ndvi_value = Column(Float, nullable=False)
    historical_avg_ndvi = Column(Float, nullable=False)
    status = Column(String(50), default="NORMAL")
    created_at = Column(DateTime, default=get_utc_now)
