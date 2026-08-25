import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class Officer(Base):
    __tablename__ = "officers"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), unique=True, nullable=False)
    officer_badge_number = Column(String(50), unique=True, nullable=False, index=True)
    designation = Column(String(100), default="District Agricultural Loss Assessor")
    assigned_state = Column(String(100), nullable=False)
    assigned_district = Column(String(100), nullable=False)
    assigned_tehsil = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    user = relationship("User", back_populates="officer_profile")
    assigned_claims = relationship("Claim", back_populates="assigned_officer")
    field_verifications = relationship("FieldVerification", back_populates="officer")


class FieldVerification(Base):
    __tablename__ = "field_verifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=False, index=True)
    officer_id = Column(String(36), ForeignKey("officers.id"), nullable=False, index=True)
    scheduled_date = Column(DateTime, default=get_utc_now)
    conducted_date = Column(DateTime, nullable=True)
    status = Column(String(50), default="PENDING") # PENDING, IN_PROGRESS, COMPLETED
    
    # Ground inspection findings
    ground_damage_percentage = Column(Float, nullable=True)
    verified_gps_lat = Column(Float, nullable=True)
    verified_gps_lon = Column(Float, nullable=True)
    field_photos = Column(JSON, default=list)
    officer_notes = Column(Text, nullable=True)
    discrepancy_found = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)

    claim = relationship("Claim", back_populates="verifications")
    officer = relationship("Officer", back_populates="field_verifications")
