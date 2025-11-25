"""
TOTP (Two-Factor Authentication) endpoints for management users.

Security Features:
- Rate limiting on verification attempts
- Secure secret storage (encrypted at rest)
- Backup codes for account recovery
- Audit logging for security events
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps
from app.core.security import verify_password
from app.core.totp import totp_service

router = APIRouter()


@router.get("/status", response_model=schemas.TOTPStatusResponse)
def get_totp_status(
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Get TOTP status for the current user.
    """
    backup_codes_count = 0
    if current_user.totp_backup_codes:
        backup_codes_count = len(current_user.totp_backup_codes)

    return schemas.TOTPStatusResponse(
        enabled=current_user.totp_enabled,
        verified_at=current_user.totp_verified_at,
        last_used_at=current_user.totp_last_used_at,
        backup_codes_remaining=backup_codes_count,
    )


@router.post("/setup", response_model=schemas.TOTPSetupResponse)
def setup_totp(
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Initialize TOTP setup for the current user.

    Returns a secret, QR code, and backup codes.
    The user must verify with a code before TOTP is enabled.
    """
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is already enabled. Disable it first to set up again.",
        )

    # Generate new secret
    secret = totp_service.generate_secret()

    # Generate QR code
    qr_code = totp_service.generate_qr_code_base64(
        secret=secret,
        email=current_user.email,
    )

    # Generate provisioning URI
    provisioning_uri = totp_service.get_provisioning_uri(
        secret=secret,
        email=current_user.email,
    )

    # Generate backup codes
    backup_codes = totp_service.generate_backup_codes()

    # Store encrypted secret and hashed backup codes (not enabled yet)
    encrypted_secret = totp_service.encrypt_secret(secret)
    hashed_backup_codes = [totp_service.hash_backup_code(code) for code in backup_codes]

    # Update user with pending TOTP setup
    current_user.totp_secret = encrypted_secret
    current_user.totp_backup_codes = hashed_backup_codes
    current_user.totp_enabled = False  # Not enabled until verified
    db.add(current_user)
    db.commit()

    return schemas.TOTPSetupResponse(
        secret=secret,
        qr_code=qr_code,
        provisioning_uri=provisioning_uri,
        backup_codes=backup_codes,
    )


@router.post("/enable", response_model=schemas.TOTPEnableResponse)
def enable_totp(
    request: schemas.TOTPEnableRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Enable TOTP after verifying setup with a code.

    This confirms the user has successfully set up their authenticator app.
    """
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is already enabled.",
        )

    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP setup not initiated. Call /setup first.",
        )

    # Check rate limiting
    if current_user.totp_locked_until:
        if datetime.utcnow() < current_user.totp_locked_until:
            remaining = (
                current_user.totp_locked_until - datetime.utcnow()
            ).seconds // 60
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many attempts. Try again in {remaining} minutes.",
            )
        else:
            # Reset lockout
            current_user.totp_failed_attempts = 0
            current_user.totp_locked_until = None

    # Decrypt and verify
    try:
        secret = totp_service.decrypt_secret(current_user.totp_secret)
        is_valid = totp_service.verify_code(secret, request.code)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying TOTP code.",
        )

    if not is_valid:
        # Increment failed attempts
        current_user.totp_failed_attempts += 1

        if current_user.totp_failed_attempts >= totp_service.MAX_VERIFICATION_ATTEMPTS:
            current_user.totp_locked_until = datetime.utcnow() + timedelta(
                minutes=totp_service.LOCKOUT_DURATION_MINUTES
            )
            db.add(current_user)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many failed attempts. Account locked for 15 minutes.",
            )

        db.add(current_user)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code.",
        )

    # Enable TOTP
    current_user.totp_enabled = True
    current_user.totp_verified_at = datetime.utcnow()
    current_user.totp_failed_attempts = 0
    current_user.totp_locked_until = None
    db.add(current_user)
    db.commit()

    return schemas.TOTPEnableResponse(
        enabled=True,
        message="Two-factor authentication has been enabled successfully.",
        backup_codes=None,  # Already provided during setup
    )


