import json
from typing import Any, Dict, List, Optional
from asyncpg import Connection


async def create_analysis(
    conn: Connection,
    user_id: str,
    cv_text: str,
    jd_text: str,
    company: Optional[str] = None,
    recruiter_name: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> str:
    """
    Insert a new analysis record into the database.
    """
    query = """
        INSERT INTO analyses (user_id, cv_text, jd_text, company, recruiter_name, workspace_id, status)
        VALUES ($1::uuid, $2, $3, $4, $5, $6::uuid, 'pending')
        RETURNING id;
    """
    analysis_id = await conn.fetchval(
        query, user_id, cv_text, jd_text, company, recruiter_name, workspace_id
    )
    return str(analysis_id)


async def get_analysis(conn: Connection, analysis_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve an analysis by its ID.

    Args:
        conn (Connection): The asyncpg connection
        analysis_id (str): The ID of the analysis

    Returns:
        Optional[Dict[str, Any]]: The analysis record as a dictionary, or None if not found
    """
    query = """
        SELECT id, user_id, cv_text, jd_text, company, recruiter_name, status, result, created_at
        FROM analyses
        WHERE id = $1::uuid;
    """
    row = await conn.fetchrow(query, analysis_id)
    if row:
        record = dict(row)

        # Parse JSONB string into python dict if it exists
        if record.get("result") and isinstance(record["result"], str):
            record["result"] = json.loads(record["result"])

        # Convert UUID fields to strings for dict serialization
        record["id"] = str(record["id"])
        record["user_id"] = str(record["user_id"])
        return record
    return None


async def update_analysis_result(
    conn: Connection,
    analysis_id: str,
    status: str,
    result: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Update the status and result of an existing analysis.

    Args:
        conn (Connection): The asyncpg connection
        analysis_id (str): The ID of the analysis
        status (str): The new status (e.g., 'completed', 'failed')
        result (Optional[Dict[str, Any]]): The JSON result from the AI processing

    Returns:
        bool: True if the update was successful, False otherwise
    """
    query = """
        UPDATE analyses
        SET status = $1, result = $2::jsonb
        WHERE id = $3::uuid;
    """
    result_json = json.dumps(result) if result else None

    status_str = await conn.execute(query, status, result_json, analysis_id)
    return status_str.endswith("1")


async def get_user_analyses(
    conn: Connection, user_id: str, workspace_id: Optional[str] = None, limit: int = 50, offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Retrieve a list of analyses for a specific user or workspace.
    """
    if workspace_id:
        # Check if user has access to workspace
        has_access = await conn.fetchval(
            "SELECT 1 FROM workspace_members WHERE workspace_id = $1::uuid AND user_id = $2::uuid",
            workspace_id, user_id
        )
        if not has_access:
            return []
            
        query = """
            SELECT id, user_id, company, recruiter_name, status, created_at, workspace_id
            FROM analyses
            WHERE workspace_id = $1::uuid
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3;
        """
        rows = await conn.fetch(query, workspace_id, limit, offset)
    else:
        query = """
            SELECT id, user_id, company, recruiter_name, status, created_at, workspace_id
            FROM analyses
            WHERE user_id = $1::uuid AND workspace_id IS NULL
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3;
        """
        rows = await conn.fetch(query, user_id, limit, offset)

    results = []
    for row in rows:
        record = dict(row)
        record["id"] = str(record["id"])
        record["user_id"] = str(record["user_id"])
        if record.get("workspace_id"):
            record["workspace_id"] = str(record["workspace_id"])
        results.append(record)

    return results


async def get_telegram_config(
    conn: Connection, user_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve Telegram configuration for a user.

    Args:
        conn (Connection): The asyncpg connection
        user_id (str): The ID of the user

    Returns:
        Optional[Dict[str, Any]]: The Telegram config record if active, else None
    """
    query = """
        SELECT chat_id, is_active 
        FROM telegram_configs 
        WHERE user_id = $1::uuid AND is_active = true;
    """
    row = await conn.fetchrow(query, user_id)
    if row:
        return dict(row)
    return None


async def log_audit_event(
    conn: Connection,
    event_type: str,
    *,
    user_id: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Persist a minimal, non-sensitive security audit event."""
    await conn.execute(
        """
        INSERT INTO audit_events (
            user_id, event_type, ip_address, user_agent, metadata
        )
        VALUES ($1::uuid, $2, $3::inet, $4, $5::jsonb)
        """,
        user_id,
        event_type,
        ip_address,
        (user_agent or "")[:255] or None,
        json.dumps(metadata or {}),
    )
