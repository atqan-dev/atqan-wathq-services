"""
Authentication endpoints for management users.
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, schemas, models
from app.api import deps
from app.core import security
from app.core.config import settings

router = APIRouter()
reusable_oauth2 = HTTPBearer()


@router.post("/login", response_model=schemas.Token)
def management_login(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """Management user login."""
    user = crud.management_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not crud.management_user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = security.create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        is_management_user=True,
        is_super_admin=user.is_super_admin,
    )

    refresh_token = security.create_refresh_token(
        subject=user.id,
        is_management_user=True,
        is_super_admin=user.is_super_admin,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=schemas.Token)
def refresh_management_token(
    db: Session = Depends(deps.get_db), token: str = Depends(reusable_oauth2)
) -> Any:
    """Refresh management user token."""
    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        # Check if this is a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token"
            )

        # Verify this is a management user token
        if not payload.get("is_management_user"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Management user token required",
            )

        user_id = payload.get("sub")
        user = crud.management_user.get(db, id=user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Management user not found")

        if not crud.management_user.is_active(user):
            raise HTTPException(status_code=400, detail="Inactive management user")

        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = security.create_access_token(
            subject=user.id,
            expires_delta=access_token_expires,
            is_management_user=True,
            is_super_admin=user.is_super_admin,
        )

        # Create new refresh token
        new_refresh_token = security.create_refresh_token(
            subject=user.id,
            is_management_user=True,
            is_super_admin=user.is_super_admin,
        )

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    except (JWTError, ValidationError) as e:
        print(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/test-token", response_model=schemas.ManagementUser)
def test_token(
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Test access token and return current user with tenant info.
    """
    return current_user
