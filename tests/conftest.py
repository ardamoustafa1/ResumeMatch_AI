from datetime import datetime, timezone
import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.api.deps import get_current_user
from backend.db.connection import get_db
from backend.main import app
from backend.core.rate_limit import limiter

USER_ID = "987e6543-e21b-12d3-a456-426614174999"
ANALYSIS_ID = "123e4567-e89b-12d3-a456-426614174000"


class MockConnection:
    async def fetchval(self, *args, **kwargs):
        return ANALYSIS_ID

    async def fetchrow(self, query, *args, **kwargs):
        if "api_keys" in query:
            return None
        return {
            "id": ANALYSIS_ID,
            "user_id": USER_ID,
            "cv_text": "Sample CV text " * 20,
            "jd_text": "Sample job description " * 10,
            "company": "TestCorp",
            "recruiter_name": "Alice",
            "status": "pending",
            "result": None,
            "created_at": datetime.now(timezone.utc),
        }

    async def fetch(self, *args, **kwargs):
        return []

    async def execute(self, *args, **kwargs):
        return "UPDATE 1"


async def override_get_db() -> AsyncGenerator[MockConnection, None]:
    yield MockConnection()


async def override_current_user() -> dict:
    return {
        "id": USER_ID,
        "email": "qa@example.com",
        "is_active": True,
        "is_superuser": False,
        "email_verified": False,
        "created_at": datetime.now(timezone.utc),
    }


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
