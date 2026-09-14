import json
import asyncio
from typing import Dict, List
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        # Maps WebSocket -> {user_id, zone_ids}
        self.active_connections: Dict[WebSocket, dict] = {}

    async def connect(self, websocket: WebSocket, user_id: str, zone_ids: List[str] = None):
        await websocket.accept()
        self.active_connections[websocket] = {
            "user_id": user_id,
            "zone_ids": zone_ids or [],
        }

    def disconnect(self, websocket: WebSocket):
        self.active_connections.pop(websocket, None)

    async def send_personal(self, websocket: WebSocket, message: dict):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        disconnected = []
        for ws in list(self.active_connections.keys()):
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

    async def broadcast_to_zone(self, zone_id: str, message: dict):
        disconnected = []
        for ws, meta in list(self.active_connections.items()):
            if not meta["zone_ids"] or zone_id in meta["zone_ids"]:
                try:
                    await ws.send_text(json.dumps(message))
                except Exception:
                    disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

    @property
    def connection_count(self) -> int:
        return len(self.active_connections)


manager = ConnectionManager()
