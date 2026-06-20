from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from backend.core.security import get_password_hash
from backend.db.connection import get_db
from backend.main import app
from tests.conftest import USER_ID, override_get_db

pytestmark = pytest.mark.asyncio


class AuthConnection:
    def __init__(self):
        self.executed: list[tuple] = []

    async def fetchrow(self, query, *args):
        if "SELECT id FROM users" in query:
            return None
        if "INSERT INTO users" in query:
            return {
                "id": USER_ID,
                "email": "new@example.com",
                "is_active": True,
                "is_superuser": False,
                "email_verified": False,
                "created_at": datetime.now(timezone.utc),
            }
        if "hashed_password" in query:
            return {
                "id": USER_ID,
                "email": "qa@example.com",
                "hashed_password": get_password_hash("ValidPassword!123"),
                "is_active": True,
                "email_verified": True,
            }
        return None

    async def execute(self, query, *args):
        self.executed.append((query, *args))
        return "INSERT 0 1"


async def test_register_creates_secure_account(client: AsyncClient, mocker):
    connection = AuthConnection()

    async def override():
        yield connection

    mocker.patch(
        "backend.api.v1.routes.auth.send_verification_email",
        return_value=True,
    )
    app.dependency_overrides[get_db] = override
    try:
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "new@example.com",
                "password": "ValidPassword!123",
            },
        )
    finally:
        app.dependency_overrides[get_db] = override_get_db

    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"
    assert any("email_verification_tokens" in item[0] for item in connection.executed)


async def test_login_sets_http_only_cookies(client: AsyncClient):
    connection = AuthConnection()

    async def override():
        yield connection

    app.dependency_overrides[get_db] = override
    try:
        response = await client.post(
            "/api/v1/auth/login",
            data={
                "username": "qa@example.com",
                "password": "ValidPassword!123",
            },
        )
    finally:
        app.dependency_overrides[get_db] = override_get_db

    assert response.status_code == 200
    cookies = response.headers.get_list("set-cookie")
    assert any("access_token=" in cookie and "HttpOnly" in cookie for cookie in cookies)
    assert any(
        "refresh_token=" in cookie and "HttpOnly" in cookie for cookie in cookies
    )


async def test_forgot_password_does_not_reveal_unknown_accounts(client: AsyncClient):
    connection = AuthConnection()

    async def override():
        yield connection

    app.dependency_overrides[get_db] = override
    try:
        response = await client.post(
            "/api/v1/auth/forgot-password",
            json={"email": "unknown@example.com"},
        )
    finally:
        app.dependency_overrides[get_db] = override_get_db

    assert response.status_code == 202
    assert "If the account exists" in response.json()["message"]


async def test_verify_email_consumes_one_time_token(client: AsyncClient):
    now = datetime.now(timezone.utc)

    class VerifyConnection(AuthConnection):
        async def fetchrow(self, query, *args):
            return {
                "id": "123e4567-e89b-12d3-a456-426614174123",
                "user_id": USER_ID,
                "expires_at": now + timedelta(hours=1),
                "used_at": None,
            }

    connection = VerifyConnection()

    async def override():
        yield connection

    app.dependency_overrides[get_db] = override
    try:
        response = await client.post(
            "/api/v1/auth/verify-email",
            json={"token": "x" * 48},
        )
    finally:
        app.dependency_overrides[get_db] = override_get_db

    assert response.status_code == 200
    assert response.json()["status"] == "verified"
    assert len(connection.executed) == 2
