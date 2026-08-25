import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def get_utc_now():
    return datetime.now(timezone.utc)


class Role(Base):
    __tablename__ = "roles"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(50), unique=True, nullable=False, index=True)  # farmer, officer, admin, super_admin
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    users = relationship("User", back_populates="role_rel")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(150), unique=True, nullable=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=False)
    role = Column(String(50), nullable=False, default="farmer", index=True)  # farmer, officer, admin, super_admin
    role_id = Column(String(36), ForeignKey("roles.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    preferred_language = Column(String(10), default="en")  # en, hi, mr, te, etc.
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    role_rel = relationship("Role", back_populates="users")
    farmer_profile = relationship("Farmer", back_populates="user", uselist=False)
    officer_profile = relationship("Officer", back_populates="user", uselist=False)
