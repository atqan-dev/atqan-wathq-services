"""
User database model.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class User(Base):
    """
    User model for database with tenant support and role-based permissions.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(
        String, index=True, nullable=False
    )  # Removed unique constraint for multitenancy
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    name_ar = Column(String, nullable=True)  # Arabic name
    logo = Column(String, nullable=True)  # User avatar/logo URL/path
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    roles = relationship("Role", secondary="user_roles", back_populates="users")
    authorized_services = relationship("Service", secondary="user_service_permissions", back_populates="authorized_users")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
