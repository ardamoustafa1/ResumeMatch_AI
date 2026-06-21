import logging
from typing import Dict, Any

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from pydantic import BaseModel

from backend.api.deps import get_current_user
from backend.db.connection import get_db
from backend.db.admin_queries import get_all_users, update_user_status, get_system_stats

logger = logging.getLogger(__name__)
router = APIRouter()

def require_superuser(current_user: dict = Security(get_current_user)):
    if not current_user.get("is_superuser"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires superuser privileges",
        )
    return current_user

class UserStatusUpdate(BaseModel):
    is_active: bool

@router.get("/users")
async def list_users(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: dict = Depends(require_superuser),
    conn: Connection = Depends(get_db),
):
    users = await get_all_users(conn, limit=limit, offset=offset)
    return {
        "items": users,
        "limit": limit,
        "offset": offset,
    }

@router.patch("/users/{user_id}/status")
async def update_status(
    user_id: str,
    payload: UserStatusUpdate,
    current_user: dict = Depends(require_superuser),
    conn: Connection = Depends(get_db),
):
    if str(current_user["id"]) == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own status",
        )
        
    success = await update_user_status(conn, user_id, payload.is_active)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return {"status": "success", "is_active": payload.is_active}

@router.get("/system")
async def system_health(
    _: dict = Depends(require_superuser),
    conn: Connection = Depends(get_db),
):
    try:
        stats = await get_system_stats(conn)
        return {"status": "healthy", "stats": stats}
    except Exception as e:
        logger.exception("Failed to get system stats")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve system statistics",
        )
