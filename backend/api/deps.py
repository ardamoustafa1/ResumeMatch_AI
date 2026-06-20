from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from asyncpg import Connection
from pydantic import ValidationError

from backend.db.connection import get_db
from backend.core.security import ALGORITHM, SECRET_KEY, hash_token
from datetime import datetime, timezone

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


async def get_current_user(
    request: Request,
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
            SELECT id, email, is_active, is_superuser, email_verified, created_at
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
            SELECT k.user_id, k.expires_at, k.revoked_at, k.scopes,
                   u.id, u.email, u.is_active, u.is_superuser, u.email_verified, u.created_at
            FROM api_keys k
            JOIN users u ON u.id = k.user_id
            WHERE k.token_hash = $1
            """,
            hashed
        )
        if not api_key_record:
            raise credentials_exception
        now = datetime.now(timezone.utc)
        if api_key_record["revoked_at"] is not None or (api_key_record["expires_at"] and api_key_record["expires_at"] <= now):
            raise credentials_exception
        user = dict(api_key_record)
        if "extension" in str(user.get("scopes", "")):
            if request.url.path == "/api/v1/analysis/export":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="API key does not have sufficient permissions for this action",
                )
            allowed_paths = ["/api/v1/analysis", "/api/v1/extract-text"]
            is_allowed = any(request.url.path.startswith(p) for p in allowed_paths)
            if not is_allowed or request.method == "DELETE":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="API key does not have sufficient permissions for this action",
                )
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )
    return dict(user)
