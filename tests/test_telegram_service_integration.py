import pytest
from backend.services.telegram_service import TelegramService


@pytest.mark.asyncio
async def test_telegram_service_integration(mocker):
    # Mock httpx.AsyncClient.post
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    mock_post.return_value = mock_response

    service = TelegramService(bot_token="test_token", chat_id="12345")

    # Test send_message
    success = await service.send_message("Test message")
    assert success is True
    mock_post.assert_called_once()

    # Check payload
    args, kwargs = mock_post.call_args
    assert args[0] == "https://api.telegram.org/bottest_token/sendMessage"
    assert kwargs["json"]["chat_id"] == "12345"
    assert kwargs["json"]["text"] == "Test message"

    # Test send_message failure
    mock_post.reset_mock()
    mock_response.status_code = 400
    mock_response.json.return_value = {"ok": False, "description": "Bad Request"}
    mock_post.return_value = mock_response

    success = await service.send_message("Failing message")
    assert success is False
    mock_post.assert_called_once()
