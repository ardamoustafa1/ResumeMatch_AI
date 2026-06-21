from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from asyncpg import Connection
from pydantic import ValidationError

from backend.db.connection import get_db
from backend.core.security import ALGORITHM, SECRET_KEY, hash_token
from datetime import datetime, timezone
from fastapi import BackgroundTasks
import enum
from fastapi.security import SecurityScopes
from backend.core.context import user_id_var


class Scope(str, enum.Enum):
    READ_ANALYSIS = "read:analysis"
    WRITE_ANALYSIS = "write:analysis"
    EXTRACT = "extract"
    EXTENSION = "extension"


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


async def get_current_user(
    security_scopes: SecurityScopes,
    request: Request,
    background_tasks: BackgroundTasks,
    conn: Connection = Depends(get_db),
    bearer_token: str | None = Depends(oauth2_scheme),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = bearer_token or request.cookies.get("access_token")
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None or payload.get("type") != "access":
            raise credentials_exception
        user = await conn.fetchrow(
            """
            SELECT id, email, is_active, is_superuser, email_verified, created_at, mfa_enabled
            FROM users
            WHERE email = $1
            """,
            email,
        )
        if not user:
            raise credentials_exception
    except (JWTError, ValidationError):
        hashed = hash_token(token)
        api_key_record = await conn.fetchrow(
            """
            SELECT k.id as key_id, k.user_id, k.expires_at, k.revoked_at, k.scopes,
                   u.id, u.email, u.is_active, u.is_superuser, u.email_verified, u.created_at, u.mfa_enabled
            FROM api_keys k
            JOIN users u ON u.id = k.user_id
            WHERE k.token_hash = $1
            """,
            hashed,
        )
        if not api_key_record:
            raise credentials_exception
        now = datetime.now(timezone.utc)
        if api_key_record["revoked_at"] is not None or (
            api_key_record["expires_at"] and api_key_record["expires_at"] <= now
        ):
            raise credentials_exception
        user = dict(api_key_record)
        user["id"] = api_key_record[
            "user_id"
        ]  # Fix id mapping because user id and key id overlap
        user["auth_type"] = "api_key"

        if security_scopes.scopes:
            has_permission = any(
                scope in user.get("scopes", []) for scope in security_scopes.scopes
            )
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="API key does not have sufficient permissions for this action",
                )
        else:
            # Deny API keys by default on endpoints that don't declare required scopes
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="API key does not have sufficient permissions for this action",
            )

        # Schedule async update of usage metadata
        user_agent = request.headers.get("user-agent", "unknown")

        async def update_usage(key_id: str, ua: str):
            if db_pool.pool is None:
                return
            async with db_pool.pool.acquire() as update_conn:
                await update_conn.execute(
                    "UPDATE api_keys SET last_used_at = $1, device_info = $2 WHERE id = $3",
                    datetime.now(timezone.utc),
                    ua,
                    key_id,
                )

        # db_pool is needed here. Import it.
        from backend.db.connection import db_pool

        background_tasks.add_task(
            update_usage, str(api_key_record["key_id"]), user_agent
        )

    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    user_id_var.set(str(user["id"]))
    return dict(user)
