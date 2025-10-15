"""
Management-specific dependency injection utilities.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.management_user import ManagementUser
from app.schemas.user import TokenPayload
from app import crud

reusable_oauth2 = HTTPBearer()


def get_current_management_user(
    db: Session = Depends(deps.get_db),
    token: str = Depends(reusable_oauth2)
) -> ManagementUser:
    """Get current authenticated management user."""
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    # Verify this is a management user token
    if not token_data.is_management_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Management user token required",
        )

    user = crud.management_user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="Management user not found")
    return user


def get_current_active_management_user(
    current_user: ManagementUser = Depends(get_current_management_user),
) -> ManagementUser:
    """Get current active management user."""
    if not crud.management_user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive management user")
    return current_user


def get_current_super_admin(
    current_user: ManagementUser = Depends(get_current_active_management_user),
) -> ManagementUser:
    """Get current super admin management user."""
    if not crud.management_user.is_super_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin privileges required"
        )
    return current_user


def require_super_admin_or_self(user_id: int):
    """Dependency factory for operations that require super admin or self access."""
    def _check_permission(
        current_user: ManagementUser = Depends(get_current_active_management_user),
    ) -> ManagementUser:
        if not crud.management_user.is_super_admin(current_user) and current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin privileges or self access required"
            )
        return current_user
    return _check_permission


def get_management_or_super_user(
    db: Session = Depends(deps.get_db),
    token: str = Depends(reusable_oauth2)
):
    """Get management user or regular super user for cross-system access."""
    try:
        payload = jwt.decode(token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    # Check if management user
    if token_data.is_management_user:
        user = crud.management_user.get(db, id=token_data.sub)
        if not user or not crud.management_user.is_active(user):
            raise HTTPException(status_code=404, detail="Management user not found or inactive")
        return {"type": "management", "user": user, "is_super_admin": user.is_super_admin}
    
    # Check if regular super user
    user = crud.user.get(db, id=token_data.sub)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or inactive")
    
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super user or management user privileges required"
        )
    
    return {"type": "regular", "user": user, "is_super_admin": user.is_superuser}