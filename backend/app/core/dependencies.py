"""
Re-export authorization dependencies for backward compatibility.
"""

from app.api.deps import get_current_user, RoleChecker, security_scheme


def require_roles(allowed_roles):
    """Legacy helper function delegating to RoleChecker."""
    return RoleChecker(allowed_roles)
