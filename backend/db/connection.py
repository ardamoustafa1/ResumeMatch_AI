import asyncio
import logging
import os
from typing import AsyncGenerator
import asyncpg
from asyncpg.pool import Pool

logger = logging.getLogger(__name__)

# Fetch from settings, fallback to localhost
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/networkforge")

class DatabasePool:
    """
    Manages the asyncpg connection pool lifecycle with robust retry logic.
    """
    def __init__(self) -> None:
        self.pool: Pool | None = None

    async def connect(self, retries: int = 5, backoff_factor: float = 2.0) -> None:
        """
        Initialize the asyncpg connection pool with exponential backoff.
        
        Args:
            retries (int): Maximum number of retry attempts.
            backoff_factor (float): Multiplier for the delay between retries.
        """
        for attempt in range(1, retries + 1):
            try:
                logger.info(f"Connecting to database (Attempt {attempt}/{retries})...")
                self.pool = await asyncpg.create_pool(
                    dsn=DATABASE_URL,
                    min_size=5,
                    max_size=20,
                    command_timeout=60.0,
                )
                logger.info("Database connection pool established successfully.")
                return
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                if attempt == retries:
                    logger.error("Max retries reached. Could not connect to database.")
                    raise
                sleep_time = backoff_factor ** attempt
                logger.info(f"Retrying in {sleep_time} seconds...")
                await asyncio.sleep(sleep_time)

    async def disconnect(self) -> None:
        """
        Gracefully close the database connection pool.
        """
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed.")

db_pool = DatabasePool()

async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """
    FastAPI dependency to acquire a database connection from the pool.
    Yields the connection and releases it back to the pool automatically.
    """
    if db_pool.pool is None:
        raise RuntimeError("Database pool is not initialized")
    
    async with db_pool.pool.acquire() as connection:
        yield connection
