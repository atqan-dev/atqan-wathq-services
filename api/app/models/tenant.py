"""
Tenant database model for multitenancy support.
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class Tenant(Base):
    """
    Tenant model for multitenancy support.
    Each tenant represents an organization/company using the application.
    """

    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    name_ar = Column(String, nullable=True)  # Arabic name
    slug = Column(
        String, unique=True, index=True, nullable=False
    )  # Used for subdomain/identification
    description = Column(Text, nullable=True)
    logo = Column(String, nullable=True)  # Logo URL/path
    is_active = Column(Boolean, default=True)
    max_users = Column(Integer, default=100)  # User limit per tenant
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="tenant")
    roles = relationship("Role", back_populates="tenant")
    notifications = relationship(
        "Notification",
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
