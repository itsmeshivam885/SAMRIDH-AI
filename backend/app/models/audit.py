import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class CropScan(Base):
    __tablename__ = "crop_scans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    image_url = Column(String(255), nullable=False)
    scan_type = Column(String(50), default="DISEASE_AND_STRESS") # DISEASE_AND_STRESS, PEST, WEED
    
    # AI Results
    health_score = Column(Float, default=85.0) # 0 to 100
    detected_condition = Column(String(100), default="Healthy Crop Canopy") # e.g. "Soybean Rust (Phakopsora pachyrhizi)", "Yellow Mosaic Virus"
    condition_category = Column(String(50), default="HEALTHY") # HEALTHY, FUNGAL, BACTERIAL, VIRAL, PEST, NUTRIENT_DEFICIENCY
    confidence = Column(Float, default=0.96)
    advisory_recommendation = Column(Text, nullable=True)
    advisory_recommendation_hi = Column(Text, nullable=True)
    treatment_type = Column(String(50), default="PREVENTIVE") # ORGANIC, BIO_FUNGICIDE, CHEMICAL_AUTHORIZED, MONITOR
    scanned_at = Column(DateTime, default=get_utc_now)

    farm = relationship("Farm", back_populates="crop_scans")


class AIModelRegistry(Base):
    __tablename__ = "ai_models"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), unique=True, nullable=False) # e.g. "SAMRIDH-YOLO-Pest-v11"
    task_type = Column(String(50), nullable=False) # CROP_DISEASE, DAMAGE_SEGMENTATION, SATELLITE_NDVI, FRAUD_DETECTION
    version = Column(String(20), nullable=False)
    framework = Column(String(50), default="PyTorch")
    is_active = Column(Boolean, default=True)
    is_demo_mock = Column(Boolean, default=True) # Reflects DEMO_MODE
    accuracy_metric = Column(String(50), default="mAP@0.5: 0.912 / F1: 0.89")
    created_at = Column(DateTime, default=get_utc_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True) # USER_LOGIN, CLAIM_FILED, OFFICER_DECISION, MODEL_TOGGLE
    resource_type = Column(String(50), nullable=False) # Claim, DamageReport, User, SystemSetting
    resource_id = Column(String(36), nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=get_utc_now, index=True)


class SystemSetting(Base):
    __tablename__ = "system_settings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)
