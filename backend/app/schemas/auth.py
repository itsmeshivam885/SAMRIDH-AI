from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime


class LoginRequest(BaseModel):
    username_or_phone: str
    password: str


class OTPRequest(BaseModel):
    phone_number: str


class OTPVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    full_name: str
    role: str
    preferred_language: str = "en"
    farmer_id: Optional[str] = None
    officer_id: Optional[str] = None


class UserCreate(BaseModel):
    username: str
    phone_number: str
    full_name: str
    password: str
    email: Optional[str] = None
    role: str = "farmer"
    preferred_language: str = "en"


class UserRead(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    phone_number: str
    full_name: str
    role: str
    preferred_language: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
