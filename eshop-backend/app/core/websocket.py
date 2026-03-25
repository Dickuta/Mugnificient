import asyncio
import json
from typing import Dict, List, Set
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from starlette.requests import Request
import logging

from app.core.security import get_current_user
from app.models.models import User

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager"""

    def __init__(self):
        # user_id -> set of websockets
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # websocket -> user_id
        self.user_connections: Dict[WebSocket, int] = {}
        # General broadcast connections
        self.broadcast_connections: Set[WebSocket] = set()

    async def connect_user(self, websocket: WebSocket, user_id: int):
        """Connect a user"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()

        self.active_connections[user_id].add(websocket)
        self.user_connections[websocket] = user_id
        logger.info(f"User {user_id} connected via WebSocket")

    async def connect_broadcast(self, websocket: WebSocket):
        """Connect for broadcast messages"""
        await websocket.accept()
        self.broadcast_connections.add(websocket)
        logger.info("New broadcast WebSocket connection")

    def disconnect(self, websocket: WebSocket):
        """Disconnect a websocket"""
        if websocket in self.user_connections:
            user_id = self.user_connections.pop(websocket)
            if user_id in self.active_connections:
                self.active_connections[user_id].discard(websocket)
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected")
        else:
            self.broadcast_connections.discard(websocket)

    async def send_personal(self, user_id: int, message: dict):
        """Send message to specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    disconnected.add(websocket)

            # Remove disconnected
            for ws in disconnected:
                self.active_connections[user_id].discard(ws)

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()
        for websocket in self.broadcast_connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                disconnected.add(websocket)

        for ws in disconnected:
            self.broadcast_connections.discard(ws)

    async def send_order_update(self, user_id: int, order_data: dict):
        """Send order update notification"""
        message = {
            "type": "order_update",
            "data": order_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_personal(user_id, message)

    async def send_stock_alert(self, user_id: int, product_data: dict):
        """Send stock alert notification"""
        message = {
            "type": "stock_alert",
            "data": product_data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.send_personal(user_id, message)

    async def notify_admins(self, message: dict):
        """Send notification to all admin users"""
        # This would require tracking admin user IDs
        # For now, broadcast to all
        await self.broadcast(message)


# Global connection manager
manager = ConnectionManager()


# SSE (Server-Sent Events) for notifications
from fastapi.responses import StreamingResponse
import time


async def notification_stream(request: Request):
    """Server-Sent Events endpoint for notifications"""

    async def event_generator():
        queue = asyncio.Queue()

        # Add queue to a global registry (simplified)
        notification_queues.append(queue)

        try:
            while True:
                if await request.is_disconnected():
                    break

                try:
                    message = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"data: {json.dumps(message)}\n\n"
                except asyncio.TimeoutError:
                    yield f": keepalive\n\n"
        finally:
            notification_queues.remove(queue)

    notification_queues: List[asyncio.Queue] = []

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


# WebSocket endpoint
websocket_router = APIRouter()


@websocket_router.websocket("/ws/notifications")
async def websocket_notifications(websocket: WebSocket):
    """WebSocket endpoint for real-time notifications"""
    user = None

    # Try to get user from query param (token)
    token = websocket.query_params.get("token")
    if token:
        try:
            from app.core.security import decode_token

            payload = decode_token(token)
            from app.core.database import SessionLocal
            from app.models.models import User

            db = SessionLocal()
            user = db.query(User).filter(User.username == payload.get("sub")).first()
            user_id = user.id if user else None
            db.close()
        except Exception as e:
            logger.error(f"WebSocket auth error: {e}")
            user_id = None
    else:
        user_id = None

    if user_id:
        await manager.connect_user(websocket, user_id)
    else:
        await manager.connect_broadcast(websocket)

    try:
        while True:
            # Keep connection alive, wait for messages
            data = await websocket.receive_text()
            # Handle incoming messages if needed
            logger.debug(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@websocket_router.post("/notify/order/{order_id}")
async def notify_order_update(order_id: int):
    """Trigger order update notification (for testing)"""
    # In production, this would be called after order status changes
    await manager.broadcast(
        {
            "type": "order_update",
            "data": {"order_id": order_id, "status": "updated"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    return {"message": "Notification sent"}


@websocket_router.post("/notify/stock/{product_id}")
async def notify_stock_alert(product_id: int):
    """Trigger stock alert notification"""
    await manager.broadcast(
        {
            "type": "stock_alert",
            "data": {"product_id": product_id, "message": "Low stock!"},
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
    return {"message": "Stock alert sent"}
