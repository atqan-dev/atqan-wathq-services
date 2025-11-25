"""
Management User database model for cross-tenant administration.
"""

from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class ManagementUser(Base):
    """
    Management User model for cross-tenant administration.
    These users can manage all tenants and regular users.
    """

    __tablename__ = "management_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    name_ar = Column(String, nullable=True)  # Arabic name
    logo = Column(String, nullable=True)  # User avatar/logo URL/path
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_super_admin = Column(Boolean, default=False)  # Can manage others
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # TOTP Two-Factor Authentication fields
    totp_enabled = Column(Boolean, default=False, nullable=False)
    totp_secret = Column(Text, nullable=True)  # Encrypted TOTP secret
    totp_backup_codes = Column(JSON, nullable=True)  # Hashed backup codes
    totp_verified_at = Column(
        DateTime(timezone=True), nullable=True
    )  # When 2FA was enabled
    totp_last_used_at = Column(
        DateTime(timezone=True), nullable=True
    )  # Last successful 2FA

    # Rate limiting for TOTP verification
    totp_failed_attempts = Column(Integer, default=0, nullable=False)
    totp_locked_until = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    notifications = relationship(
        "Notification", back_populates="management_user", cascade="all, delete-orphan"
    )
    # Profile relationship is defined in ManagementUserProfile
