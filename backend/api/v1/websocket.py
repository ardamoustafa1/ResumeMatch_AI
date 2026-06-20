import asyncio
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status, Depends
from jose import JWTError, jwt

from backend.core.security import ALGORITHM, SECRET_KEY
from backend.core.config import settings
from backend.core.websocket_manager import ws_manager
from backend.db.connection import db_pool
from backend.tasks.progress_events import async_redis_client
from backend.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

WS_TICKET_TTL = 60

@router.post("/ticket")
async def generate_ws_ticket(
    analysis_id: str,
    current_user: dict = Depends(get_current_user)
):
    ticket = str(uuid.uuid4())
    redis_key = f"ws_ticket:{ticket}:{analysis_id}"
    await async_redis_client.set(redis_key, current_user["email"], ex=WS_TICKET_TTL)
    return {"ticket": ticket}


async def _authorize(websocket: WebSocket, analysis_id: str) -> bool:
    origin = websocket.headers.get("origin")
    if origin and origin not in settings.allowed_origins:
        return False
        
    ticket = websocket.query_params.get("ticket")
    if not ticket or db_pool.pool is None:
        return False
        
    redis_key = f"ws_ticket:{ticket}:{analysis_id}"
    email_bytes = await async_redis_client.get(redis_key)
    if not email_bytes:
        return False
    
    email = email_bytes.decode("utf-8")
    
    async with db_pool.pool.acquire() as connection:
        owner = await connection.fetchval(
            """
            SELECT 1
            FROM analyses a
            JOIN users u ON u.id = a.user_id
            WHERE a.id = $1::uuid AND u.email = $2 AND u.is_active = TRUE
            """,
            analysis_id,
            email,
        )
    if bool(owner):
        # Burn ticket
        await async_redis_client.delete(redis_key)
        return True
    return False


@router.websocket("/analysis/{analysis_id}")
async def analysis_websocket_endpoint(websocket: WebSocket, analysis_id: str):
    if not await _authorize(websocket, analysis_id):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws_manager.connect(websocket, analysis_id)
    try:
        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                await websocket.send_json(
                    {
                        "analysis_id": analysis_id,
                        "event": "heartbeat",
                        "step": "heartbeat",
                        "progress": None,
                        "message": "Connection active",
                        "data": {},
                    }
                )
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, analysis_id)
    except Exception:
        ws_manager.disconnect(websocket, analysis_id)
        logger.exception("WebSocket error for analysis %s", analysis_id)
