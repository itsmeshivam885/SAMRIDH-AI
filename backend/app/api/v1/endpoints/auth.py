from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, Token, UserResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

REDIRECT_MATRIX = {
    "FARMER": "/farmer/dashboard",
    "FIELD_OFFICER": "/officer/dashboard",
    "INSURER": "/insurer/dashboard",
    "SUPER_ADMIN": "/super-admin/dashboard",
}


@router.post("/login", response_model=Token)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with username and password.
    Returns JWT access token, role details, and dashboard redirect URL.
    """
    username_clean = req.username.strip().lower()
    user = db.query(User).filter(User.username == username_clean).first()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    role_str = user.role.value if isinstance(user.role, UserRole) else str(user.role)
    redirect_url = REDIRECT_MATRIX.get(role_str, "/farmer/dashboard")
    access_token = create_access_token(subject=user.id, role=role_str)

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        role=role_str,
        full_name=user.full_name,
        redirect_url=redirect_url,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    role_str = current_user.role.value if isinstance(current_user.role, UserRole) else str(current_user.role)
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        registration_no=current_user.registration_no,
        full_name=current_user.full_name,
        role=role_str,
    )
