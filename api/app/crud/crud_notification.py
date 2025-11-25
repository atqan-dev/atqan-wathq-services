"""
CRUD operations for notifications.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.notification import Notification, NotificationStatus
from app.schemas.notification import (
    NotificationCreate,
    NotificationFilter,
    NotificationUpdate,
)


class CRUDNotification(CRUDBase[Notification, NotificationCreate, NotificationUpdate]):
    """CRUD operations for notifications."""

    def get_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        tenant_id: int,
        skip: int = 0,
        limit: int = 50,
        include_expired: bool = False
    ) -> List[Notification]:
        """Get notifications for a specific user."""
        query = db.query(self.model).filter(
            or_(
                # User-specific notifications
                and_(
                    self.model.user_id == user_id,
                    self.model.tenant_id == tenant_id
                ),
                # Tenant-wide notifications (no specific user)
                and_(
                    self.model.user_id.is_(None),
                    self.model.tenant_id == tenant_id
                )
            )
        )
        
        if not include_expired:
            query = query.filter(
                or_(
                    self.model.expires_at.is_(None),
                    self.model.expires_at > func.now()
                )
            )
        
        return query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()

    def get_by_management_user(
        self,
        db: Session,
        *,
        management_user_id: int,
        skip: int = 0,
        limit: int = 50,
        include_expired: bool = False
    ) -> List[Notification]:
        """Get notifications for a management user."""
        query = db.query(self.model).filter(
            or_(
                # Management user-specific notifications
                self.model.management_user_id == management_user_id,
                # System-wide notifications (no specific user/tenant)
                and_(
                    self.model.user_id.is_(None),
                    self.model.tenant_id.is_(None),
                    self.model.management_user_id.is_(None)
                )
            )
        )
        
        if not include_expired:
            query = query.filter(
                or_(
                    self.model.expires_at.is_(None),
                    self.model.expires_at > func.now()
                )
            )
        
        return query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()

    def get_by_tenant(
        self,
        db: Session,
        *,
        tenant_id: int,
        skip: int = 0,
        limit: int = 50,
        include_expired: bool = False
    ) -> List[Notification]:
        """Get all notifications for a tenant."""
        query = db.query(self.model).filter(self.model.tenant_id == tenant_id)
        
        if not include_expired:
            query = query.filter(
                or_(
                    self.model.expires_at.is_(None),
                    self.model.expires_at > func.now()
                )
            )
        
        return query.order_by(desc(self.model.created_at)).offset(skip).limit(limit).all()

    def get_unread_count_by_user(
        self,
        db: Session,
        *,
        user_id: int,
        tenant_id: int
    ) -> int:
        """Get unread notification count for a user."""
        return db.query(self.model).filter(
            and_(
                or_(
                    # User-specific notifications
                    and_(
                        self.model.user_id == user_id,
                        self.model.tenant_id == tenant_id
                    ),
                    # Tenant-wide notifications
                    and_(
                        self.model.user_id.is_(None),
                        self.model.tenant_id == tenant_id
                    )
                ),
                self.model.status == NotificationStatus.UNREAD,
                or_(
                    self.model.expires_at.is_(None),
                    self.model.expires_at > func.now()
                )
            )
        ).count()

    def get_unread_count_by_management_user(
        self,
        db: Session,
        *,
        management_user_id: int
    ) -> int:
        """Get unread notification count for a management user."""
        return db.query(self.model).filter(
            and_(
                or_(
                    # Management user-specific notifications
                    self.model.management_user_id == management_user_id,
                    # System-wide notifications
                    and_(
                        self.model.user_id.is_(None),
                        self.model.tenant_id.is_(None),
                        self.model.management_user_id.is_(None)
                    )
                ),
                self.model.status == NotificationStatus.UNREAD,
                or_(
                    self.model.expires_at.is_(None),
                    self.model.expires_at > func.now()
                )
            )
        ).count()

    def mark_as_read(
        self,
        db: Session,
        *,
        notification_ids: List[int],
        user_id: Optional[int] = None,
        management_user_id: Optional[int] = None
    ) -> int:
        """Mark notifications as read."""
        query = db.query(self.model).filter(
            and_(
                self.model.id.in_(notification_ids),
                self.model.status == NotificationStatus.UNREAD
            )
        )
        
        # Add user/management user filter for security
        if user_id is not None:
            query = query.filter(
                or_(
                    self.model.user_id == user_id,
                    self.model.user_id.is_(None)  # Tenant-wide notifications
                )
            )
        elif management_user_id is not None:
            query = query.filter(
                or_(
                    self.model.management_user_id == management_user_id,
                    and_(
                        self.model.user_id.is_(None),
                        self.model.tenant_id.is_(None),
                        self.model.management_user_id.is_(None)
                    )  # System-wide notifications
                )
            )
        
        updated_count = query.update({
            self.model.status: NotificationStatus.READ,
            self.model.read_at: func.now()
        })
        
        db.commit()
        return updated_count

    def create_for_user(
        self,
        db: Session,
        *,
        obj_in: NotificationCreate,
        user_id: int,
        tenant_id: int
    ) -> Notification:
        """Create a notification for a specific user."""
        obj_in.user_id = user_id
        obj_in.tenant_id = tenant_id
        obj_in.management_user_id = None
        return self.create(db, obj_in=obj_in)

    def create_for_tenant(
        self,
        db: Session,
        *,
        obj_in: NotificationCreate,
        tenant_id: int
    ) -> Notification:
        """Create a tenant-wide notification."""
        obj_in.user_id = None
        obj_in.tenant_id = tenant_id
        obj_in.management_user_id = None
        return self.create(db, obj_in=obj_in)

    def create_for_management_user(
        self,
        db: Session,
        *,
        obj_in: NotificationCreate,
        management_user_id: int
    ) -> Notification:
        """Create a notification for a management user."""
        obj_in.user_id = None
        obj_in.tenant_id = None
        obj_in.management_user_id = management_user_id
        return self.create(db, obj_in=obj_in)

    def create_system_wide(
        self,
        db: Session,
        *,
        obj_in: NotificationCreate
    ) -> Notification:
        """Create a system-wide notification."""
        obj_in.user_id = None
        obj_in.tenant_id = None
        obj_in.management_user_id = None
        return self.create(db, obj_in=obj_in)

    def cleanup_expired(self, db: Session) -> int:
        """Remove expired notifications."""
        deleted_count = db.query(self.model).filter(
            and_(
                self.model.expires_at.isnot(None),
                self.model.expires_at < func.now()
            )
        ).delete()
        
        db.commit()
        return deleted_count

    def get_with_filter(
        self,
        db: Session,
        *,
        filter_params: NotificationFilter
    ) -> List[Notification]:
        """Get notifications with advanced filtering."""
        query = db.query(self.model)
        
        if filter_params.status:
            query = query.filter(self.model.status == filter_params.status)
        
        if filter_params.type:
            query = query.filter(self.model.type == filter_params.type)
        
        if filter_params.category:
            query = query.filter(self.model.category == filter_params.category)
        
        if filter_params.user_id:
            query = query.filter(self.model.user_id == filter_params.user_id)
        
        if filter_params.tenant_id:
            query = query.filter(self.model.tenant_id == filter_params.tenant_id)
        
        if filter_params.management_user_id:
            query = query.filter(
                self.model.management_user_id == filter_params.management_user_id
            )
        
        if not filter_params.include_expired:
            query = query.filter(
                or_(
                    self.model.expires_at.is_(None),
                    self.model.expires_at > func.now()
                )
            )
        
        return query.order_by(desc(self.model.created_at)).offset(
            filter_params.offset
        ).limit(filter_params.limit).all()

    def create_async(
        self,
        db: Session,
        *,
        title: str,
        message: str,
        notification_type: str = "info",
        category: str = "system",
        user_id: Optional[int] = None,
        tenant_id: Optional[int] = None,
        management_user_id: Optional[int] = None,
        action_url: Optional[str] = None,
        extra_data: Optional[dict] = None,
        expires_at: Optional[datetime] = None,
    ) -> str:
        """
        Create notification asynchronously using Celery.

        Returns the Celery task ID.
        """
        from app.celery_worker.tasks import create_notification_task

        task = create_notification_task.delay(
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
            user_id=user_id,
            tenant_id=tenant_id,
            management_user_id=management_user_id,
            action_url=action_url,
            extra_data=extra_data,
            expires_at=expires_at,
        )

        return task.id


notification = CRUDNotification(Notification)
