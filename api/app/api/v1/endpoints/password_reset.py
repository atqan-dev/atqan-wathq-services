"""
Password reset endpoints for management users.
"""

from datetime import datetime, timedelta
from typing import Any, Optional
import secrets
import string

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app import crud, schemas
from app.api import deps
from app.api.management_deps import get_current_active_management_user
from app.core import security
from app.core.config import settings
from app.models.management_user import ManagementUser
from app.db.session import SessionLocal

router = APIRouter()


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PasswordResetToken(BaseModel):
    """Store password reset tokens in memory (in production, use Redis or DB)"""
    email: str
    token: str
    expires_at: datetime


# In-memory storage for reset tokens (in production, use Redis or database)
reset_tokens: dict[str, PasswordResetToken] = {}


def generate_reset_token() -> str:
    """Generate a secure random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


def send_reset_email(email: str, token: str):
    """Send password reset email (placeholder - implement actual email sending)."""
    reset_link = f"http://localhost:3000/reset-password?token={token}"
    print(f"Password reset link for {email}: {reset_link}")
    # In production, implement actual email sending here
    # You can use services like SendGrid, AWS SES, or SMTP


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    *,
    db: Session = Depends(deps.get_db),
    body: PasswordResetRequest,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Request password reset for management user.
    """
    # Check if user exists
    user = db.query(ManagementUser).filter(
        ManagementUser.email == body.email
    ).first()
    
    if not user:
        # Don't reveal if email exists or not for security
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    token = generate_reset_token()
    
    # Store token with expiration (15 minutes)
    reset_tokens[token] = PasswordResetToken(
        email=body.email,
        token=token,
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )
    
    # Send reset email in background
    background_tasks.add_task(send_reset_email, body.email, token)
    
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    *,
    db: Session = Depends(deps.get_db),
    body: PasswordResetConfirm
) -> Any:
    """
    Reset password using token.
    """
    # Check if token exists and is valid
    token_data = reset_tokens.get(body.token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Check if token is expired
    if datetime.utcnow() > token_data.expires_at:
        # Remove expired token
        del reset_tokens[body.token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    # Get user
    user = db.query(ManagementUser).filter(
        ManagementUser.email == token_data.email
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    hashed_password = security.get_password_hash(body.new_password)
    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    
    # Remove used token
    del reset_tokens[body.token]
    
    return {"message": "Password has been reset successfully"}


@router.post("/validate-token", status_code=status.HTTP_200_OK)
def validate_reset_token(token: str) -> Any:
    """
    Validate if a reset token is valid.
    """
    token_data = reset_tokens.get(token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset token"
        )
    
    # Check if token is expired
    if datetime.utcnow() > token_data.expires_at:
        # Remove expired token
        del reset_tokens[token]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reset token has expired"
        )
    
    return {
        "valid": True,
        "email": token_data.email
    }


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    *,
    db: Session = Depends(deps.get_db),
    body: PasswordChangeRequest,
    current_user: ManagementUser = Depends(get_current_active_management_user)
) -> Any:
    """
    Change password for authenticated management user.
    """
    # Verify current password
    if not security.verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Check if new password is different from current
    if security.verify_password(body.new_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password
    hashed_password = security.get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    db.add(current_user)
    db.commit()
    
    return {"message": "Password changed successfully"}
