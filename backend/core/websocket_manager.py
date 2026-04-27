import json
import logging
from typing import Dict, Set
from fastapi import WebSocket
import asyncio
from backend.tasks.progress_events import async_redis_client

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections and proxies real-time Redis pub/sub events 
    directly to the connected clients for a specific analysis.
    """
    def __init__(self):
        # Mapping of analysis_id -> set of WebSockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, analysis_id: str):
        await websocket.accept()
        if analysis_id not in self.active_connections:
            self.active_connections[analysis_id] = set()
        
        self.active_connections[analysis_id].add(websocket)
        logger.info(f"WebSocket connected for analysis {analysis_id}")
        
        # Spawn a background task to listen to Redis if this is the first client for this analysis
        if len(self.active_connections[analysis_id]) == 1:
            asyncio.create_task(self._listen_to_redis(analysis_id))

    def disconnect(self, websocket: WebSocket, analysis_id: str):
        if analysis_id in self.active_connections:
            self.active_connections[analysis_id].discard(websocket)
            if not self.active_connections[analysis_id]:
                del self.active_connections[analysis_id]
        logger.info(f"WebSocket disconnected for analysis {analysis_id}")

    async def _listen_to_redis(self, analysis_id: str):
        """
        Subscribes to the specific analysis Redis channel and pushes events down the WebSockets.
        """
        channel_name = f"analysis_progress:{analysis_id}"
        pubsub = async_redis_client.pubsub()
        await pubsub.subscribe(channel_name)
        
        logger.info(f"Subscribed to Redis channel: {channel_name}")
        
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = message["data"].decode("utf-8")
                    
                    # Push to all connected clients
                    if analysis_id in self.active_connections:
                        # Copy the set to avoid RuntimeError if changed during iteration
                        websockets = list(self.active_connections[analysis_id])
                        for ws in websockets:
                            try:
                                await ws.send_text(data)
                            except Exception as e:
                                logger.error(f"Error sending to websocket: {e}")
                                self.disconnect(ws, analysis_id)
                                
                    # If process finished, stop listening
                    try:
                        msg_data = json.loads(data)
                        if msg_data.get("step") in ["done", "failed"]:
                            break
                    except json.JSONDecodeError:
                        pass
                        
                # If all clients dropped out, stop listening
                if analysis_id not in self.active_connections:
                    break
        finally:
            await pubsub.unsubscribe(channel_name)
            logger.info(f"Unsubscribed from Redis channel: {channel_name}")

ws_manager = ConnectionManager()
