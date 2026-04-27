import logging
from fastapi import APIRouter, Depends, status
from asyncpg import Connection

from backend.db.connection import get_db
from backend.tasks.celery_app import celery_app
from backend.tasks.progress_events import async_redis_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("", status_code=status.HTTP_200_OK)
async def health_check(conn: Connection = Depends(get_db)):
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "db": "down",
        "redis": "down",
        "workers": 0
    }
    
    # Check Postgres Connection
    try:
        await conn.execute("SELECT 1")
        health_status["db"] = "up"
    except Exception as e:
        logger.error(f"DB health check failed: {e}")
        health_status["status"] = "degraded"
        
    # Check Redis Connection
    try:
        await async_redis_client.ping()
        health_status["redis"] = "up"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        health_status["status"] = "degraded"
        
    # Check Celery Worker Count
    try:
        i = celery_app.control.inspect()
        active_nodes = i.ping()
        if active_nodes:
            health_status["workers"] = len(active_nodes)
        else:
            health_status["status"] = "degraded"
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        health_status["status"] = "degraded"
        
    return health_status
