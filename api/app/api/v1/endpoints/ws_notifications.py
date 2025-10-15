"""WebSocket endpoint for real-time notifications."""

import logging
from typing import Dict, Set
from datetime import datetime

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Query,
    status,
    Depends,
)
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User
from app.models.management_user import ManagementUser
from app.schemas.user import TokenPayload
from app.api.management_deps import get_current_active_management_user

router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for notifications."""

    def __init__(self):
        """Initialize connection manager."""
        # User connections: {user_id: {websocket1, websocket2, ...}}
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        # Management user connections
        self.management_connections: Dict[int, Set[WebSocket]] = {}
        # Tenant connections: {tenant_id: {websocket1, websocket2, ...}}
        self.tenant_connections: Dict[int, Set[WebSocket]] = {}
        
        # Metrics tracking
        self.total_connections = 0
        self.total_disconnections = 0
        self.total_messages_sent = 0
        self.total_errors = 0
        self.connection_start_time = datetime.now()

    async def connect_user(self, websocket: WebSocket, user_id: int, tenant_id: int):
        """Connect a user WebSocket."""
        await websocket.accept()

        # Add to user connections
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)

        # Add to tenant connections
        if tenant_id not in self.tenant_connections:
            self.tenant_connections[tenant_id] = set()
        self.tenant_connections[tenant_id].add(websocket)
        
        # Update metrics
        self.total_connections += 1

        logger.info(f"User {user_id} (tenant {tenant_id}) connected to WebSocket")

    async def connect_management_user(
        self, websocket: WebSocket, management_user_id: int
    ):
        """Connect a management user WebSocket."""
        await websocket.accept()

        if management_user_id not in self.management_connections:
            self.management_connections[management_user_id] = set()
        self.management_connections[management_user_id].add(websocket)
        
        # Update metrics
        self.total_connections += 1

        logger.info(
            f"Management user {management_user_id} " f"connected to WebSocket"
        )

    def disconnect_user(self, websocket: WebSocket, user_id: int, tenant_id: int):
        """Disconnect a user WebSocket."""
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        if tenant_id in self.tenant_connections:
            self.tenant_connections[tenant_id].discard(websocket)
            if not self.tenant_connections[tenant_id]:
                del self.tenant_connections[tenant_id]
        
        # Update metrics
        self.total_disconnections += 1

        logger.info(f"User {user_id} (tenant {tenant_id}) disconnected from WebSocket")

    def disconnect_management_user(
        self, websocket: WebSocket, management_user_id: int
    ):
        """Disconnect a management user WebSocket."""
        if management_user_id in self.management_connections:
            self.management_connections[management_user_id].discard(websocket)
            if not self.management_connections[management_user_id]:
                del self.management_connections[management_user_id]
        
        # Update metrics
        self.total_disconnections += 1

        logger.info(
            f"Management user {management_user_id} " f"disconnected from WebSocket"
        )

    async def send_to_user(self, user_id: int, message: dict):
        """Send message to a specific user."""
        if user_id in self.user_connections:
            disconnected = set()
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_json(message)
                    self.total_messages_sent += 1
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    self.total_errors += 1
                    disconnected.add(websocket)

            # Clean up disconnected websockets
            for ws in disconnected:
                self.user_connections[user_id].discard(ws)

    async def send_to_management_user(
        self, management_user_id: int, message: dict
    ):
        """Send message to a specific management user."""
        if management_user_id in self.management_connections:
            disconnected = set()
            for websocket in self.management_connections[
                management_user_id
            ]:
                try:
                    await websocket.send_json(message)
                    self.total_messages_sent += 1
                except Exception as e:
                    logger.error(
                        f"Error sending to management user "
                        f"{management_user_id}: {e}"
                    )
                    self.total_errors += 1
                    disconnected.add(websocket)

            # Clean up disconnected websockets
            for ws in disconnected:
                self.management_connections[management_user_id].discard(ws)

    async def send_to_tenant(self, tenant_id: int, message: dict):
        """Send message to all users in a tenant."""
        if tenant_id in self.tenant_connections:
            disconnected = set()
            for websocket in self.tenant_connections[tenant_id]:
                try:
                    await websocket.send_json(message)
                    self.total_messages_sent += 1
                except Exception as e:
                    logger.error(
                        f"Error sending to tenant {tenant_id}: {e}"
                    )
                    self.total_errors += 1
                    disconnected.add(websocket)

            # Clean up disconnected websockets
            for ws in disconnected:
                self.tenant_connections[tenant_id].discard(ws)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected users."""
        all_connections = set()
        for connections in self.user_connections.values():
            all_connections.update(connections)
        for connections in self.management_connections.values():
            all_connections.update(connections)

        disconnected = set()
        for websocket in all_connections:
            try:
                await websocket.send_json(message)
                self.total_messages_sent += 1
            except Exception as e:
                logger.error(f"Error broadcasting: {e}")
                self.total_errors += 1
                disconnected.add(websocket)
    
    def get_metrics(self) -> dict:
        """Get current WebSocket metrics."""
        total_users = len(self.user_connections)
        total_management = len(self.management_connections)
        total_active = sum(
            len(conns) for conns in self.user_connections.values()
        ) + sum(
            len(conns) for conns in self.management_connections.values()
        )
        
        uptime = (datetime.now() - self.connection_start_time).total_seconds()
        
        return {
            "active_connections": total_active,
            "connected_users": total_users,
            "connected_management_users": total_management,
            "connected_tenants": len(self.tenant_connections),
            "total_connections": self.total_connections,
            "total_disconnections": self.total_disconnections,
            "total_messages_sent": self.total_messages_sent,
            "total_errors": self.total_errors,
            "uptime_seconds": uptime,
        }


