import os
import json
import redis.asyncio as redis
import redis as sync_redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Sync redis client for Celery workers
sync_redis_client = sync_redis.from_url(REDIS_URL)

def publish_progress_sync(analysis_id: str, step: str, percent: int, data: dict = None) -> None:
    """
    Publish real-time progress to a Redis pub/sub channel synchronously.
    Used by the Celery worker to push events during the analysis pipeline.
    """
    channel = f"analysis_progress:{analysis_id}"
    message = {
        "analysis_id": analysis_id,
        "step": step,
        "progress": percent,
        "data": data or {}
    }
    sync_redis_client.publish(channel, json.dumps(message))

# Async redis client for FastAPI WebSocket Manager
async_redis_client = redis.from_url(REDIS_URL)

async def publish_progress(analysis_id: str, step: str, percent: int, data: dict = None) -> None:
    """
    Publish real-time progress to a Redis pub/sub channel asynchronously.
    """
    channel = f"analysis_progress:{analysis_id}"
    message = {
        "analysis_id": analysis_id,
        "step": step,
        "progress": percent,
        "data": data or {}
    }
    await async_redis_client.publish(channel, json.dumps(message))
