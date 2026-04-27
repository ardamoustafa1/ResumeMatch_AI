import logging
from fastapi import APIRouter, Depends, HTTPException, status
from asyncpg import Connection

from backend.db.connection import get_db
from backend.models.schemas import TelegramConfig

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/configure", status_code=status.HTTP_200_OK)
async def configure_telegram(
    config: TelegramConfig,
    conn: Connection = Depends(get_db)
):
    try:
        # Upsert the telegram config into the database
        query = """
            INSERT INTO telegram_configs (user_id, chat_id, is_active)
            VALUES ($1::uuid, $2, $3)
            ON CONFLICT (user_id) 
            DO UPDATE SET chat_id = EXCLUDED.chat_id, is_active = EXCLUDED.is_active, updated_at = CURRENT_TIMESTAMP;
        """
        await conn.execute(query, config.user_id, config.chat_id, config.is_active)
        
        # Placeholder for verifying config via API
        # e.g. await send_telegram_message(config.chat_id, "NetworkForge integration successful!")
        
        return {
            "status": "success",
            "message": "Telegram configured successfully. A test message would be sent here."
        }
    except Exception as e:
        logger.error(f"Failed to configure telegram: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Configuration failed", "code": "CONFIG_ERROR", "detail": str(e)}
        )
