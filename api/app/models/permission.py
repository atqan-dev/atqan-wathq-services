"""
Permission and Role models for RBAC system.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

# Association table for role-permission many-to-many relationship
role_permission_association = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True),
)

# Association table for user-role many-to-many relationship
user_role_association = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class Permission(Base):
    """
    Individual permission model with WATHQ service support.
    """

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(
        String, unique=True, nullable=False, index=True
    )  # e.g., 'use_commercial_registration', 'manage_tenant_services'
    description = Column(Text, nullable=True)
    resource = Column(String, nullable=False)  # e.g., 'user', 'tenant', 'service', 'wathq_service'
    action = Column(
        String, nullable=False
    )  # e.g., 'create', 'read', 'update', 'delete', 'use', 'manage'
    scope = Column(String, default="tenant")  # 'tenant', 'system', 'service'
    service_slug = Column(String, nullable=True)  # For service-specific permissions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    roles = relationship(
        "Role", secondary=role_permission_association, back_populates="permissions"
    )


class Role(Base):
    """
    Role model that groups permissions (e.g., 'admin', 'manager', 'member').
    Roles are tenant-specific or system-wide.
    """

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)  # e.g., 'admin', 'manager'
    description = Column(Text, nullable=True)
    tenant_id = Column(
        Integer, ForeignKey("tenants.id"), nullable=True, index=True
    )  # NULL for system roles
    is_default = Column(Boolean, default=False)  # Default role for new users in tenant
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="roles")
    permissions = relationship(
        "Permission", secondary=role_permission_association, back_populates="roles"
    )
    users = relationship(
        "User", secondary=user_role_association, back_populates="roles"
    )
