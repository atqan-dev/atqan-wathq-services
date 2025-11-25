"""
Pydantic schemas for TOTP two-factor authentication.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TOTPSetupResponse(BaseModel):
    """Response when initiating TOTP setup."""

    secret: str = Field(
        ..., description="Base32-encoded TOTP secret (show once, then discard)"
    )
    qr_code: str = Field(
        ..., description="Base64-encoded QR code image for authenticator apps"
    )
    provisioning_uri: str = Field(..., description="otpauth:// URI for manual entry")
    backup_codes: list[str] = Field(
        ..., description="One-time backup codes for account recovery"
    )


class TOTPVerifyRequest(BaseModel):
    """Request to verify a TOTP code."""

    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit TOTP code from authenticator app",
    )


class TOTPVerifyResponse(BaseModel):
    """Response after verifying TOTP code."""

    success: bool
    message: str


class TOTPEnableRequest(BaseModel):
    """Request to enable TOTP after setup verification."""

    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="6-digit TOTP code to confirm setup",
    )


class TOTPEnableResponse(BaseModel):
    """Response after enabling TOTP."""

    enabled: bool
    message: str
    backup_codes: Optional[list[str]] = Field(
        None, description="Backup codes (only shown once when enabling)"
    )


class TOTPDisableRequest(BaseModel):
    """Request to disable TOTP."""

    password: str = Field(
        ..., min_length=1, description="Current password for verification"
    )
    code: Optional[str] = Field(
        None,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="TOTP code (required if TOTP is enabled)",
    )


class TOTPDisableResponse(BaseModel):
    """Response after disabling TOTP."""

    disabled: bool
    message: str


class TOTPStatusResponse(BaseModel):
    """Response with TOTP status for current user."""

    enabled: bool
    verified_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    backup_codes_remaining: int = 0


class TOTPLoginRequest(BaseModel):
    """Request for TOTP verification during login."""

    temp_token: str = Field(..., description="Temporary token from initial login")
    code: str = Field(
        ...,
        min_length=6,
        max_length=8,  # Allow backup codes (8 chars) or TOTP (6 digits)
        description="TOTP code or backup code",
    )


class TOTPLoginResponse(BaseModel):
    """Response after successful TOTP verification during login."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TOTPRequiredResponse(BaseModel):
    """Response when TOTP is required for login."""

    requires_totp: bool = True
    temp_token: str = Field(
        ..., description="Temporary token for TOTP verification step"
    )
    message: str = "Two-factor authentication required"


class BackupCodeVerifyRequest(BaseModel):
    """Request to verify a backup code."""

    code: str = Field(
        ...,
        min_length=8,
        max_length=9,  # With or without dash
        description="Backup code (format: XXXX-XXXX or XXXXXXXX)",
    )


class RegenerateBackupCodesRequest(BaseModel):
    """Request to regenerate backup codes."""

    password: str = Field(
        ..., min_length=1, description="Current password for verification"
    )
    code: str = Field(
        ...,
        min_length=6,
        max_length=6,
        pattern=r"^\d{6}$",
        description="Current TOTP code for verification",
    )


class RegenerateBackupCodesResponse(BaseModel):
    """Response with new backup codes."""

    backup_codes: list[str] = Field(
        ..., description="New backup codes (save these securely)"
    )
    message: str
