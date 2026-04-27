import asyncio
import os
import uuid
import sys

sys.path.insert(0, '/app')

from backend.db.connection import db_pool, DATABASE_URL
from backend.services.telegram_service import verify_telegram_config

async def main():
    print(f"Connecting to {DATABASE_URL}...")
    await db_pool.connect(retries=1)
    
    chat_id = "1857022853"
    
    async with db_pool.pool.acquire() as conn:
        # 1. Create a dummy user
        user_id = str(uuid.uuid4())
        await conn.execute("INSERT INTO users (id, email) VALUES ($1::uuid, $2)", user_id, f"test_{user_id[:8]}@example.com")
        print(f"Created test user: {user_id}")
        
        # 2. Add Telegram config
        await conn.execute("""
            INSERT INTO telegram_configs (user_id, chat_id, is_active) 
            VALUES ($1::uuid, $2, true)
        """, user_id, chat_id)
        print(f"Registered Telegram Chat ID {chat_id} for user {user_id}")
        
    await db_pool.disconnect()
    
    # 3. Test sending message
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("TELEGRAM_BOT_TOKEN not set in environment.")
        return
        
    print("Testing Telegram message delivery...")
    success = await verify_telegram_config(bot_token, chat_id)
    if success:
        print("✅ Test message sent successfully to Telegram!")
    else:
        print("❌ Failed to send test message.")

if __name__ == "__main__":
    asyncio.run(main())
