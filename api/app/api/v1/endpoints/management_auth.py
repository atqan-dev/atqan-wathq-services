"""
Authentication endpoints for management users.

Supports TOTP two-factor authentication when enabled.
"""

from datetime import datetime, timedelta
from typing import Any, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordRequestForm,
)
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.totp import totp_service

router = APIRouter()
reusable_oauth2 = HTTPBearer()

# Temporary token for TOTP verification (short-lived)
TOTP_TEMP_TOKEN_EXPIRE_MINUTES = 5


def create_totp_temp_token(user_id: int) -> str:
    """Create a short-lived token for TOTP verification step."""
    expire = datetime.utcnow() + timedelta(minutes=TOTP_TEMP_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "exp": expire,
        "sub": str(user_id),
        "type": "totp_temp",
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=security.ALGORITHM)


def verify_totp_temp_token(token: str) -> int:
    """Verify a TOTP temporary token and return user_id."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        if payload.get("type") != "totp_temp":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid temporary token",
            )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid temporary token",
            )
        return int(user_id)
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Temporary token expired or invalid",
        ) from e


@router.post(
    "/login",
    response_model=Union[schemas.Token, schemas.TOTPRequiredResponse],
)
def management_login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Management user login.

    If TOTP is enabled, returns a temporary token for the second step.
    Otherwise, returns access and refresh tokens directly.
    """
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

    # Check if TOTP is enabled
    if user.totp_enabled:
        # Check if account is locked due to failed TOTP attempts
        if user.totp_locked_until:
            if datetime.utcnow() < user.totp_locked_until:
                remaining = (user.totp_locked_until - datetime.utcnow()).seconds // 60
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Account locked. Try again in {remaining} minutes.",
                )
            else:
                # Reset lockout
                user.totp_failed_attempts = 0
                user.totp_locked_until = None
                db.add(user)
                db.commit()

        # Return temporary token for TOTP verification
        temp_token = create_totp_temp_token(user.id)
        return schemas.TOTPRequiredResponse(
            requires_totp=True,
            temp_token=temp_token,
            message="Two-factor authentication required",
        )

    # No TOTP - issue tokens directly
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = security.create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        is_management_user=True,
        is_super_admin=user.is_super_admin,  # type: ignore
    )

    refresh_token = security.create_refresh_token(
        subject=user.id,
        is_management_user=True,
        is_super_admin=user.is_super_admin,  # type: ignore
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/totp", response_model=schemas.Token)
def management_login_totp(
    request: schemas.TOTPLoginRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Complete login with TOTP verification.

    Accepts either a 6-digit TOTP code or a backup code.
    """
    # Verify temporary token
    user_id = verify_totp_temp_token(request.temp_token)

    user = crud.management_user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.totp_enabled or not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is not enabled for this account",
        )

    # Check if account is locked
    if user.totp_locked_until and datetime.utcnow() < user.totp_locked_until:
        remaining = (user.totp_locked_until - datetime.utcnow()).seconds // 60
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked. Try again in {remaining} minutes.",
        )

    code = request.code.replace("-", "")  # Normalize backup codes
    is_valid = False
    is_backup_code = False

    # Try TOTP code first (6 digits)
    if len(code) == 6 and code.isdigit():
        try:
            secret = totp_service.decrypt_secret(user.totp_secret)
            is_valid = totp_service.verify_code(secret, code)
        except Exception:
            pass

    # Try backup code if TOTP failed
    if not is_valid and user.totp_backup_codes:
        is_valid, matched_hash = totp_service.verify_backup_code(
            request.code, user.totp_backup_codes
        )
        if is_valid:
            is_backup_code = True
            # Remove used backup code
            user.totp_backup_codes = [
                c for c in user.totp_backup_codes if c != matched_hash
            ]

    if not is_valid:
        # Increment failed attempts
        user.totp_failed_attempts = (user.totp_failed_attempts or 0) + 1

        if user.totp_failed_attempts >= totp_service.MAX_VERIFICATION_ATTEMPTS:
            user.totp_locked_until = datetime.utcnow() + timedelta(
                minutes=totp_service.LOCKOUT_DURATION_MINUTES
            )
            db.add(user)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Account locked for 15 minutes.",
            )

        db.add(user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code",
        )

    # Success - reset failed attempts and update last used
    user.totp_failed_attempts = 0
    user.totp_locked_until = None
    user.totp_last_used_at = datetime.utcnow()
    db.add(user)
    db.commit()

    # Issue tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = security.create_access_token(
        subject=user.id,
        expires_delta=access_token_expires,
        is_management_user=True,
        is_super_admin=user.is_super_admin,  # type: ignore
    )

    refresh_token = security.create_refresh_token(
        subject=user.id,
        is_management_user=True,
        is_super_admin=user.is_super_admin,  # type: ignore
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=schemas.Token)
def refresh_management_token(
    db: Session = Depends(deps.get_db),
    token: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
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
            is_super_admin=user.is_super_admin,  # type: ignore
        )

        # Create new refresh token
        new_refresh_token = security.create_refresh_token(
            subject=user.id,
            is_management_user=True,
            is_super_admin=user.is_super_admin,  # type: ignore
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
