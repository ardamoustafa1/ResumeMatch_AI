import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from backend.core.websocket_manager import ws_manager

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/analysis/{analysis_id}")
async def analysis_websocket_endpoint(websocket: WebSocket, analysis_id: str):
    """
    Subscribes the client to real-time analysis progress via Redis Pub/Sub.
    """
    await ws_manager.connect(websocket, analysis_id)
    
    try:
        while True:
            try:
                # Wait for any client message, applying a timeout to inject regular heartbeats
                await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send heartbeat every 30 seconds to prevent reverse proxies from closing idle connections
                await websocket.send_json({"step": "heartbeat", "progress": None})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, analysis_id)
        logger.info(f"Client disconnected from analysis stream {analysis_id}")
    except Exception as e:
        ws_manager.disconnect(websocket, analysis_id)
        logger.error(f"WebSocket error for {analysis_id}: {e}")
