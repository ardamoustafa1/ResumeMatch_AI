from fastapi import APIRouter, Response
from backend.db.connection import db_pool
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest
import logging

from backend.core.prometheus_metrics import (
    celery_queue_depth,
    db_pool_active,
    db_pool_size,
)
from backend.tasks.progress_events import async_redis_client

router = APIRouter()


@router.get("")
async def get_metrics():
    """
    Export Prometheus metrics.
    """
    if db_pool.pool:
        # asyncpg doesn't expose all stats natively but we can check sizes
        db_pool_size.set(db_pool.pool.get_max_size())
        # To get accurate idle/active count we might need internals or queries:
        try:
            async with db_pool.pool.acquire() as conn:
                res = await conn.fetchrow(
                    "SELECT count(*) as active FROM pg_stat_activity WHERE datname = current_database() AND state = 'active'"
                )
                if res and res["active"]:
                    db_pool_active.set(res["active"])
        except Exception as e:
            logging.error(f"Failed to fetch db pool stats for metrics: {e}")

    for queue in ("celery", "high_priority", "low_priority"):
        try:
            celery_queue_depth.labels(queue=queue).set(
                await async_redis_client.llen(queue)
            )
        except Exception as exc:
            logging.error("Failed to fetch queue depth for %s: %s", queue, exc)

    return Response(generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
