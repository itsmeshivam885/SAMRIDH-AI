from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, get_password_hash
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, Token, UserResponse, RegisterRequest, RegisterResponse
from app.api.deps import get_current_user
import uuid, random, re
from datetime import datetime, timezone

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


@router.post("/register", response_model=RegisterResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new stakeholder user. Auto-generates username & password.
    Saves to PostgreSQL users table.
    """
    username_clean = req.username.strip().lower()

    # Prevent duplicate registrations
    existing = db.query(User).filter(User.username == username_clean).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{username_clean}' is already registered.",
        )

    # Map role string to UserRole enum
    role_map = {
        "FARMER": UserRole.FARMER,
        "FIELD_OFFICER": UserRole.FIELD_OFFICER,
        "INSURER": UserRole.INSURER,
        "SUPER_ADMIN": UserRole.SUPER_ADMIN,
    }
    user_role = role_map.get(req.role.upper(), UserRole.FARMER)

    # Use provided generated_password or create one
    plain_password = req.generated_password or f"{req.full_name.split()[0].capitalize()}#SAMRIDH2026!"
    hashed = get_password_hash(plain_password)

    docket_no = f"REG-PMFBY-2026-{(req.state or 'MP')[:2].upper()}-{random.randint(100000, 999999)}"

    new_user = User(
        id=str(uuid.uuid4()),
        username=username_clean,
        registration_no=req.registration_no or username_clean,
        full_name=req.full_name,
        hashed_password=hashed,
        role=user_role,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    role_str = new_user.role.value if isinstance(new_user.role, UserRole) else str(new_user.role)
    return RegisterResponse(
        success=True,
        username=username_clean,
        full_name=new_user.full_name,
        role=role_str,
        docket_no=docket_no,
        message=f"User '{username_clean}' successfully registered as {role_str}.",
    )


@router.get("/users")
def list_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all registered users. Super Admin only."""
    role_str = current_user.role.value if isinstance(current_user.role, UserRole) else str(current_user.role)
    if role_str != "SUPER_ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Super Admin access required.")

    users = db.query(User).order_by(User.created_at.desc()).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "full_name": u.full_name,
            "role": u.role.value if isinstance(u.role, UserRole) else str(u.role),
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


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
