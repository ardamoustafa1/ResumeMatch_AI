from httpx import AsyncClient
from backend.db.connection import db_pool
from tests.conftest import USER_ID


async def test_register_creates_secure_account(client: AsyncClient, mocker):
    mocker.patch(
        "backend.api.v1.routes.auth.send_verification_email", return_value=True
    )
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "ValidPassword!123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "new@example.com"


async def test_login_sets_http_only_cookies(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "qa@example.com", "password": "ValidPassword!123"},
    )
    assert response.status_code == 200
    cookies = response.headers.get_list("set-cookie")
    assert any("access_token=" in cookie and "HttpOnly" in cookie for cookie in cookies)
    assert any(
        "refresh_token=" in cookie and "HttpOnly" in cookie for cookie in cookies
    )
    async with db_pool.pool.acquire() as conn:
        event = await conn.fetchval(
            "SELECT event_type FROM audit_events "
            "WHERE user_id = $1 ORDER BY created_at DESC LIMIT 1",
            USER_ID,
        )
    assert event == "session.login"


async def test_forgot_password_does_not_reveal_unknown_accounts(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "unknown@example.com"},
    )
    assert response.status_code == 202
    assert "If the account exists" in response.json()["message"]


async def test_verify_email_consumes_one_time_token(client: AsyncClient):
    from backend.core.security import create_one_time_token
    from datetime import timedelta

    token, token_hash, expires_at = create_one_time_token(timedelta(hours=1))

    async with db_pool.pool.acquire() as conn:
        # qa@example.com is unverified initially
        await conn.execute(
            "UPDATE users SET email_verified = FALSE WHERE email = 'qa@example.com'"
        )
        user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = 'qa@example.com'"
        )
        await conn.execute(
            "INSERT INTO email_verification_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)",
            user["id"],
            token_hash,
            expires_at,
        )

    # Verify email
    response = await client.post("/api/v1/auth/verify-email", json={"token": token})
    assert response.status_code == 200
    assert response.json()["status"] == "verified"

    # Verify again, should fail
    response2 = await client.post("/api/v1/auth/verify-email", json={"token": token})
    assert response2.status_code == 400


async def test_resend_verification(client: AsyncClient, mocker):
    mocker.patch(
        "backend.api.v1.routes.auth.send_verification_email", return_value=True
    )
    async with db_pool.pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET email_verified = FALSE WHERE email = 'qa@example.com'"
        )

    response = await client.post(
        "/api/v1/auth/resend-verification", json={"email": "qa@example.com"}
    )
    assert response.status_code == 202


async def test_forgot_password_and_reset(client: AsyncClient, mocker):
    mocker.patch(
        "backend.api.v1.routes.auth.send_password_reset_email", return_value=True
    )

    # Request reset
    response = await client.post(
        "/api/v1/auth/forgot-password", json={"email": "qa@example.com"}
    )
    assert response.status_code == 202

    # Instead of extracting the token from the email mock (which is tricky because of the async execution),
    # let's just create a token and insert it directly to test the reset endpoint.
    from backend.core.security import create_one_time_token
    from datetime import timedelta

    token, token_hash, expires_at = create_one_time_token(timedelta(hours=1))
    async with db_pool.pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id FROM users WHERE email = 'qa@example.com'"
        )
        await conn.execute(
            "INSERT INTO password_reset_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)",
            user["id"],
            token_hash,
            expires_at,
        )

    reset_response = await client.post(
        "/api/v1/auth/reset-password",
        json={"token": token, "password": "NewValidPassword!123"},
    )
    assert reset_response.status_code == 200


async def test_delete_users_me(client: AsyncClient):
    # Verify user exists
    async with db_pool.pool.acquire() as conn:
        user = await conn.fetchrow("SELECT * FROM users WHERE id = $1", USER_ID)
        assert user is not None

    response = await client.delete("/api/v1/auth/me")
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


