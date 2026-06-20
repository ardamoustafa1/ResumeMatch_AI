import logging
import os

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, status

from backend.api.deps import get_current_user
from backend.db.connection import get_db
from backend.models.schemas import TelegramConfig
from backend.services.telegram_service import verify_telegram_config

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/configure", status_code=status.HTTP_200_OK)
async def configure_telegram(
    config: TelegramConfig,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram integration is not configured.",
        )
    if not await verify_telegram_config(bot_token, config.chat_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram chat could not be verified.",
        )

    try:
        await conn.execute(
            """
            INSERT INTO telegram_configs (user_id, chat_id, is_active)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id)
            DO UPDATE SET
                chat_id = EXCLUDED.chat_id,
                is_active = EXCLUDED.is_active,
                updated_at = CURRENT_TIMESTAMP
            """,
            current_user["id"],
            config.chat_id,
            config.is_active,
        )
        return {
            "status": "success",
            "message": "Telegram integration verified and saved.",
        }
    except Exception:
        logger.exception("Failed to configure Telegram")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Configuration failed", "code": "CONFIG_ERROR"},
        )
