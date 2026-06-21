import pytest
from httpx import Response, Request, TimeoutException, RequestError
from backend.services.telegram_service import (
    format_message_for_telegram,
    _send_message,
    verify_telegram_config,
    send_error_notification,
    send_analysis_complete,
    TelegramError,
    TelegramNetworkTimeoutError,
    TelegramInvalidTokenError,
    TelegramChatNotFoundError,
)
from backend.models.schemas import FullAnalysisResult, MatchResult, OutreachMessages


def test_format_message_for_telegram():
    assert format_message_for_telegram(None) == ""
    assert format_message_for_telegram("Hello _ World") == "Hello \\_ World"
    assert format_message_for_telegram("abc", truncate_len=2) == "ab\\.\\.\\."


async def test_send_message_success(mocker):
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {"ok": True}
    mock_post.return_value = mock_response

    result = await _send_message("fake_token", "fake_chat", "Hello")
    assert result == {"ok": True}


async def test_send_message_invalid_token(mocker):
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {
        "ok": False,
        "error_code": 401,
        "description": "Unauthorized",
    }
    mock_post.return_value = mock_response

    with pytest.raises(TelegramInvalidTokenError):
        await _send_message("fake_token", "fake_chat", "Hello")


async def test_send_message_chat_not_found(mocker):
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {
        "ok": False,
        "error_code": 400,
        "description": "chat not found",
    }
    mock_post.return_value = mock_response

    with pytest.raises(TelegramChatNotFoundError):
        await _send_message("fake_token", "fake_chat", "Hello")


async def test_send_message_other_error(mocker):
    mock_post = mocker.patch("httpx.AsyncClient.post")
    mock_response = mocker.Mock(spec=Response)
    mock_response.json.return_value = {
        "ok": False,
        "error_code": 500,
        "description": "Server Error",
    }
    mock_post.return_value = mock_response

    with pytest.raises(TelegramError):
        await _send_message("fake_token", "fake_chat", "Hello")


async def test_send_message_timeout(mocker):
    mocker.patch(
        "httpx.AsyncClient.post",
        side_effect=TimeoutException("timeout"),
    )

    with pytest.raises(TelegramNetworkTimeoutError):
        await _send_message("fake_token", "fake_chat", "Hello")


async def test_send_message_request_error(mocker):
    mocker.patch(
        "httpx.AsyncClient.post",
        side_effect=RequestError(
            "error",
            request=mocker.Mock(spec=Request),
        ),
    )

    with pytest.raises(TelegramError):
        await _send_message("fake_token", "fake_chat", "Hello")


async def test_verify_telegram_config(mocker):
    mocker.patch(
        "backend.services.telegram_service._send_message", return_value={"ok": True}
    )
    assert await verify_telegram_config("bot", "chat") is True


async def test_verify_telegram_config_fail(mocker):
    mocker.patch(
        "backend.services.telegram_service._send_message",
        side_effect=TelegramError("fail"),
    )
    assert await verify_telegram_config("bot", "chat") is False


async def test_send_error_notification(mocker):
    mock_send = mocker.patch("backend.services.telegram_service._send_message")
    await send_error_notification("chat", "bot", "id123", "Some error")
    mock_send.assert_called_once()


async def test_send_error_notification_fail(mocker):
    mocker.patch(
        "backend.services.telegram_service._send_message",
        side_effect=Exception("fail"),
    )
    # Should not raise
    await send_error_notification("chat", "bot", "id123", "Some error")


async def test_send_analysis_complete(mocker):
    mock_send = mocker.patch("backend.services.telegram_service._send_message")

    result = FullAnalysisResult(
        match_result=MatchResult(
            score=85,
            match_reasoning="Good",
            matched_skills=["Python", "Go"],
            missing_skills=["Rust"],
            improvement_suggestions=[],
        ),
        outreach_messages=OutreachMessages(
            dm_first_contact="Hi", dm_follow_up="Bump", connection_note="Connect"
        ),
    )

    await send_analysis_complete("chat", "bot", "id123", "TechCorp", "Alice", result)
    mock_send.assert_called_once()


async def test_send_analysis_complete_fail(mocker):
    mocker.patch(
        "backend.services.telegram_service._send_message",
        side_effect=Exception("fail"),
    )

    result = FullAnalysisResult(match_result=None, outreach_messages=None)

    # Should not raise
    await send_analysis_complete("chat", "bot", "id123", "", "", result)