# Global connection manager instance
manager = ConnectionManager()


def get_db_for_websocket():
    """Get database session for WebSocket."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


async def authenticate_websocket_user(token: str, db: Session) -> User:
    """Authenticate user from WebSocket token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, Exception) as e:
        logger.error(f"Token validation failed: {e}")
        raise ValueError("Could not validate credentials")

    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("Inactive user")

    return user


async def authenticate_websocket_management_user(
    token: str, db: Session
) -> ManagementUser:
    """Authenticate management user from WebSocket token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, Exception) as e:
        logger.error(f"Token validation failed: {e}")
        raise ValueError("Could not validate credentials")

    management_user = (
        db.query(ManagementUser).filter(ManagementUser.id == token_data.sub).first()
    )

    if not management_user:
        raise ValueError("Management user not found")

    if not management_user.is_active:
        raise ValueError("Inactive management user")

    return management_user


@router.websocket("/ws/notifications")
async def websocket_notifications_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
    user_type: str = Query("user", description="Type of user: 'user' or 'management'"),
):
    """
    WebSocket endpoint for real-time notifications.

    Usage:
    - Connect with JWT token as query parameter:
      ws://host/api/v1/ws/notifications?token=YOUR_JWT_TOKEN
    - For management users:
      ws://host/api/v1/ws/notifications?token=JWT&user_type=management
    - Receive notifications as JSON messages in real-time

    Message format:
    {
        "type": "notification",
        "data": {
            "id": 1,
            "title": "Notification title",
            "message": "Notification message",
            "notification_type": "info",
            "created_at": "2024-01-01T00:00:00",
            ...
        }
    }
    """
    db = get_db_for_websocket()

    try:
        if user_type == "management":
            # Authenticate management user
            try:
                management_user = await authenticate_websocket_management_user(
                    token, db
                )
            except ValueError as e:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION, reason=str(e)
                )
                return

            # Connect management user
            await manager.connect_management_user(websocket, management_user.id)

            # Send welcome message
            await websocket.send_json(
                {
                    "type": "connected",
                    "message": (
                        f"Welcome, {management_user.email}! "
                        f"You are now connected to notifications."
                    ),
                    "user_type": "management",
                }
            )

            try:
                # Keep connection alive and handle incoming messages
                while True:
                    data = await websocket.receive_text()
                    # Echo back or handle ping/pong
                    if data == "ping":
                        await websocket.send_json({"type": "pong"})
            except WebSocketDisconnect:
                manager.disconnect_management_user(websocket, management_user.id)
        else:
            # Authenticate regular user
            try:
                user = await authenticate_websocket_user(token, db)
            except ValueError as e:
                await websocket.close(
                    code=status.WS_1008_POLICY_VIOLATION, reason=str(e)
                )
                return

            # Connect user
            await manager.connect_user(websocket, user.id, user.tenant_id)

            # Send welcome message
            await websocket.send_json(
                {
                    "type": "connected",
                    "message": (
                        f"Welcome, {user.email}! "
                        f"You are now connected to notifications."
                    ),
                    "user_type": "user",
                }
            )

            try:
                # Keep connection alive and handle incoming messages
                while True:
                    data = await websocket.receive_text()
                    # Echo back or handle ping/pong
                    if data == "ping":
                        await websocket.send_json({"type": "pong"})
            except WebSocketDisconnect:
                manager.disconnect_user(websocket, user.id, user.tenant_id)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        except Exception:
            pass
    finally:
        db.close()


# Helper function to be used by notification creation endpoints
async def broadcast_notification_to_user(user_id: int, notification_data: dict):
    """
    Broadcast a notification to a specific user via WebSocket.
    Call this function when creating a new notification.
    """
    await manager.send_to_user(
        user_id, {"type": "notification", "data": notification_data}
    )


async def broadcast_notification_to_management_user(
    management_user_id: int, notification_data: dict
):
    """
    Broadcast a notification to a specific management user via WebSocket.
    Call this function when creating a new notification.
    """
    await manager.send_to_management_user(
        management_user_id, {"type": "notification", "data": notification_data}
    )


async def broadcast_notification_to_tenant(tenant_id: int, notification_data: dict):
    """
    Broadcast a notification to all users in a tenant via WebSocket.
    Call this function when creating a tenant-wide notification.
    """
    await manager.send_to_tenant(
        tenant_id, {"type": "notification", "data": notification_data}
    )


async def broadcast_system_notification(notification_data: dict):
    """
    Broadcast a system-wide notification to all connected users.
    Call this function when creating a system-wide notification.
    """
    await manager.broadcast({"type": "notification", "data": notification_data})


# Metrics endpoint for monitoring
@router.get("/ws/metrics")
def get_websocket_metrics(
    current_user=Depends(get_current_active_management_user),
):
    """
    Get WebSocket connection metrics and monitoring data.
    Management users only.
    """
    return manager.get_metrics()
