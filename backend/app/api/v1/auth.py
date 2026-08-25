from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import LoginRequest, OTPRequest, OTPVerifyRequest, UserCreate, TokenResponse, UserRead
from app.schemas.common import APIResponse
from app.services.auth_service import auth_service
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(req: LoginRequest, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "127.0.0.1"
    token_resp = auth_service.authenticate_user(db, req, ip_address=ip)
    return APIResponse(success=True, data=token_resp)


@router.post("/otp/request", response_model=APIResponse[dict])
def request_otp(req: OTPRequest):
    resp = auth_service.request_otp(req)
    return APIResponse(success=True, data=resp)


@router.post("/otp/verify", response_model=APIResponse[TokenResponse])
def verify_otp(req: OTPVerifyRequest, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "127.0.0.1"
    token_resp = auth_service.verify_otp_and_login(db, req, ip_address=ip)
    return APIResponse(success=True, data=token_resp)


@router.post("/register", response_model=APIResponse[TokenResponse])
def register(req: UserCreate, db: Session = Depends(get_db)):
    token_resp = auth_service.register_user(db, req)
    return APIResponse(success=True, data=token_resp)


@router.get("/me", response_model=APIResponse[UserRead])
def get_me(current_user = Depends(get_current_user)):
    return APIResponse(success=True, data=current_user)