async def test_register_duplicate_email(client: AsyncClient, mocker):
    mocker.patch(
        "backend.api.v1.routes.auth.send_verification_email", return_value=True
    )
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "ValidPassword!123"},
    )
    # Register second
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "dup@example.com", "password": "ValidPassword!123"},
    )
    assert response.status_code == 409


async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "qa@example.com", "password": "WrongPassword!"},
    )
    assert response.status_code == 401


async def test_refresh_token_missing(client: AsyncClient):
    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


async def test_refresh_token_valid(client: AsyncClient):
    # Login to get refresh token
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "qa@example.com", "password": "ValidPassword!123"},
    )
    assert login_resp.status_code == 200
    cookies = login_resp.cookies

    # Refresh
    client.cookies = cookies
    refresh_resp = await client.post("/api/v1/auth/refresh")
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.cookies


async def test_logout(client: AsyncClient):
    from backend.core.security import get_password_hash

    async with db_pool.pool.acquire() as conn:
        await conn.execute(
            "UPDATE users SET hashed_password = $1 WHERE email = 'qa@example.com'",
            get_password_hash("ValidPassword!123"),
        )

    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "qa@example.com", "password": "ValidPassword!123"},
    )
    client.cookies = login_resp.cookies

    logout_resp = await client.post("/api/v1/auth/logout")
    assert logout_resp.status_code == 204
    assert not logout_resp.cookies.get("refresh_token")


async def test_read_users_me(client: AsyncClient):
    response = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 200
    assert "email" in response.json()


async def test_api_keys_crud(client: AsyncClient):
    # Generate API key
    gen_resp = await client.post(
        "/api/v1/auth/api-key", headers={"Authorization": "Bearer fake_token"}
    )
    assert gen_resp.status_code == 200
    key_data = gen_resp.json()
    assert "access_token" in key_data

    # List API keys
    list_resp = await client.get(
        "/api/v1/auth/api-keys", headers={"Authorization": "Bearer fake_token"}
    )
    assert list_resp.status_code == 200
    keys = list_resp.json()
    assert len(keys) >= 1
    key_id = keys[0]["id"]

    # Revoke API key
    rev_resp = await client.delete(
        f"/api/v1/auth/api-keys/{key_id}",
        headers={"Authorization": "Bearer fake_token"},
    )
    assert rev_resp.status_code == 200

    # List again, should be fewer
    list_resp2 = await client.get(
        "/api/v1/auth/api-keys", headers={"Authorization": "Bearer fake_token"}
    )
    assert len(list_resp2.json()) == len(keys) - 1


async def test_refresh_token_theft_scenario(client: AsyncClient):
    # This scenario simulates token family reuse detection.
    # 1. Login to get a valid refresh token.
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "qa@example.com", "password": "ValidPassword!123"},
    )
    assert login_resp.status_code == 200
    cookies = login_resp.cookies
    refresh_token = cookies.get("refresh_token")
    assert refresh_token

    # 2. Refresh it to simulate normal usage (this revokes the first token and gives a new one).
    client.cookies = cookies
    refresh_resp1 = await client.post("/api/v1/auth/refresh")
    assert refresh_resp1.status_code == 200
    new_cookies = refresh_resp1.cookies

    # At this point, the old refresh_token is REVOKED. The new_cookies contain the valid one.

    # 3. Simulate an attacker trying to use the OLD (revoked) refresh token.
    client.cookies = cookies
    refresh_resp2 = await client.post("/api/v1/auth/refresh")

    # Expect a 401 because the token is revoked.
    assert refresh_resp2.status_code == 401
    assert "Invalid refresh token" in refresh_resp2.json()["detail"]

    # 4. As a consequence, ALL refresh tokens for the user should be revoked!
    # So the legitimate user using new_cookies should now fail!
    client.cookies = new_cookies
    refresh_resp3 = await client.post("/api/v1/auth/refresh")
    assert refresh_resp3.status_code == 401
    assert "Invalid refresh token" in refresh_resp3.json()["detail"]
