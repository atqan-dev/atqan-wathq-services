"""
Notification API endpoints.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.management_deps import get_current_management_user
from app.api.deps import get_db

router = APIRouter()


@router.get("/", response_model=List[schemas.Notification])
def get_notifications(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_expired: bool = Query(False),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> List[models.Notification]:
    """
    Get notifications for the current user.
    """
    try:
        notifications = crud.notification.get_by_user(
            db,
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            skip=skip,
            limit=limit,
            include_expired=include_expired,
        )
        return notifications
    except Exception as e:
        # If table doesn't exist yet, return empty list
        # This happens when migrations haven't been run
        import logging
        logging.warning(f"Failed to get notifications: {e}")
        return []


@router.get("/unread-count", response_model=int)
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> int:
    """
    Get unread notification count for the current user.
    """
    try:
        return crud.notification.get_unread_count_by_user(
            db, user_id=current_user.id, tenant_id=current_user.tenant_id
        )
    except Exception as e:
        # If table doesn't exist yet, return 0
        # This happens when migrations haven't been run
        import logging
        logging.warning(f"Failed to get unread count: {e}")
        return 0


@router.post("/mark-as-read", response_model=dict)
def mark_notifications_as_read(
    *,
    db: Session = Depends(get_db),
    notification_data: schemas.NotificationMarkAsRead,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> dict:
    """
    Mark notifications as read for the current user.
    """
    updated_count = crud.notification.mark_as_read(
        db,
        notification_ids=notification_data.notification_ids,
        user_id=current_user.id,
    )
    return {"updated_count": updated_count}


@router.post("/", response_model=schemas.Notification)
async def create_notification(
    *,
    db: Session = Depends(get_db),
    notification_in: schemas.NotificationCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> models.Notification:
    """
    Create a new notification. Only superusers can create notifications.
    Automatically broadcasts via WebSocket to connected users.
    """
    from app.api.v1.endpoints.ws_notifications import (
        broadcast_notification_to_user,
        broadcast_notification_to_tenant,
    )
    
    if notification_in.user_id:
        # User-specific notification
        user = crud.user.get(db, id=notification_in.user_id)
        if not user or user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in your tenant"
            )
        notification = crud.notification.create_for_user(
            db,
            obj_in=notification_in,
            user_id=notification_in.user_id,
            tenant_id=current_user.tenant_id,
        )
        
        # Broadcast to user via WebSocket
        await broadcast_notification_to_user(
            notification_in.user_id,
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "created_at": notification.created_at.isoformat() if notification.created_at else None,
                "is_read": notification.is_read,
                "user_id": notification.user_id,
                "tenant_id": notification.tenant_id,
            }
        )
        return notification
    else:
        # Tenant-wide notification
        notification = crud.notification.create_for_tenant(
            db, obj_in=notification_in, tenant_id=current_user.tenant_id
        )
        
        # Broadcast to tenant via WebSocket
        await broadcast_notification_to_tenant(
            current_user.tenant_id,
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "created_at": notification.created_at.isoformat() if notification.created_at else None,
                "is_read": notification.is_read,
                "tenant_id": notification.tenant_id,
            }
        )
        return notification


@router.get("/{notification_id}", response_model=schemas.Notification)
def get_notification(
    *,
    db: Session = Depends(get_db),
    notification_id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> models.Notification:
    """
    Get a specific notification by ID.
    """
    notification = crud.notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Check if user has access to this notification
    if notification.user_id and notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if notification.tenant_id and notification.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return notification


@router.delete("/{notification_id}", response_model=dict)
def delete_notification(
    *,
    db: Session = Depends(get_db),
    notification_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> dict:
    """
    Delete a notification. Only superusers can delete notifications.
    """
    notification = crud.notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    # Check if user has access to this notification
    if notification.tenant_id and notification.tenant_id != current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    crud.notification.remove(db, id=notification_id)
    return {"message": "Notification deleted successfully"}


# Management endpoints
@router.get("/management/", response_model=List[schemas.Notification])
def get_management_notifications(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_expired: bool = Query(False),
    current_management_user: models.ManagementUser = Depends(get_current_management_user),
) -> List[models.Notification]:
    """
    Get notifications for the current management user.
    """
    notifications = crud.notification.get_by_management_user(
        db,
        management_user_id=current_management_user.id,
        skip=skip,
        limit=limit,
        include_expired=include_expired,
    )
    return notifications


@router.get("/management/unread-count", response_model=int)
def get_management_unread_count(
    db: Session = Depends(get_db),
    current_management_user: models.ManagementUser = Depends(get_current_management_user),
) -> int:
    """
    Get unread notification count for the current management user.
    """
    return crud.notification.get_unread_count_by_management_user(
        db, management_user_id=current_management_user.id
    )


@router.post("/management/mark-as-read", response_model=dict)
def mark_management_notifications_as_read(
    *,
    db: Session = Depends(get_db),
    notification_data: schemas.NotificationMarkAsRead,
    current_management_user: models.ManagementUser = Depends(get_current_management_user),
) -> dict:
    """
    Mark notifications as read for the current management user.
    """
    updated_count = crud.notification.mark_as_read(
        db,
        notification_ids=notification_data.notification_ids,
        management_user_id=current_management_user.id,
    )
    return {"updated_count": updated_count}


@router.post("/management/create", response_model=schemas.Notification)
async def create_management_notification(
    *,
    db: Session = Depends(get_db),
    notification_in: schemas.NotificationCreate,
    current_management_user: models.ManagementUser = Depends(get_current_management_user),
) -> models.Notification:
    """
    Create a notification for management users or system-wide.
    Automatically broadcasts via WebSocket to connected users.
    """
    from app.api.v1.endpoints.ws_notifications import (
        broadcast_notification_to_user,
        broadcast_notification_to_tenant,
        broadcast_notification_to_management_user,
        broadcast_system_notification,
    )
    
    if notification_in.management_user_id:
        # Management user-specific notification
        management_user = crud.management_user.get(db, id=notification_in.management_user_id)
        if not management_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Management user not found"
            )
        notification = crud.notification.create_for_management_user(
            db,
            obj_in=notification_in,
            management_user_id=notification_in.management_user_id,
        )
        
        # Broadcast to management user via WebSocket
        await broadcast_notification_to_management_user(
            notification_in.management_user_id,
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "created_at": notification.created_at.isoformat() if notification.created_at else None,
                "is_read": notification.is_read,
                "management_user_id": notification.management_user_id,
            }
        )
        return notification
        
    elif notification_in.tenant_id:
        # Tenant-wide notification
        tenant = crud.tenant.get(db, id=notification_in.tenant_id)
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        notification = crud.notification.create_for_tenant(
            db, obj_in=notification_in, tenant_id=notification_in.tenant_id
        )
        
        # Broadcast to tenant via WebSocket
        await broadcast_notification_to_tenant(
            notification_in.tenant_id,
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "created_at": notification.created_at.isoformat() if notification.created_at else None,
                "is_read": notification.is_read,
                "tenant_id": notification.tenant_id,
            }
        )
        return notification
        
    elif notification_in.user_id:
        # User-specific notification
        user = crud.user.get(db, id=notification_in.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        notification = crud.notification.create_for_user(
            db,
            obj_in=notification_in,
            user_id=notification_in.user_id,
            tenant_id=user.tenant_id,
        )
        
        # Broadcast to user via WebSocket
        await broadcast_notification_to_user(
            notification_in.user_id,
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "created_at": notification.created_at.isoformat() if notification.created_at else None,
                "is_read": notification.is_read,
                "user_id": notification.user_id,
                "tenant_id": notification.tenant_id,
            }
        )
        return notification
        
    else:
        # System-wide notification
        notification = crud.notification.create_system_wide(db, obj_in=notification_in)
        
        # Broadcast to all users via WebSocket
        await broadcast_system_notification(
            {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "notification_type": notification.notification_type,
                "created_at": notification.created_at.isoformat() if notification.created_at else None,
                "is_read": notification.is_read,
            }
        )
        return notification


@router.post("/management/cleanup-expired", response_model=dict)
def cleanup_expired_notifications(
    db: Session = Depends(get_db),
    current_management_user: models.ManagementUser = Depends(get_current_management_user),
) -> dict:
    """
    Clean up expired notifications. Management users only.
    """
    deleted_count = crud.notification.cleanup_expired(db)
    return {"deleted_count": deleted_count}
