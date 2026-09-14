from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from typing import Optional
import json
import asyncio

from app.core.websocket_manager import manager
from app.core.security import decode_token
from app.core.redis_client import get_redis_pool

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket, token: Optional[str] = Query(None)):
    # Authenticate WebSocket connection via token query param
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        zone_ids = []  # Could parse from payload or query param
    except Exception:
        await websocket.close(code=4001, reason="Invalid authentication token")
        return

    await manager.connect(websocket, user_id, zone_ids)

    # Send initial connection confirmation
    await manager.send_personal(websocket, {
        "event": "connected",
        "message": "CAT-Guard real-time alerts connected",
        "user_id": user_id,
    })

    redis = await get_redis_pool()
    pubsub = redis.pubsub()
    await pubsub.subscribe("catguard:alerts")

    async def listen_redis():
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        alert_data = json.loads(message["data"])
                        await manager.send_personal(websocket, alert_data)
                    except Exception:
                        pass
        except Exception:
            pass

    redis_task = asyncio.create_task(listen_redis())

    try:
        while True:
            # Keep connection alive, handle client messages (ping/pong)
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send_personal(websocket, {"event": "pong"})
    except WebSocketDisconnect:
        pass
    finally:
        redis_task.cancel()
        await pubsub.unsubscribe("catguard:alerts")
        manager.disconnect(websocket)
