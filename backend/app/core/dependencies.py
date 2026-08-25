from typing import List, Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db),
):
    """Retrieve and authenticate the current user from Bearer token"""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "NOT_AUTHENTICATED", "message": "Authentication token is required"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(auth.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Invalid or expired token"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    from app.models.user import User
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "INACTIVE_USER", "message": "User account is disabled"},
        )
    
    return user


def require_roles(allowed_roles: List[str]):
    """Role-Based Access Control (RBAC) dependency factory"""
    def role_checker(current_user = Depends(get_current_user)):
        user_role = getattr(current_user, "role", None)
        if hasattr(user_role, "name"):
            role_name = user_role.name
        elif isinstance(user_role, str):
            role_name = user_role
        else:
            role_name = str(user_role)
            
        # Super admin always has access
        if role_name == "super_admin":
            return current_user
            
        if role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ACCESS_DENIED",
                    "message": f"Role '{role_name}' is not authorized to access this resource. Allowed: {allowed_roles}",
                },
            )
        return current_user
    return role_checker
