from httpx import AsyncClient
from backend.main import app
from backend.db.connection import get_db
from backend.api.deps import get_current_user


class ApiKeyConnection:
    async def fetchrow(self, query, *args):
        # Mock api_keys and users JOIN query
        if "SELECT k.id as key_id, k.user_id" in query:
            return {
                "key_id": "key-uuid",
                "id": "user-uuid",
                "user_id": "user-uuid",
                "email": "extension@example.com",
                "is_active": True,
                "is_superuser": False,
                "email_verified": True,
                "created_at": "2024-01-01",
                "expires_at": None,
                "revoked_at": None,
                "scopes": [
                    "extension",
                    "read:analysis",
                    "write:analysis",
                    "extract",
                ],
            }
        return None


async def test_extension_api_key_cannot_access_me(client: AsyncClient, mocker):
    connection = ApiKeyConnection()

    async def override():
        yield connection

    new_overrides = app.dependency_overrides.copy()
    new_overrides.pop(get_current_user, None)
    new_overrides[get_db] = override
    mocker.patch.dict(app.dependency_overrides, new_overrides, clear=True)

    from jose import JWTError

    mocker.patch("jose.jwt.decode", side_effect=JWTError("Invalid token"))
    mocker.patch("backend.api.deps.hash_token", return_value="hashed")
    mocker.patch("fastapi.BackgroundTasks.add_task")

    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer ext_fake_token"}
    )

    assert response.status_code == 403
    assert "API key does not have sufficient permissions" in response.json()["detail"]


async def test_extension_api_key_can_access_analysis(client: AsyncClient, mocker):
    connection = ApiKeyConnection()

    async def override():
        yield connection

    new_overrides = app.dependency_overrides.copy()
    new_overrides.pop(get_current_user, None)
    new_overrides[get_db] = override
    mocker.patch.dict(app.dependency_overrides, new_overrides, clear=True)

    from jose import JWTError

    mocker.patch("jose.jwt.decode", side_effect=JWTError("Invalid token"))
    mocker.patch("backend.api.deps.hash_token", return_value="hashed")
    mocker.patch("fastapi.BackgroundTasks.add_task")
    # Instead of patching get_user_analyses, just mock the fetch
    connection.fetch = mocker.AsyncMock(return_value=[])

    response = await client.get(
        "/api/v1/analysis", headers={"Authorization": "Bearer ext_fake_token"}
    )

    assert response.status_code == 200


async def test_extension_api_key_can_start_analysis(client: AsyncClient, mocker):
    connection = ApiKeyConnection()
    connection.fetchval = mocker.AsyncMock(
        return_value="123e4567-e89b-12d3-a456-426614174000"
    )

    async def override():
        yield connection

    new_overrides = app.dependency_overrides.copy()
    new_overrides.pop(get_current_user, None)
    new_overrides[get_db] = override
    mocker.patch.dict(app.dependency_overrides, new_overrides, clear=True)

    from jose import JWTError

    mocker.patch("jose.jwt.decode", side_effect=JWTError("Invalid token"))
    mocker.patch("backend.api.deps.hash_token", return_value="hashed")
    mocker.patch("fastapi.BackgroundTasks.add_task")
    queue_task = mocker.patch("backend.api.v1.routes.analysis.run_analysis_task.delay")

    response = await client.post(
        "/api/v1/analysis",
        headers={"Authorization": "Bearer ext_fake_token"},
        json={
            "cv_text": "A" * 120,
            "jd_text": "B" * 80,
            "company": "Test Corp",
        },
    )

    assert response.status_code == 202
    queue_task.assert_called_once()
