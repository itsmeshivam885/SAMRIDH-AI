from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, Role
from app.models.farmer import Farmer
from app.models.officer import Officer
from app.models.audit import AuditLog
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.schemas.auth import LoginRequest, OTPRequest, OTPVerifyRequest, UserCreate, TokenResponse
from app.core.config import settings


class AuthService:
    def authenticate_user(self, db: Session, req: LoginRequest, ip_address: str = "127.0.0.1") -> TokenResponse:
        # Check by username or phone
        user = db.query(User).filter(
            (User.username == req.username_or_phone) | (User.phone_number == req.username_or_phone)
        ).first()

        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "INVALID_CREDENTIALS", "message": "Invalid username/phone or password"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "USER_INACTIVE", "message": "User account is disabled"},
            )

        # Audit log
        log = AuditLog(
            user_id=user.id,
            action="USER_LOGIN_PASSWORD",
            resource_type="User",
            resource_id=user.id,
            ip_address=ip_address,
            details={"role": user.role},
        )
        db.add(log)
        db.commit()

        return self._generate_token_response(db, user)

    def request_otp(self, req: OTPRequest) -> Dict[str, Any]:
        # In demo mode, returns success with hint
        return {
            "phone_number": req.phone_number,
            "otp_sent": True,
            "demo_otp_hint": settings.MOCK_OTP_CODE if settings.DEMO_MODE else None,
            "message": "OTP sent successfully to registered mobile number.",
        }

    def verify_otp_and_login(self, db: Session, req: OTPVerifyRequest, ip_address: str = "127.0.0.1") -> TokenResponse:
        if req.otp_code != settings.MOCK_OTP_CODE and req.otp_code != "123456":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_OTP", "message": "Invalid or expired OTP code"},
            )

        user = db.query(User).filter(User.phone_number == req.phone_number).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "USER_NOT_FOUND", "message": "No account registered with this phone number"},
            )

        log = AuditLog(
            user_id=user.id,
            action="USER_LOGIN_OTP",
            resource_type="User",
            resource_id=user.id,
            ip_address=ip_address,
            details={"role": user.role},
        )
        db.add(log)
        db.commit()

        return self._generate_token_response(db, user)

    def register_user(self, db: Session, req: UserCreate) -> TokenResponse:
        existing = db.query(User).filter(
            (User.username == req.username) | (User.phone_number == req.phone_number)
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "USER_EXISTS", "message": "Username or phone number is already registered"},
            )

        new_user = User(
            username=req.username,
            phone_number=req.phone_number,
            email=req.email,
            full_name=req.full_name,
            role=req.role,
            preferred_language=req.preferred_language,
            hashed_password=get_password_hash(req.password),
        )
        db.add(new_user)
        db.flush()

        # If registering as farmer, initialize farmer profile
        if req.role == "farmer":
            farmer = Farmer(
                user_id=new_user.id,
                farmer_id_code=f"FARMER-{new_user.id[:8].upper()}",
                state="Madhya Pradesh",
                district="Sehore",
                village="Ashta",
            )
            db.add(farmer)

        db.commit()
        db.refresh(new_user)

        return self._generate_token_response(db, new_user)

    def _generate_token_response(self, db: Session, user: User) -> TokenResponse:
        token_data = {
            "sub": user.id,
            "username": user.username,
            "role": user.role,
        }
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        farmer_id = user.farmer_profile.id if user.farmer_profile else None
        officer_id = user.officer_profile.id if user.officer_profile else None

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user_id=user.id,
            username=user.username,
            full_name=user.full_name,
            role=user.role,
            preferred_language=user.preferred_language,
            farmer_id=farmer_id,
            officer_id=officer_id,
        )


auth_service = AuthService()
