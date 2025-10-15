"""
Security utilities for authentication and authorization.
"""

from datetime import datetime, timedelta
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Use a configuration that avoids the bcrypt issue
pwd_context = CryptContext(
    schemes=["argon2"],
    default="argon2",
    deprecated="auto"
)

ALGORITHM = "HS256"


def create_access_token(
    subject: str | Any,
    tenant_id: int = None,
    tenant_slug: str = None,
    expires_delta: timedelta = None,
    is_management_user: bool = False,
    is_super_admin: bool = False,
) -> str:
    """
    Create a JWT access token with tenant and management information.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "tenant_id": tenant_id,
        "tenant_slug": tenant_slug,
        "is_management_user": is_management_user,
        "is_super_admin": is_super_admin,
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    subject: str | Any,
    tenant_id: int = None,
    tenant_slug: str = None,
    is_management_user: bool = False,
    is_super_admin: bool = False,
) -> str:
    """
    Create a JWT refresh token with tenant and management information.
    """
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "tenant_id": tenant_id,
        "tenant_slug": tenant_slug,
        "is_management_user": is_management_user,
        "is_super_admin": is_super_admin,
        "type": "refresh",
    }
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Get password hash.
    """
    return pwd_context.hash(password)