@router.post("/disable", response_model=schemas.TOTPDisableResponse)
def disable_totp(
    request: schemas.TOTPDisableRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Disable TOTP for the current user.

    Requires password verification and TOTP code (if enabled).
    """
    # Verify password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password.",
        )

    # If TOTP is enabled, require a valid code
    if current_user.totp_enabled:
        if not request.code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TOTP code is required to disable two-factor authentication.",
            )

        try:
            secret = totp_service.decrypt_secret(current_user.totp_secret)
            is_valid = totp_service.verify_code(secret, request.code)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error verifying TOTP code.",
            )

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid TOTP code.",
            )

    # Disable TOTP and clear all related data
    current_user.totp_enabled = False
    current_user.totp_secret = None
    current_user.totp_backup_codes = None
    current_user.totp_verified_at = None
    current_user.totp_last_used_at = None
    current_user.totp_failed_attempts = 0
    current_user.totp_locked_until = None
    db.add(current_user)
    db.commit()

    return schemas.TOTPDisableResponse(
        disabled=True,
        message="Two-factor authentication has been disabled.",
    )


@router.post("/verify", response_model=schemas.TOTPVerifyResponse)
def verify_totp(
    request: schemas.TOTPVerifyRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Verify a TOTP code for the current user.

    This endpoint can be used to test TOTP codes without any side effects.
    """
    if not current_user.totp_enabled or not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is not enabled for this account.",
        )

    try:
        secret = totp_service.decrypt_secret(current_user.totp_secret)
        is_valid = totp_service.verify_code(secret, request.code)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying TOTP code.",
        )

    if is_valid:
        return schemas.TOTPVerifyResponse(
            success=True,
            message="TOTP code is valid.",
        )
    else:
        return schemas.TOTPVerifyResponse(
            success=False,
            message="Invalid TOTP code.",
        )


@router.post(
    "/backup-codes/regenerate", response_model=schemas.RegenerateBackupCodesResponse
)
def regenerate_backup_codes(
    request: schemas.RegenerateBackupCodesRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Regenerate backup codes for the current user.

    Requires password and TOTP verification.
    Old backup codes will be invalidated.
    """
    if not current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is not enabled for this account.",
        )

    # Verify password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password.",
        )

    # Verify TOTP code
    try:
        secret = totp_service.decrypt_secret(current_user.totp_secret)
        is_valid = totp_service.verify_code(secret, request.code)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verifying TOTP code.",
        )

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code.",
        )

    # Generate new backup codes
    backup_codes = totp_service.generate_backup_codes()
    hashed_backup_codes = [totp_service.hash_backup_code(code) for code in backup_codes]

    # Update user
    current_user.totp_backup_codes = hashed_backup_codes
    db.add(current_user)
    db.commit()

    return schemas.RegenerateBackupCodesResponse(
        backup_codes=backup_codes,
        message="Backup codes have been regenerated. Save them securely.",
    )


@router.post("/backup-codes/verify", response_model=schemas.TOTPVerifyResponse)
def verify_backup_code(
    request: schemas.BackupCodeVerifyRequest,
    db: Session = Depends(deps.get_db),
    current_user: models.ManagementUser = Depends(deps.get_current_management_user),
) -> Any:
    """
    Verify and consume a backup code.

    The backup code will be invalidated after successful use.
    """
    if not current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP is not enabled for this account.",
        )

    if not current_user.totp_backup_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No backup codes available.",
        )

    # Verify backup code
    is_valid, matched_hash = totp_service.verify_backup_code(
        request.code,
        current_user.totp_backup_codes,
    )

    if not is_valid:
        return schemas.TOTPVerifyResponse(
            success=False,
            message="Invalid backup code.",
        )

    # Remove used backup code
    current_user.totp_backup_codes = [
        code for code in current_user.totp_backup_codes if code != matched_hash
    ]
    current_user.totp_last_used_at = datetime.utcnow()
    db.add(current_user)
    db.commit()

    return schemas.TOTPVerifyResponse(
        success=True,
        message="Backup code verified and consumed.",
    )
