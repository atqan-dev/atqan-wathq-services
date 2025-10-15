"""
Celery tasks for WATHQ notifications system.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

from app.celery_worker.celery_app import celery_app
from app.db.session import SessionLocal
from app.models.notification import Notification, NotificationStatus
from app.schemas.notification import NotificationCreate

logger = logging.getLogger(__name__)


@celery_app.task
def create_notification_task(
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
    Create a notification asynchronously.

    Returns notification ID.
    """
    from app.crud.crud_notification import notification as notification_crud

    try:
        db = SessionLocal()

        notification_data = NotificationCreate(
            title=title,
            message=message,
            type=notification_type,
            category=category,
            user_id=user_id,
            tenant_id=tenant_id,
            management_user_id=management_user_id,
            action_url=action_url,
            extra_data=str(extra_data) if extra_data else None,
            expires_at=expires_at,
        )

        notification = notification_crud.create(db, obj_in=notification_data)

        logger.info(f"Created notification {notification.id} via Celery task")
        return str(notification.id)

    except Exception as e:
        logger.error(f"Failed to create notification via Celery: {e}")
        raise
    finally:
        db.close()


@celery_app.task
def send_notification_email_task(
    notification_id: int,
    recipient_email: str,
    recipient_name: Optional[str] = None,
) -> bool:
    """
    Send notification email asynchronously.

    Returns True if sent successfully.
    """
    try:
        # For now, just log the email sending (email service needs to be implemented)
        logger.info(f"Would send email to {recipient_email} for notification {notification_id}")

        # TODO: Implement actual email sending
        # from app.services.email_service import send_notification_email

        return True

    except Exception as e:
        logger.error(f"Failed to send notification email via Celery: {e}")
        return False


@celery_app.task
def cleanup_expired_notifications() -> int:
    """
    Clean up expired notifications.

    Returns number of notifications cleaned up.
    """
    try:
        db = SessionLocal()

        # Get expired notifications
        expired_notifications = (
            db.query(Notification)
            .filter(Notification.expires_at < datetime.now(timezone.utc))
            .all()
        )

        if not expired_notifications:
            logger.info("No expired notifications to clean up")
            return 0

        # Delete expired notifications
        deleted_count = 0
        for notification in expired_notifications:
            db.delete(notification)
            deleted_count += 1

        db.commit()
        logger.info(f"Cleaned up {deleted_count} expired notifications")

        return deleted_count

    except Exception as e:
        logger.error(f"Failed to cleanup expired notifications: {e}")
        return 0
    finally:
        db.close()


@celery_app.task
def send_pending_notifications() -> int:
    """
    Send pending notifications that haven't been sent yet.

    Returns number of notifications sent.
    """
    try:
        db = SessionLocal()

        # Get unread notifications that should be sent via email
        pending_notifications = (
            db.query(Notification)
            .filter(
                Notification.status == NotificationStatus.UNREAD,
                Notification.user_id.isnot(None),  # Only user-specific notifications
            )
            .limit(50)  # Process in batches
            .all()
        )

        sent_count = 0
        for notification in pending_notifications:
            if notification.user and notification.user.email:
                # TODO: Send actual email
                logger.info(f"Would send email for notification {notification.id}")

                notification.status = NotificationStatus.READ
                notification.read_at = datetime.now(timezone.utc)
                sent_count += 1

        db.commit()
        logger.info(f"Processed {sent_count} pending notifications")

        return sent_count

    except Exception as e:
        logger.error(f"Failed to send pending notifications: {e}")
        return 0
    finally:
        db.close()


@celery_app.task
def process_wathq_service_notification(
    service_slug: str,
    tenant_id: int,
    user_id: Optional[int] = None,
    message: str = "WATHQ service operation completed",
    notification_type: str = "success",
) -> str:
    """
    Process WATHQ service-related notifications.

    Returns notification ID.
    """
    return create_notification_task.delay(
        title=f"WATHQ Service: {service_slug}",
        message=message,
        notification_type=notification_type,
        category="wathq_service",
        user_id=user_id,
        tenant_id=tenant_id,
    ).id


@celery_app.task
def process_tenant_notification(
    tenant_id: int,
    title: str,
    message: str,
    notification_type: str = "info",
    category: str = "tenant",
) -> str:
    """
    Process tenant-related notifications.

    Returns notification ID.
    """
    return create_notification_task.delay(
        title=title,
        message=message,
        notification_type=notification_type,
        category=category,
        tenant_id=tenant_id,
    ).id


@celery_app.task
def process_security_notification(
    user_id: Optional[int] = None,
    management_user_id: Optional[int] = None,
    title: str = "Security Alert",
    message: str = "Security event detected",
    notification_type: str = "warning",
) -> str:
    """
    Process security-related notifications.

    Returns notification ID.
    """
    return create_notification_task.delay(
        title=title,
        message=message,
        notification_type=notification_type,
        category="security",
        user_id=user_id,
        management_user_id=management_user_id,
    ).id
