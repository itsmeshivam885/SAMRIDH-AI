from typing import Optional
from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    role: str
    full_name: str
    redirect_url: str


class UserResponse(BaseModel):
    id: str
    username: str
    registration_no: str
    full_name: str
    role: str

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Backward-compatible token response schema."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    full_name: str
    role: str
    redirect_url: Optional[str] = None
    preferred_language: str = "en"


class RegisterRequest(BaseModel):
    username: str
    full_name: str
    registration_no: str
    role: str = "FARMER"
    phone: Optional[str] = None
    email: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    stakeholder: Optional[str] = None
    category: Optional[str] = None
    designation: Optional[str] = None
    generated_password: Optional[str] = None


class RegisterResponse(BaseModel):
    success: bool
    username: str
    full_name: str
    role: str
    docket_no: str
    message: str
