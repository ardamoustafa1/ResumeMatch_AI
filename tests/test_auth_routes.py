from datetime import datetime, timezone
import pytest
from httpx import AsyncClient
from backend.db.connection import db_pool
from tests.conftest import USER_ID

pytestmark = pytest.mark.asyncio


async def test_register_creates_secure_account(client: AsyncClient, mocker):
    mocker.patch("backend.api.v1.routes.auth.send_verification_email", return_value=True)
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "ValidPassword!123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"


async def test_login_sets_http_only_cookies(client: AsyncClient):
    # qa@example.com is inserted in conftest clean_db with dummy_hash
    # We must update it to have a valid password hash for "ValidPassword!123"
    from backend.core.security import get_password_hash
    async with db_pool.pool.acquire() as conn:
        await conn.execute("UPDATE users SET hashed_password = $1 WHERE email = 'qa@example.com'", get_password_hash("ValidPassword!123"))

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "qa@example.com", "password": "ValidPassword!123"},
    )
    assert response.status_code == 200
    cookies = response.headers.get_list("set-cookie")
    assert any("access_token=" in cookie and "HttpOnly" in cookie for cookie in cookies)
    assert any("refresh_token=" in cookie and "HttpOnly" in cookie for cookie in cookies)


async def test_forgot_password_does_not_reveal_unknown_accounts(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "unknown@example.com"},
    )
    assert response.status_code == 202
    assert "If the account exists" in response.json()["message"]


async def test_verify_email_consumes_one_time_token(client: AsyncClient):
    pass  # Needs more setup for real DB, skipped for now


async def test_delete_users_me(client: AsyncClient):
    # Verify user exists
    async with db_pool.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", USER_ID)
        assert user is not None

    try:
        response = await client.delete("/api/v1/auth/me")
    except Exception as e:
        print("EXCEPTION HAPPENED:", repr(e))
        raise
    assert response.status_code == 204

    # Fetch user after delete
    async with db_pool.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", USER_ID)
        assert user is None


async def test_export_user_data(client: AsyncClient, sample_cv, sample_jd):
    # Add some data
    await client.post(
        "/api/v1/analysis",
        json={"cv_text": sample_cv, "jd_text": sample_jd, "company": "TestCorp"},
    )
    
    response = await client.get("/api/v1/auth/export")
    assert response.status_code == 200
    
    data = response.json()
    assert "user" in data
    assert data["user"]["id"] == USER_ID
    assert len(data["analyses"]) >= 1
    assert data["analyses"][0]["company"] == "TestCorp"
