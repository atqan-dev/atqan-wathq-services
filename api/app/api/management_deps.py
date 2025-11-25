"""
Management-specific dependency injection utilities.
"""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.management_user import ManagementUser
from app.schemas.user import TokenPayload

logger = logging.getLogger(__name__)

reusable_oauth2 = HTTPBearer()


def get_current_management_user(
    db: Session = Depends(deps.get_db), token: str = Depends(reusable_oauth2)
) -> ManagementUser:
    """Get current authenticated management user."""
    logger.info("=== Management Auth Debug ===")
    logger.info(
        f"Token received: {token.credentials[:50]}..."
        if len(token.credentials) > 50
        else f"Token received: {token.credentials}"
    )

    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        logger.info(f"JWT decoded successfully. Payload: {payload}")
        token_data = TokenPayload(**payload)
        logger.info(
            f"TokenPayload created: sub={token_data.sub}, is_management_user={token_data.is_management_user}"
        )
    except JWTError as e:
        logger.error(f"JWTError: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: JWT Error - {str(e)}",
        )
    except ValidationError as e:
        logger.error(f"ValidationError: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: Validation Error - {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Could not validate credentials: {str(e)}",
        )

    # Verify this is a management user token
    if not token_data.is_management_user:
        logger.error(
            f"Token is not for management user. is_management_user={token_data.is_management_user}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Management user token required",
        )

    user = crud.management_user.get(db, id=token_data.sub)
    if not user:
        logger.error(f"Management user not found for id={token_data.sub}")
        raise HTTPException(status_code=404, detail="Management user not found")

    logger.info(f"Management user authenticated: id={user.id}, email={user.email}")
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
            detail="Super admin privileges required",
        )
    return current_user


def require_super_admin_or_self(user_id: int):
    """Dependency factory for operations that require super admin or self access."""

    def _check_permission(
        current_user: ManagementUser = Depends(get_current_active_management_user),
    ) -> ManagementUser:
        if (
            not crud.management_user.is_super_admin(current_user)
            and current_user.id != user_id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin privileges or self access required",
            )
        return current_user

    return _check_permission


def get_management_or_super_user(
    db: Session = Depends(deps.get_db), token: str = Depends(reusable_oauth2)
):
    """Get management user or regular super user for cross-system access."""
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

    # Check if management user
    if token_data.is_management_user:
        user = crud.management_user.get(db, id=token_data.sub)
        if not user or not crud.management_user.is_active(user):
            raise HTTPException(
                status_code=404, detail="Management user not found or inactive"
            )
        return {
            "type": "management",
            "user": user,
            "is_super_admin": user.is_super_admin,
        }

    # Check if regular super user
    user = crud.user.get(db, id=token_data.sub)
    if not user or not user.is_active:
        raise HTTPException(status_code=404, detail="User not found or inactive")

    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super user or management user privileges required",
        )

    return {"type": "regular", "user": user, "is_super_admin": user.is_superuser}
