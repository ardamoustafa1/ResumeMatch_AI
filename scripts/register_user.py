"""Create a local development user from environment variables."""

import asyncio
import os

from backend.core.security import get_password_hash
from backend.db.connection import db_pool


async def main() -> None:
    email = os.getenv("DEV_USER_EMAIL")
    password = os.getenv("DEV_USER_PASSWORD")
    if not email or not password:
        raise SystemExit("Set DEV_USER_EMAIL and DEV_USER_PASSWORD.")

    await db_pool.connect(retries=1)
    assert db_pool.pool is not None
    try:
        async with db_pool.pool.acquire() as connection:
            await connection.execute(
                """
                INSERT INTO users (email, hashed_password, email_verified)
                VALUES ($1, $2, TRUE)
                ON CONFLICT (email) DO UPDATE
                SET hashed_password = EXCLUDED.hashed_password,
                    email_verified = TRUE,
                    updated_at = CURRENT_TIMESTAMP
                """,
                email.lower(),
                get_password_hash(password),
            )
    finally:
        await db_pool.disconnect()
    print(f"Development user ready: {email.lower()}")


if __name__ == "__main__":
    asyncio.run(main())
