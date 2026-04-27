import asyncio
import sys
sys.path.insert(0, '/app')

from backend.db.connection import db_pool

async def main():
    await db_pool.connect(retries=1)
    
    user_id = "00000000-0000-0000-0000-000000000000"
    chat_id = "1857022853"
    
    async with db_pool.pool.acquire() as conn:
        # Create default mock user
        await conn.execute("INSERT INTO users (id, email) VALUES ($1::uuid, 'default@example.com') ON CONFLICT DO NOTHING", user_id)
        
        # Link chat ID to default user
        await conn.execute("""
            INSERT INTO telegram_configs (user_id, chat_id, is_active) 
            VALUES ($1::uuid, $2, true)
            ON CONFLICT (user_id) DO UPDATE SET chat_id = EXCLUDED.chat_id
        """, user_id, chat_id)
        
    await db_pool.disconnect()
    print("Default user configured successfully!")

if __name__ == "__main__":
    asyncio.run(main())
