"""
Service and TenantService database models with WATHQ integration.
"""

import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Numeric, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

# Association table for user-service permissions
user_service_permission = Table(
    "user_service_permissions",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("service_id", UUID(as_uuid=True), ForeignKey("services.id"), primary_key=True),
)


class Service(Base):
    """
    Service model for managing WATHQ services with UUID and slug.
    """

    __tablename__ = "services"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)  # e.g., 'commercial-registration'
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False, default="wathq")  # 'wathq', 'internal', etc.
    price = Column(Numeric(10, 2), nullable=False, default=0.00)
    is_active = Column(Boolean, default=True)
    requires_approval = Column(Boolean, default=True)  # Tenant admin approval required
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant_services = relationship("TenantService", back_populates="service")
    authorized_users = relationship("User", secondary=user_service_permission, back_populates="authorized_services")


class TenantService(Base):
    """
    TenantService model for tenant service subscriptions and management.
    """

    __tablename__ = "tenant_services"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)  # Admin approval status
    max_users = Column(Integer, default=10)  # Max users allowed for this service
    usage_count = Column(Integer, default=0)  # Track usage
    wathq_api_key = Column(String, nullable=True)  # Tenant-specific WATHQ API key
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    tenant = relationship("Tenant")
    service = relationship("Service", back_populates="tenant_services")
    approver = relationship("User", foreign_keys=[approved_by])