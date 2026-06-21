from typing import Any, Dict, List
from asyncpg import Connection

async def get_all_users(
    conn: Connection, limit: int = 50, offset: int = 0
) -> List[Dict[str, Any]]:
    query = """
        SELECT id, email, is_active, is_superuser, email_verified, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT $1 OFFSET $2;
    """
    rows = await conn.fetch(query, limit, offset)
    
    results = []
    for row in rows:
        record = dict(row)
        record["id"] = str(record["id"])
        results.append(record)
    return results

async def update_user_status(
    conn: Connection, user_id: str, is_active: bool
) -> bool:
    query = """
        UPDATE users
        SET is_active = $1
        WHERE id = $2::uuid;
    """
    status_str = await conn.execute(query, is_active, user_id)
    return status_str.endswith("1")

async def get_system_stats(conn: Connection) -> Dict[str, Any]:
    # Total users
    users_count = await conn.fetchval("SELECT COUNT(*) FROM users;")
    # Total analyses
    analyses_count = await conn.fetchval("SELECT COUNT(*) FROM analyses;")
    # Analyses in last 24h
    recent_analyses = await conn.fetchval(
        "SELECT COUNT(*) FROM analyses WHERE created_at > NOW() - INTERVAL '1 day';"
    )
    
    return {
        "total_users": users_count,
        "total_analyses": analyses_count,
        "analyses_24h": recent_analyses,
    }
