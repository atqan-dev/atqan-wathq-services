"""
Notification Pydantic schemas.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.notification import (
    NotificationCategory,
    NotificationStatus,
    NotificationType,
)


class NotificationBase(BaseModel):
    """Base notification schema."""
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: NotificationType = NotificationType.INFO
    category: NotificationCategory = NotificationCategory.SYSTEM
    action_url: Optional[str] = Field(None, max_length=500)
    extra_data: Optional[str] = None
    expires_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    """Schema for creating notifications."""
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None
    management_user_id: Optional[int] = None


class NotificationUpdate(BaseModel):
    """Schema for updating notifications."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = Field(None, min_length=1)
    type: Optional[NotificationType] = None
    category: Optional[NotificationCategory] = None
    status: Optional[NotificationStatus] = None
    action_url: Optional[str] = Field(None, max_length=500)
    extra_data: Optional[str] = None
    expires_at: Optional[datetime] = None


class NotificationInDBBase(NotificationBase):
    """Base schema for notifications in database."""
    id: int
    status: NotificationStatus
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None
    management_user_id: Optional[int] = None
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Notification(NotificationInDBBase):
    """Schema for notification responses."""
    pass


class NotificationInDB(NotificationInDBBase):
    """Schema for notifications stored in database."""
    pass


class NotificationMarkAsRead(BaseModel):
    """Schema for marking notification as read."""
    notification_ids: list[int] = Field(..., min_items=1)


class NotificationStats(BaseModel):
    """Schema for notification statistics."""
    total: int
    unread: int
    read: int
    by_type: dict[str, int]
    by_category: dict[str, int]


class NotificationBulkCreate(BaseModel):
    """Schema for creating multiple notifications."""
    notifications: list[NotificationCreate] = Field(..., min_items=1)


class NotificationFilter(BaseModel):
    """Schema for filtering notifications."""
    status: Optional[NotificationStatus] = None
    type: Optional[NotificationType] = None
    category: Optional[NotificationCategory] = None
    user_id: Optional[int] = None
    tenant_id: Optional[int] = None
    management_user_id: Optional[int] = None
    include_expired: bool = False
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
