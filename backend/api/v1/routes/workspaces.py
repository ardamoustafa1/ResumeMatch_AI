from fastapi import APIRouter, Depends, HTTPException, Security, status
from pydantic import BaseModel
from asyncpg import Connection

from backend.api.deps import get_current_user, Scope
from backend.db.connection import get_db

router = APIRouter()

class WorkspaceCreate(BaseModel):
    name: str

class WorkspaceMemberAdd(BaseModel):
    user_email: str
    role: str = "member"

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    current_user: dict = Security(get_current_user, scopes=[Scope.WRITE_ANALYSIS]),
    conn: Connection = Depends(get_db)
):
    ws_id = await conn.fetchval(
        "INSERT INTO workspaces (name, created_by) VALUES ($1, $2) RETURNING id",
        payload.name,
        current_user["id"]
    )
    await conn.execute(
        "INSERT INTO workspace_members (workspace_id, user_id, role) VALUES ($1, $2, 'owner')",
        ws_id, current_user["id"]
    )
    return {"id": ws_id, "name": payload.name}

@router.get("")
async def list_workspaces(
    current_user: dict = Security(get_current_user, scopes=[Scope.READ_ANALYSIS]),
    conn: Connection = Depends(get_db)
):
    rows = await conn.fetch(
        """
        SELECT w.id, w.name, wm.role 
        FROM workspaces w
        JOIN workspace_members wm ON w.id = wm.workspace_id
        WHERE wm.user_id = $1
        """,
        current_user["id"]
    )
    return {"items": [dict(r) for r in rows]}

@router.post("/{workspace_id}/members")
async def add_workspace_member(
    workspace_id: str,
    payload: WorkspaceMemberAdd,
    current_user: dict = Security(get_current_user, scopes=[Scope.WRITE_ANALYSIS]),
    conn: Connection = Depends(get_db)
):
    role = await conn.fetchval(
        "SELECT role FROM workspace_members WHERE workspace_id = $1::uuid AND user_id = $2",
        workspace_id, current_user["id"]
    )
    if role != "owner":
        raise HTTPException(status_code=403, detail="Only owners can add members")

    target_user_id = await conn.fetchval("SELECT id FROM users WHERE email = $1", payload.user_email)
    if not target_user_id:
        raise HTTPException(status_code=404, detail="User not found")

    await conn.execute(
        "INSERT INTO workspace_members (workspace_id, user_id, role) VALUES ($1::uuid, $2, $3) ON CONFLICT DO NOTHING",
        workspace_id, target_user_id, payload.role
    )
    return {"status": "success"}
