"""
Dependency injection utilities for FastAPI.
"""

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.core.multitenancy import get_current_tenant
from app.db.session import SessionLocal
from app.models.user import User
from app.models.management_user import ManagementUser
from app.schemas.user import TokenPayload

reusable_oauth2 = HTTPBearer()


def get_db() -> Generator:
    """
    Get database session.
    """
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    """
    Get current authenticated user.
    """
    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    # Verify tenant context matches token
    current_tenant = get_current_tenant()
    if current_tenant.tenant_slug and token_data.tenant_slug:
        if current_tenant.tenant_slug != token_data.tenant_slug:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token tenant does not match request tenant",
            )

    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Additional tenant validation
    if token_data.tenant_id and user.tenant_id != token_data.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to the specified tenant",
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get current active superuser.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


def get_current_management_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> ManagementUser:
    """
    Get current authenticated management user.
    """
    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    # Management users don't have tenant context
    management_user = db.query(ManagementUser).filter(
        ManagementUser.id == token_data.sub
    ).first()
    
    if not management_user:
        raise HTTPException(status_code=404, detail="Management user not found")
    
    if not management_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive management user")
    
    return management_user


def get_current_user_optional(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User | None:
    """
    Get current user if authenticated, otherwise return None.
    """
    try:
        return get_current_user(db, token)
    except HTTPException:
        return None


def get_current_management_user_optional(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> ManagementUser | None:
    """
    Get current management user if authenticated, otherwise return None.
    """
    try:
        return get_current_management_user(db, token)
    except HTTPException:
        return None


def has_permission(user: User, permission_name: str) -> bool:
    """
    Check if user has a specific permission.
    """
    if user.is_superuser:
        return True
    
    # Check user's roles for the permission
    for role in user.roles:
        for permission in role.permissions:
            if permission.name == permission_name:
                return True
    
    return False


def require_permission(user: User, permission_name: str) -> None:
    """
    Require user to have a specific permission, raise exception if not.
    """
    if not has_permission(user, permission_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission_name}' required"
        )
