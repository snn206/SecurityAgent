"""WebSocket event router — real-time execution events."""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from security_agent.api.websocket.manager import ConnectionManager

ws_router = APIRouter()
_manager: ConnectionManager | None = None


def get_manager() -> ConnectionManager:
    global _manager
    if _manager is None:
        _manager = ConnectionManager()
    return _manager


@ws_router.websocket("/ws/{execution_id}")
async def websocket_endpoint(websocket: WebSocket, execution_id: str) -> None:
    """WebSocket endpoint — subscribe to events for an execution_id."""
    manager = get_manager()
    await manager.connect(execution_id, websocket)
    try:
        while True:
            # Keep connection alive; client can also send pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(execution_id, websocket)
