import asyncio
import logging
import smtplib
from email.message import EmailMessage

from backend.core.config import settings

logger = logging.getLogger(__name__)


def _send_sync(recipient: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_starttls:
            smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)


async def send_email(recipient: str, subject: str, body: str) -> bool:
    if not settings.smtp_host:
        logger.info("Email delivery skipped for %s (SMTP not configured).", recipient)
        return False
    await asyncio.to_thread(_send_sync, recipient, subject, body)
    return True


async def send_verification_email(recipient: str, token: str) -> bool:
    link = f"{settings.frontend_url}/verify-email?token={token}"
    return await send_email(
        recipient,
        "Verify your NetworkForge account",
        f"Verify your account by opening this link:\n\n{link}\n\n"
        "This link expires in 24 hours.",
    )


async def send_password_reset_email(recipient: str, token: str) -> bool:
    link = f"{settings.frontend_url}/reset-password?token={token}"
    return await send_email(
        recipient,
        "Reset your NetworkForge password",
        f"Reset your password by opening this link:\n\n{link}\n\n"
        "This link expires in one hour. Ignore this email if you did not request it.",
    )
