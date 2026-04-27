import json
from typing import List, Optional, Dict, Any
from asyncpg import Connection


async def create_analysis(
    conn: Connection,
    user_id: str,
    cv_text: str,
    jd_text: str,
    company: Optional[str] = None,
    recruiter_name: Optional[str] = None
) -> str:
    """
    Insert a new analysis record into the database.
    
    Args:
        conn (Connection): The asyncpg connection
        user_id (str): The ID of the user requesting the analysis
        cv_text (str): Candidate's CV text
        jd_text (str): Job description text
        company (Optional[str]): Hiring company name
        recruiter_name (Optional[str]): Recruiter's name
        
    Returns:
        str: The UUID of the newly created analysis as a string
    """
    query = """
        INSERT INTO analyses (user_id, cv_text, jd_text, company, recruiter_name, status)
        VALUES ($1::uuid, $2, $3, $4, $5, 'pending')
        RETURNING id;
    """
    analysis_id = await conn.fetchval(
        query, 
        user_id, 
        cv_text, 
        jd_text, 
        company, 
        recruiter_name
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
    result: Optional[Dict[str, Any]] = None
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
        SET status = $1, result = $2::jsonb, updated_at = CURRENT_TIMESTAMP
        WHERE id = $3::uuid;
    """
    result_json = json.dumps(result) if result else None
    
    status_str = await conn.execute(query, status, result_json, analysis_id)
    return status_str.endswith("1")


async def get_user_analyses(
    conn: Connection, 
    user_id: str, 
    limit: int = 50, 
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Retrieve a list of analyses for a specific user.
    
    Args:
        conn (Connection): The asyncpg connection
        user_id (str): The ID of the user
        limit (int): Pagination limit
        offset (int): Pagination offset
        
    Returns:
        List[Dict[str, Any]]: A list of analysis records
    """
    query = """
        SELECT id, user_id, company, recruiter_name, status, created_at
        FROM analyses
        WHERE user_id = $1::uuid
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3;
    """
    rows = await conn.fetch(query, user_id, limit, offset)
    
    results = []
    for row in rows:
        record = dict(row)
        record["id"] = str(record["id"])
        record["user_id"] = str(record["user_id"])
        results.append(record)
        
    return results


async def get_telegram_config(conn: Connection, user_id: str) -> Optional[Dict[str, Any]]:
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
