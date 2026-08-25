import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    farmer_id_code = Column(String(50), unique=True, nullable=False, index=True)  # e.g., FARMER-MP-2026-001
    masked_aadhaar = Column(String(20), nullable=True)  # e.g. "XXXX-XXXX-1234" (Strictly masked for privacy)
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    tehsil = Column(String(100), nullable=True)
    village = Column(String(100), nullable=False, index=True)
    pincode = Column(String(10), nullable=True)
    pmfby_policy_number = Column(String(100), nullable=True, index=True)
    bank_account_masked = Column(String(30), nullable=True)
    ifsc_code = Column(String(20), nullable=True)
    extra_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="farmer_profile")
    farms = relationship("Farm", back_populates="farmer", cascade="all, delete-orphan")
