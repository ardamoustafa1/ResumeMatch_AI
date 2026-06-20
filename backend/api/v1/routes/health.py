import asyncio
import logging

from asyncpg import Connection
from fastapi import APIRouter, Depends, Response, status

from backend.db.connection import get_db
from backend.tasks.celery_app import celery_app
from backend.tasks.progress_events import async_redis_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness() -> dict[str, str]:
    return {"status": "alive", "version": "1.0.0"}


@router.get("", status_code=status.HTTP_200_OK)
@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness(
    response: Response,
    conn: Connection = Depends(get_db),
):
    health_status: dict[str, str | int] = {
        "status": "healthy",
        "version": "1.0.0",
        "db": "down",
        "redis": "down",
        "workers": 0,
    }

    try:
        await conn.execute("SELECT 1")
        health_status["db"] = "up"
    except Exception:
        logger.exception("Database readiness check failed")

    try:
        res = async_redis_client.ping()
        if hasattr(res, "__await__"):
            await res
        health_status["redis"] = "up"
    except Exception:
        logger.exception("Redis readiness check failed")

    try:
        inspector = celery_app.control.inspect(timeout=1)
        active_nodes = await asyncio.wait_for(
            asyncio.to_thread(inspector.ping),
            timeout=2,
        )
        if active_nodes:
            health_status["workers"] = len(active_nodes)
    except Exception:
        logger.warning("Celery readiness check failed")

    if (
        health_status["db"] != "up"
        or health_status["redis"] != "up"
        or health_status["workers"] == 0
    ):
        health_status["status"] = "degraded"
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return health_status
