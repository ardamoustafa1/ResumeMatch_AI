import pytest
from httpx import AsyncClient
from backend.main import app
from tests.conftest import override_get_db
from backend.db.connection import get_db
from backend.api.deps import get_current_user

pytestmark = pytest.mark.asyncio

class ApiKeyConnection:
    async def fetchrow(self, query, *args):
        # Mock api_keys and users JOIN query
        if "SELECT k.user_id, k.expires_at" in query:
            return {
                "id": "user-uuid",
                "user_id": "user-uuid",
                "email": "extension@example.com",
                "is_active": True,
                "is_superuser": False,
                "email_verified": True,
                "created_at": "2024-01-01",
                "expires_at": None,
                "revoked_at": None,
                "scopes": "extension",
            }
        return None

async def test_extension_api_key_cannot_access_me(client: AsyncClient, mocker):
    connection = ApiKeyConnection()
    async def override():
        yield connection
    
    app.dependency_overrides[get_db] = override
    
    # We must patch token verification to fallback to api key logic
    mocker.patch("jose.jwt.decode", side_effect=Exception("Invalid token"))
    mocker.patch("backend.api.deps.hash_token", return_value="hashed")

    try:
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer ext_fake_token"}
        )
    finally:
        app.dependency_overrides[get_db] = override_get_db

    assert response.status_code == 403
    assert "API key does not have sufficient permissions" in response.json()["detail"]

async def test_extension_api_key_can_access_analysis(client: AsyncClient, mocker):
    connection = ApiKeyConnection()
    async def override():
        yield connection
    
    app.dependency_overrides[get_db] = override
    mocker.patch("jose.jwt.decode", side_effect=Exception("Invalid token"))
    mocker.patch("backend.api.deps.hash_token", return_value="hashed")
    mocker.patch("backend.api.v1.routes.analysis.get_user_analyses", return_value=[])

    try:
        response = await client.get(
            "/api/v1/analysis",
            headers={"Authorization": "Bearer ext_fake_token"}
        )
    finally:
        app.dependency_overrides[get_db] = override_get_db

    # Expecting 200 OK or similar, but definitely not 403 API Scope block
    assert response.status_code != 403
