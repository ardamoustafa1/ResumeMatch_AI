#!/usr/bin/env python3
"""
Purge old analysis data for GDPR / Data Retention compliance.
Deletes analyses older than 30 days.

Usage:
    docker compose exec api python scripts/purge_old_data.py
    # or set up as a cron job:
    # 0 0 * * * cd /path/to/repo && docker compose exec -T api python scripts/purge_old_data.py
"""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from backend.db.connection import db_pool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RETENTION_DAYS = 30

async def purge_old_data():
    await db_pool.connect()
    if not db_pool.pool:
        logger.error("Failed to connect to DB.")
        return

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)
    logger.info(f"Purging data older than {cutoff_date.isoformat()}")

    async with db_pool.pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM analyses WHERE created_at < $1", cutoff_date
        )
        logger.info(f"Purge complete. Result: {result}")

    await db_pool.disconnect()

if __name__ == "__main__":
    asyncio.run(purge_old_data())
