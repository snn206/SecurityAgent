"""WebSocket connection manager for real-time execution event broadcasting."""

from __future__ import annotations

import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections per execution_id."""

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, execution_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.setdefault(execution_id, []).append(websocket)

    def disconnect(self, execution_id: str, websocket: WebSocket) -> None:
        conns = self._connections.get(execution_id, [])
        if websocket in conns:
            conns.remove(websocket)

    async def broadcast(self, execution_id: str, message: dict[str, Any]) -> None:
        """Broadcast a message to all subscribers of this execution_id."""
        conns = self._connections.get(execution_id, [])
        dead = []
        for ws in conns:
            try:
                await ws.send_text(json.dumps(message, default=str))
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(execution_id, ws)

    async def close_all(self) -> None:
        for conns in self._connections.values():
            for ws in conns:
                try:
                    await ws.close()
                except Exception:
                    pass
        self._connections.clear()
