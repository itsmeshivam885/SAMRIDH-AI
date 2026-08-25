import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class Advisory(Base):
    __tablename__ = "advisories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    farm_id = Column(String(36), ForeignKey("farms.id"), nullable=False, index=True)
    category = Column(String(50), default="IRRIGATION") # IRRIGATION, PEST_CONTROL, NUTRIENT, WEATHER_ALERT, HARVEST
    priority = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, URGENT
    title = Column(String(200), nullable=False)
    title_hi = Column(String(200), nullable=True) # Hindi translation for farmer
    message = Column(Text, nullable=False)
    message_hi = Column(Text, nullable=True)
    reasoning = Column(JSON, default=dict) # Evidence streams backing this advisory
    action_items = Column(JSON, default=list) # Concrete steps for farmer
    is_read = Column(Boolean, default=False)
    generated_at = Column(DateTime, default=get_utc_now)


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), default="INFO") # CLAIM_UPDATE, ADVISORY, DISASTER_WARNING, SYSTEM
    link_url = Column(String(255), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=get_utc_now)


class Grievance(Base):
    __tablename__ = "grievances"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    ticket_id = Column(String(50), unique=True, nullable=False, index=True) # e.g. TKT-2026-0041
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    claim_id = Column(String(36), ForeignKey("claims.id"), nullable=True)
    category = Column(String(50), default="CLAIM_DISPUTE") # DELAYED_PAYOUT, REJECTION_APPEAL, SENSOR_ISSUE, GENERAL
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="OPEN") # OPEN, UNDER_INVESTIGATION, RESOLVED, CLOSED
    officer_reply = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    resolved_at = Column(DateTime, nullable=True)
