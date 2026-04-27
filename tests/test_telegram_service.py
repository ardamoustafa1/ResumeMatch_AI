import pytest
import respx
from httpx import Response
from backend.services.telegram_service import (
    verify_telegram_config, 
    format_message_for_telegram,
)

pytestmark = pytest.mark.asyncio

def test_send_notification_formats_correctly():
    """Ensure MarkdownV2 critical characters are properly escaped."""
    # Arrange
    text = "Hello_World! (test) [bold] {obj}"
    
    # Act
    formatted = format_message_for_telegram(text)
    
    # Assert
    assert r"\_" in formatted
    assert r"\!" in formatted
    assert r"\(" in formatted
    assert r"\[" in formatted
    assert r"\{" in formatted

@respx.mock
async def test_verify_config_returns_false_on_invalid_token():
    """Ensure HTTP 401s from Telegram are caught and return False correctly."""
    # Arrange
    # Mock httpx using respx
    respx.post("https://api.telegram.org/botinvalid/sendMessage").mock(
        return_value=Response(401, json={"ok": False, "error_code": 401, "description": "Unauthorized"})
    )
    
    # Act
    result = await verify_telegram_config("invalid", "12345")
    
    # Assert
    assert result is False

@respx.mock
async def test_verify_config_returns_true_on_success():
    """Ensure valid responses from Telegram return True."""
    # Arrange
    respx.post("https://api.telegram.org/botvalid/sendMessage").mock(
        return_value=Response(200, json={"ok": True})
    )
    
    # Act
    result = await verify_telegram_config("valid", "12345")
    
    # Assert
    assert result is True
