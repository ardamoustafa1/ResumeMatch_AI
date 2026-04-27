import pytest
from httpx import AsyncClient

# Marks all tests in this file as async
pytestmark = pytest.mark.asyncio

async def test_post_analyze_returns_analysis_id(client: AsyncClient, sample_cv, sample_jd):
    """Ensure successful creation triggers a 202 Accepted and returns an ID."""
    # Arrange
    payload = {
        "cv_text": sample_cv,
        "jd_text": sample_jd,
        "company": "TestCorp"
    }

    # Act
    response = await client.post("/api/v1/analysis", json=payload)

    # Assert
    assert response.status_code == 202
    data = response.json()
    assert "analysis_id" in data
    assert data["status"] == "pending"

async def test_post_analyze_validates_cv_min_length(client: AsyncClient, sample_jd):
    """Ensure Pydantic effectively drops malformed/short CVs before hitting the DB."""
    # Arrange
    payload = {
        "cv_text": "Too short",
        "jd_text": sample_jd
    }

    # Act
    response = await client.post("/api/v1/analysis", json=payload)

    # Assert
    assert response.status_code == 422
    assert "at least 100 characters" in str(response.text) or "String should have at least" in str(response.text)

async def test_get_analysis_returns_pending_status(client: AsyncClient):
    """Ensure retrieving an ongoing analysis returns the proper pending payload."""
    # Arrange
    # conftest override returns a pending record automatically
    analysis_id = "123e4567-e89b-12d3-a456-426614174000"

    # Act
    response = await client.get(f"/api/v1/analysis/{analysis_id}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert "progress" in data

async def test_get_analysis_returns_completed_result(client: AsyncClient, mocker):
    """Ensure completed records return the full AnalysisResponse schema."""
    # Arrange: Override the DB dependency specifically for this test
    class CompletedMockConnection:
        async def fetchrow(self, *args, **kwargs):
            return {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "987e6543-e21b-12d3-a456-426614174999",
                "status": "completed",
                "result": {"match_score": 100, "matched_skills": []},
                "created_at": "2026-04-27T21:00:00Z",
                "cv_text": "", "jd_text": "", "company": "", "recruiter_name": ""
            }
    
    from backend.main import app
    from backend.db.connection import get_db
    
    async def override_get_completed_db():
        yield CompletedMockConnection()
        
    app.dependency_overrides[get_db] = override_get_completed_db

    analysis_id = "123e4567-e89b-12d3-a456-426614174000"

    # Act
    response = await client.get(f"/api/v1/analysis/{analysis_id}")

    # Assert
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["result"]["match_score"] == 100

async def test_get_analysis_404_for_unknown_id(client: AsyncClient, mocker):
    """Ensure fetching a non-existent UUID returns standard 404."""
    # Arrange
    class NotFoundMockConnection:
        async def fetchrow(self, *args, **kwargs):
            return None
    
    from backend.main import app
    from backend.db.connection import get_db
    
    async def override_get_notfound_db():
        yield NotFoundMockConnection()
        
    app.dependency_overrides[get_db] = override_get_notfound_db

    # Act
    response = await client.get("/api/v1/analysis/123e4567-e89b-12d3-a456-426614174000")

    # Assert
    assert response.status_code == 404
