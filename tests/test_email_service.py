import pytest
from unittest.mock import patch, MagicMock, call
from backend.services.email_service import _send_sync, send_email, send_verification_email, send_password_reset_email

from unittest.mock import MagicMock

def test_send_sync(mocker):
    # Mock settings
    mock_settings = MagicMock()
    mock_settings.smtp_host = "smtp.test.com"
    mock_settings.smtp_port = 587
    mock_settings.smtp_starttls = True
    mock_settings.smtp_username = "testuser"
    mock_settings.smtp_password = "testpass"
    mock_settings.smtp_from = "noreply@test.com"
    mocker.patch("backend.services.email_service.settings", mock_settings)

    # Mock smtplib.SMTP
    mock_smtp_instance = MagicMock()
    mock_smtp = mocker.patch("backend.services.email_service.smtplib.SMTP", return_value=mock_smtp_instance)
    mock_smtp_instance.__enter__.return_value = mock_smtp_instance

    _send_sync("test@example.com", "Test Subject", "Test Body")

    mock_smtp.assert_called_once_with("smtp.test.com", 587, timeout=10)
    mock_smtp_instance.starttls.assert_called_once()
    mock_smtp_instance.login.assert_called_once_with("testuser", "testpass")
    mock_smtp_instance.send_message.assert_called_once()
    
    # Check the email message
    sent_message = mock_smtp_instance.send_message.call_args[0][0]
    assert sent_message["From"] == "noreply@test.com"
    assert sent_message["To"] == "test@example.com"
    assert sent_message["Subject"] == "Test Subject"
    assert sent_message.get_content().strip() == "Test Body"


def test_send_sync_no_tls_no_auth(mocker):
    # Mock settings with no TLS and no Auth
    mock_settings = MagicMock()
    mock_settings.smtp_host = "smtp.test.com"
    mock_settings.smtp_port = 25
    mock_settings.smtp_starttls = False
    mock_settings.smtp_username = ""
    mock_settings.smtp_password = ""
    mock_settings.smtp_from = "noreply@test.com"
    mocker.patch("backend.services.email_service.settings", mock_settings)

    mock_smtp_instance = MagicMock()
    mocker.patch("backend.services.email_service.smtplib.SMTP", return_value=mock_smtp_instance)
    mock_smtp_instance.__enter__.return_value = mock_smtp_instance

    _send_sync("test@example.com", "Subject", "Body")

    mock_smtp_instance.starttls.assert_not_called()
    mock_smtp_instance.login.assert_not_called()
    mock_smtp_instance.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_skipped(mocker):
    mock_settings = MagicMock()
    mock_settings.smtp_host = ""
    mocker.patch("backend.services.email_service.settings", mock_settings)
    mock_send_sync = mocker.patch("backend.services.email_service._send_sync")
    
    result = await send_email("test@example.com", "Subject", "Body")
    
    assert result is False
    mock_send_sync.assert_not_called()


@pytest.mark.asyncio
async def test_send_email_success(mocker):
    mock_settings = MagicMock()
    mock_settings.smtp_host = "smtp.test.com"
    mocker.patch("backend.services.email_service.settings", mock_settings)
    mock_send_sync = mocker.patch("backend.services.email_service._send_sync")
    
    result = await send_email("test@example.com", "Subject", "Body")
    
    assert result is True
    mock_send_sync.assert_called_once_with("test@example.com", "Subject", "Body")


@pytest.mark.asyncio
async def test_send_verification_email(mocker):
    mock_settings = MagicMock()
    mock_settings.frontend_url = "https://app.test.com"
    mocker.patch("backend.services.email_service.settings", mock_settings)
    mock_send_email = mocker.patch("backend.services.email_service.send_email", return_value=True)
    
    result = await send_verification_email("user@example.com", "fake_token_123")
    
    assert result is True
    mock_send_email.assert_called_once()
    args = mock_send_email.call_args[0]
    assert args[0] == "user@example.com"
    assert "Verify your ResumeMatch AI account" in args[1]
    assert "https://app.test.com/verify-email?token=fake_token_123" in args[2]


@pytest.mark.asyncio
async def test_send_password_reset_email(mocker):
    mock_settings = MagicMock()
    mock_settings.frontend_url = "https://app.test.com"
    mocker.patch("backend.services.email_service.settings", mock_settings)
    mock_send_email = mocker.patch("backend.services.email_service.send_email", return_value=True)
    
    result = await send_password_reset_email("user@example.com", "reset_token_456")
    
    assert result is True
    mock_send_email.assert_called_once()
    args = mock_send_email.call_args[0]
    assert args[0] == "user@example.com"
    assert "Reset your ResumeMatch AI password" in args[1]
    assert "https://app.test.com/reset-password?token=reset_token_456" in args[2]
