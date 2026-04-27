import httpx
import logging
import re
from typing import Optional

from backend.models.schemas import FullAnalysisResult

logger = logging.getLogger(__name__)

# --- Exceptions ---
class TelegramError(Exception):
    """Base exception for Telegram errors."""
    pass

class TelegramNetworkTimeoutError(TelegramError):
    """Raised when httpx network call times out."""
    pass

class TelegramInvalidTokenError(TelegramError):
    """Raised when the Telegram Bot Token is invalid (401)."""
    pass

class TelegramChatNotFoundError(TelegramError):
    """Raised when the Chat ID is invalid or bot has been blocked/removed (400)."""
    pass

# --- Helper Methods ---

def format_message_for_telegram(text: str, truncate_len: int = 0) -> str:
    """
    Escapes special characters required by Telegram MarkdownV2 format.
    MarkdownV2 requires escaping: _ * [ ] ( ) ~ ` > # + - = | { } . !
    We only escape variables. Structural formatting should be written directly in the string.
    """
    if not text:
        return ""
        
    if truncate_len > 0 and len(text) > truncate_len:
        text = text[:truncate_len] + "..."
        
    # Note: escaping \ must happen first if there are any
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


async def _send_message(bot_token: str, chat_id: str, text: str) -> dict:
    """
    Core function to post to Telegram API using Async httpx.
    """
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=10.0)
            data = response.json()
            
            if not data.get("ok"):
                error_code = data.get("error_code")
                description = data.get("description", "")
                
                if error_code == 401:
                    raise TelegramInvalidTokenError("Invalid Telegram bot token.")
                elif error_code == 400 and "chat not found" in description.lower():
                    raise TelegramChatNotFoundError(f"Chat ID {chat_id} not found.")
                else:
                    raise TelegramError(f"Telegram API Error [{error_code}]: {description}")
                    
            return data
            
    except httpx.TimeoutException:
        raise TelegramNetworkTimeoutError("Connection to Telegram API timed out.")
    except httpx.RequestError as e:
        raise TelegramError(f"Network error communicating with Telegram: {e}")


# --- Service Methods ---

async def verify_telegram_config(bot_token: str, chat_id: str) -> bool:
    """
    Sends a test message to verify the configuration.
    Returns True if successfully delivered.
    """
    text = (
        "✅ *NetworkForge Verification*\\n\\n"
        "Your Telegram integration is fully operational\\! 🚀"
    )
    try:
        await _send_message(bot_token, chat_id, text)
        return True
    except TelegramError as e:
        logger.error(f"Telegram verification failed: {e}")
        return False


async def send_error_notification(chat_id: str, bot_token: str, analysis_id: str, error: str) -> None:
    """
    Sends a failure notification.
    """
    safe_analysis_id = format_message_for_telegram(analysis_id)
    safe_error = format_message_for_telegram(str(error), truncate_len=500)
    
    text = (
        "❌ *NetworkForge Analysis Failed*\\n\\n"
        f"Tracking ID: `{safe_analysis_id}`\\n"
        f"Error Details: {safe_error}"
    )
    
    try:
        await _send_message(bot_token, chat_id, text)
    except Exception as e:
        logger.error(f"Failed to send error notification: {e}")


async def send_analysis_complete(
    chat_id: str, 
    bot_token: str, 
    analysis_id: str, 
    company: str, 
    recruiter_name: str, 
    result: FullAnalysisResult
) -> None:
    """
    Sends the formatted summary report upon AI analysis completion.
    """
    safe_id = format_message_for_telegram(analysis_id)
    safe_company = format_message_for_telegram(company) if company else "Not specified"
    safe_recruiter = format_message_for_telegram(recruiter_name) if recruiter_name else "Not specified"
    
    score = result.match_result.score if result.match_result else 0
    
    if result.match_result:
        matched = format_message_for_telegram(", ".join(result.match_result.matched_skills[:5]), truncate_len=100)
        missing = format_message_for_telegram(", ".join(result.match_result.missing_skills[:5]), truncate_len=100)
    else:
        matched = "None"
        missing = "None"
        
    text = (
        "✅ *NetworkForge Analysis Complete*\\n\\n"
        f"🎯 Match Score: *{score}%*\\n"
        f"🏢 Company: {safe_company}\\n"
        f"👤 Recruiter: {safe_recruiter}\\n\\n"
        f"✅ Matched: {matched}\\n"
        f"❌ Missing: {missing}\\n\\n"
    )
    
    if result.outreach_messages:
        text += (
            "📩 *First Contact DM ready*\\n"
            "📅 *Follow\\-up scheduled for Day 7*\\n"
        )
        
    # App URL escaping for markdown
    app_url = f"https://your\\-app/analysis/{safe_id}"
    text += f"🔗 [View full results]({app_url})"
    
    try:
        await _send_message(bot_token, chat_id, text)
    except Exception as e:
        logger.error(f"Failed to send complete notification: {e}")
