from fastapi import APIRouter, Response, Depends
from backend.db.connection import db_pool
from prometheus_client import generate_latest, Gauge, Counter, REGISTRY
import logging

router = APIRouter()

# Metrics
db_pool_size = Gauge("db_pool_size", "Current database connection pool size")
db_pool_active = Gauge("db_pool_active_connections", "Active database connections")
http_requests_total = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])

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
                res = await conn.fetchrow("SELECT count(*) as active FROM pg_stat_activity WHERE datname = current_database() AND state = 'active'")
                if res and res["active"]:
                    db_pool_active.set(res["active"])
        except Exception as e:
            logging.error(f"Failed to fetch db pool stats for metrics: {e}")
    
    return Response(generate_latest(REGISTRY), media_type="text/plain")
