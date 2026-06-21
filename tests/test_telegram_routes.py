"""Tests for Telegram routes."""

from httpx import AsyncClient


async def test_configure_telegram_no_bot_token(client: AsyncClient, mocker):
    """If TELEGRAM_BOT_TOKEN is not set, return 503."""
    mocker.patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": ""})

    response = await client.post(
        "/api/v1/telegram/configure",
        json={"chat_id": "12345", "is_active": True},
    )
    assert response.status_code == 503


async def test_configure_telegram_verification_fails(client: AsyncClient, mocker):
    """If verify_telegram_config returns False, return 400."""
    mocker.patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test_token"})
    mocker.patch(
        "backend.api.v1.routes.telegram.verify_telegram_config",
        return_value=False,
    )

    response = await client.post(
        "/api/v1/telegram/configure",
        json={"chat_id": "12345", "is_active": True},
    )
    assert response.status_code == 400


async def test_configure_telegram_success(client: AsyncClient, mocker):
    """If verification passes, save config and return 200."""
    mocker.patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "test_token"})
    mocker.patch(
        "backend.api.v1.routes.telegram.verify_telegram_config",
        return_value=True,
    )

    response = await client.post(
        "/api/v1/telegram/configure",
        json={"chat_id": "12345", "is_active": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
