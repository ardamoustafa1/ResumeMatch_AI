import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.db.connection import get_db

# --- Mock Database ---
class MockConnection:
    """Mock asyncpg connection to simulate DB operations safely in tests."""
    async def fetchval(self, *args, **kwargs):
        # Return a deterministic UUID string for insert returning id
        return "123e4567-e89b-12d3-a456-426614174000"
        
    async def fetchrow(self, *args, **kwargs):
        # Return a pending analysis by default
        return {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "user_id": "987e6543-e21b-12d3-a456-426614174999",
            "cv_text": "Sample CV",
            "jd_text": "Sample JD",
            "company": "TestCorp",
            "recruiter_name": "Alice",
            "status": "pending",
            "result": None,
            "created_at": "2026-04-27T21:00:00Z"
        }
        
    async def execute(self, *args, **kwargs):
        # Simulate successful UPDATE 1
        return "UPDATE 1"

async def override_get_db() -> AsyncGenerator[MockConnection, None]:
    """Overrides the FastAPI get_db dependency with MockConnection."""
    yield MockConnection()

app.dependency_overrides[get_db] = override_get_db

# --- Async HTTP Client ---
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Yields a test AsyncClient hooked directly into the FastAPI ASGI app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

# --- Standard Fixtures ---
@pytest.fixture
def sample_cv() -> str:
    """Returns a sample CV string long enough to pass Pydantic validation (min 100)."""
    return "This is a sample CV that is intentionally long enough to pass the pydantic validation constraints. " * 5

@pytest.fixture
def sample_jd() -> str:
    """Returns a sample JD string long enough to pass Pydantic validation (min 50)."""
    return "This is a sample Job Description that needs to be long enough. " * 3

@pytest.fixture
def sample_analysis() -> dict:
    return {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "user_id": "987e6543-e21b-12d3-a456-426614174999",
        "status": "pending"
    }

# --- Infrastructure Mocks ---
@pytest.fixture(autouse=True)
def mock_redis(mocker):
    """Automatically mock out Redis pub/sub and Celery task dispatch to prevent hanging tests."""
    mocker.patch("backend.tasks.progress_events.publish_progress_sync", return_value=None)
    mocker.patch("backend.tasks.progress_events.publish_progress", return_value=None)
    mocker.patch("backend.tasks.celery_app.celery_app.send_task", return_value=None)
    mocker.patch("backend.tasks.analysis_tasks.run_analysis_task.delay", return_value=None)
