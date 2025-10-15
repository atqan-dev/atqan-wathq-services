"""
Notification database model.
"""

import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class NotificationType(str, enum.Enum):
    """Notification types."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationStatus(str, enum.Enum):
    """Notification status."""
    UNREAD = "unread"
    READ = "read"


class NotificationCategory(str, enum.Enum):
    """Notification categories for better organization."""
    SYSTEM = "system"
    USER_ACTION = "user_action"
    SECURITY = "security"
    WATHQ_SERVICE = "wathq_service"
    TENANT = "tenant"
    DEPLOYMENT = "deployment"


class Notification(Base):
    """
    Notification model with multitenancy support.

    Notifications can be:
    - User-specific (user_id set, tenant_id from user)
    - Tenant-wide (user_id null, tenant_id set)
    - System-wide (both null, for management users)
    """

    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)

    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(
        Enum(NotificationType),
        default=NotificationType.INFO,
        nullable=False
    )
    category = Column(
        Enum(NotificationCategory),
        default=NotificationCategory.SYSTEM,
        nullable=False
    )

    # Status
    status = Column(
        Enum(NotificationStatus),
        default=NotificationStatus.UNREAD,
        nullable=False
    )

    # Targeting
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )  # Specific user
    tenant_id = Column(
        Integer,
        ForeignKey("tenants.id"),
        nullable=True,
        index=True
    )  # Tenant-wide
    management_user_id = Column(
        Integer,
        ForeignKey("management_users.id"),
        nullable=True,
        index=True
    )  # Management user

    # Metadata
    action_url = Column(String(500), nullable=True)  # Optional URL for action
    extra_data = Column(Text, nullable=True)  # JSON metadata

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    read_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional

    # Relationships
    user = relationship("User", back_populates="notifications")
    tenant = relationship("Tenant", back_populates="notifications")
    management_user = relationship(
        "ManagementUser",
        back_populates="notifications"
    )

    def __repr__(self):
        return (
            f"<Notification(id={self.id}, title='{self.title}', "
            f"type='{self.type}', status='{self.status}')>"
        )

    @property
    def is_expired(self) -> bool:
        """Check if notification is expired."""
        if not self.expires_at:
            return False
        return datetime.now(timezone.utc) > self.expires_at

    def mark_as_read(self):
        """Mark notification as read."""
        self.status = NotificationStatus.READ
        self.read_at = func.now()
