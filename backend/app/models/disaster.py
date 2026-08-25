import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class DisasterEvent(Base):
    __tablename__ = "disaster_events"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    disaster_type = Column(String(50), nullable=False, index=True)  # FLOOD, HAILSTORM, UNSEASONAL_RAIN, DROUGHT, PEST_ATTACK, FIRE, CYCLONE
    state = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=False, index=True)
    tehsil = Column(String(100), nullable=True)
    event_start_date = Column(DateTime, default=get_utc_now)
    event_end_date = Column(DateTime, nullable=True)
    severity = Column(String(20), default="SEVERE")  # MODERATE, SEVERE, CATASTROPHIC
    estimated_affected_area_ha = Column(Float, default=1250.0)
    official_notification_number = Column(String(100), nullable=True)
    pmfby_notified = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    damage_reports = relationship("DamageReport", back_populates="disaster_event")
