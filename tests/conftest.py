import os

os.environ["DATABASE_URL"] = (
    "postgresql://postgres:postgres@localhost:5433/resumematch_test"
)
os.environ["REDIS_URL"] = "redis://localhost:6379/1"  # Use DB 1 for testing

from datetime import datetime, timezone
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.api.deps import get_current_user
from backend.db.connection import get_db, db_pool
from backend.main import app
from backend.core.rate_limit import limiter

USER_ID = "987e6543-e21b-12d3-a456-426614174999"
ANALYSIS_ID = "123e4567-e89b-12d3-a456-426614174000"


@pytest_asyncio.fixture(autouse=True)
async def setup_test_pool():
    # Setup test DB pool
    from backend.db.connection import db_pool

    await db_pool.connect()
    yield
    await db_pool.disconnect()


@pytest_asyncio.fixture(autouse=True)
async def clean_db(setup_test_pool):
    # Clean tables before each test
    async with db_pool.pool.acquire() as conn:
        await conn.execute("TRUNCATE TABLE audit_events CASCADE;")
        await conn.execute("TRUNCATE TABLE outreach_messages CASCADE;")
        await conn.execute("TRUNCATE TABLE analyses CASCADE;")
        await conn.execute("TRUNCATE TABLE refresh_tokens CASCADE;")
        await conn.execute("TRUNCATE TABLE api_keys CASCADE;")
        await conn.execute("TRUNCATE TABLE users CASCADE;")

        from backend.core.security import get_password_hash

        # Insert test user
        await conn.execute(
            """
            INSERT INTO users (id, email, hashed_password, is_active)
            VALUES ($1, $2, $3, $4)
            """,
            USER_ID,
            "qa@example.com",
            get_password_hash("ValidPassword!123"),
            True,
        )

    # Clean redis via a fresh client to avoid loop issues
    import redis.asyncio as aioredis

    test_redis = aioredis.from_url(os.environ["REDIS_URL"])
    await test_redis.flushdb()
    await test_redis.aclose()
    yield


async def override_get_db():
    async with db_pool.pool.acquire() as conn:
        yield conn


async def override_current_user() -> dict:
    return {
        "id": USER_ID,
        "email": "qa@example.com",
        "is_active": True,
        "is_superuser": False,
        "email_verified": False,
        "created_at": datetime.now(timezone.utc),
    }


@pytest_asyncio.fixture(autouse=True)
async def mock_redis_client(mocker):
    import redis.asyncio as aioredis

    test_redis = aioredis.from_url(os.environ["REDIS_URL"])
    mocker.patch("backend.tasks.analysis_tasks.async_redis_client", test_redis)
    mocker.patch("backend.tasks.progress_events.async_redis_client", test_redis)
    mocker.patch("backend.api.v1.websocket.async_redis_client", test_redis)
    mocker.patch("backend.api.v1.routes.metrics.async_redis_client", test_redis)
    mocker.patch("backend.main.async_redis_client", test_redis)
    yield
    await test_redis.aclose()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_current_user


@pytest_asyncio.fixture(autouse=True)
async def setup_test_environment():
    limiter.enabled = False
    os.environ["TELEGRAM_BOT_TOKEN"] = "fake:token"
    yield
    limiter.enabled = True


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client


@pytest.fixture
def sample_cv() -> str:
    return (
        "Senior Python engineer experienced with FastAPI, PostgreSQL, Redis, "
        "Docker, observability and reliable asynchronous systems. "
    ) * 4


@pytest.fixture
def sample_jd() -> str:
    return (
        "We need a senior backend engineer with Python, FastAPI, PostgreSQL, "
        "Redis, Docker and cloud experience. "
    ) * 3


@pytest.fixture(autouse=True)
def mock_infrastructure(mocker):
    mocker.patch(
        "backend.tasks.analysis_tasks.run_analysis_task.delay",
        return_value=None,
    )
