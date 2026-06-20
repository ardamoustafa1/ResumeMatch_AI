import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.api.deps import get_current_user
from backend.core.config import settings
from backend.core.rate_limit import limiter
from backend.core.security import (
    create_access_token,
    create_one_time_token,
    create_refresh_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from backend.db.connection import get_db
from backend.models.schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserCreate,
    UserResponse,
    VerifyEmailRequest,
)
from backend.services.email_service import (
    send_password_reset_email,
    send_verification_email,
)

logger = logging.getLogger(__name__)
router = APIRouter()

ACCESS_COOKIE_MAX_AGE = settings.access_token_minutes * 60
REFRESH_COOKIE_MAX_AGE = settings.refresh_token_days * 24 * 60 * 60


def _set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    response.set_cookie(
        "access_token",
        access_token,
        max_age=ACCESS_COOKIE_MAX_AGE,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        secure=settings.secure_cookies,
        samesite="lax",
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("3/minute")
async def register(
    request: Request,
    user_in: UserCreate,
    conn: Connection = Depends(get_db),
) -> Any:
    email = str(user_in.email).lower()
    user = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    query = """
        INSERT INTO users (email, hashed_password)
        VALUES ($1, $2)
        RETURNING id, email, is_active, is_superuser, email_verified, created_at
    """
    new_user = await conn.fetchrow(query, email, get_password_hash(user_in.password))
    verification_token, token_hash, expires_at = create_one_time_token(
        timedelta(hours=24)
    )
    await conn.execute(
        """
        INSERT INTO email_verification_tokens (user_id, token_hash, expires_at)
        VALUES ($1, $2, $3)
        """,
        new_user["id"],
        token_hash,
        expires_at,
    )
    try:
        await send_verification_email(email, verification_token)
    except Exception:
        logger.exception("Verification email delivery failed")
    return dict(new_user)


@router.post("/login")
@limiter.limit("5/minute")
async def login(
    request: Request,
    response: Response,
    conn: Connection = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    email = form_data.username.lower()
    user = await conn.fetchrow(
        """
        SELECT id, email, hashed_password, is_active, email_verified
        FROM users
        WHERE email = $1
        """,
        email,
    )
    if (
        not user
        or not user["is_active"]
        or not verify_password(form_data.password, user["hashed_password"])
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if settings.email_verification_required and not user["email_verified"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verify your email before signing in.",
        )

    access_token = create_access_token(subject=user["email"])
    refresh_token, refresh_digest, expires_at = create_refresh_token()
    await conn.execute(
        """
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
        VALUES ($1, $2, $3)
        """,
        user["id"],
        refresh_digest,
        expires_at,
    )
    _set_auth_cookies(response, access_token, refresh_token)
    return {"status": "success"}


@router.post("/refresh")
@limiter.limit("10/minute")
async def refresh_access_token(
    request: Request,
    response: Response,
    conn: Connection = Depends(get_db),
) -> Any:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
        )

    token_hash = hash_token(refresh_token)
    record = await conn.fetchrow(
        """
        SELECT rt.id, rt.user_id, rt.expires_at, rt.revoked_at, u.email, u.is_active
        FROM refresh_tokens rt
        JOIN users u ON u.id = rt.user_id
        WHERE rt.token_hash = $1
        FOR UPDATE
        """,
        token_hash,
    )
    now = datetime.now(timezone.utc)
    if (
        not record
        or record["revoked_at"] is not None
        or record["expires_at"] <= now
        or not record["is_active"]
    ):
        _clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    new_refresh_token, new_digest, expires_at = create_refresh_token()
    await conn.execute(
        "UPDATE refresh_tokens SET revoked_at = $1 WHERE id = $2",
        now,
        record["id"],
    )
    await conn.execute(
        """
        INSERT INTO refresh_tokens (user_id, token_hash, expires_at)
        VALUES ($1, $2, $3)
        """,
        record["user_id"],
        new_digest,
        expires_at,
    )
    access_token = create_access_token(subject=record["email"])
    _set_auth_cookies(response, access_token, new_refresh_token)
    return {"status": "success"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: Request,
    response: Response,
    conn: Connection = Depends(get_db),
) -> Response:
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await conn.execute(
            """
            UPDATE refresh_tokens
            SET revoked_at = CURRENT_TIMESTAMP
            WHERE token_hash = $1 AND revoked_at IS NULL
            """,
            hash_token(refresh_token),
        )
    _clear_auth_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: dict = Depends(get_current_user),
) -> Any:
    return current_user


@router.post("/verify-email")
@limiter.limit("10/hour")
async def verify_email(
    request: Request,
    payload: VerifyEmailRequest,
    conn: Connection = Depends(get_db),
):
    record = await conn.fetchrow(
        """
        SELECT id, user_id, expires_at, used_at
        FROM email_verification_tokens
        WHERE token_hash = $1
        FOR UPDATE
        """,
        hash_token(payload.token),
    )
    now = datetime.now(timezone.utc)
    if not record or record["used_at"] or record["expires_at"] <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification link is invalid or expired.",
        )
    await conn.execute(
        "UPDATE email_verification_tokens SET used_at = $1 WHERE id = $2",
        now,
        record["id"],
    )
    await conn.execute(
        "UPDATE users SET email_verified = TRUE, updated_at = $1 WHERE id = $2",
        now,
        record["user_id"],
    )
    return {"status": "verified"}


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("3/hour")
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    conn: Connection = Depends(get_db),
):
    user = await conn.fetchrow(
        "SELECT id, email FROM users WHERE email = $1 AND is_active = TRUE",
        str(payload.email).lower(),
    )
    if user:
        token, token_hash, expires_at = create_one_time_token(timedelta(hours=1))
        await conn.execute(
            """
            INSERT INTO password_reset_tokens (user_id, token_hash, expires_at)
            VALUES ($1, $2, $3)
            """,
            user["id"],
            token_hash,
            expires_at,
        )
        try:
            await send_password_reset_email(user["email"], token)
        except Exception:
            logger.exception("Password reset email delivery failed")
    return {"message": "If the account exists, password reset instructions were sent."}


@router.post("/reset-password")
@limiter.limit("5/hour")
async def reset_password(
    request: Request,
    payload: ResetPasswordRequest,
    conn: Connection = Depends(get_db),
):
    record = await conn.fetchrow(
        """
        SELECT id, user_id, expires_at, used_at
        FROM password_reset_tokens
        WHERE token_hash = $1
        FOR UPDATE
        """,
        hash_token(payload.token),
    )
    now = datetime.now(timezone.utc)
    if not record or record["used_at"] or record["expires_at"] <= now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset link is invalid or expired.",
        )
    await conn.execute(
        "UPDATE password_reset_tokens SET used_at = $1 WHERE id = $2",
        now,
        record["id"],
    )
    await conn.execute(
        "UPDATE users SET hashed_password = $1, updated_at = $2 WHERE id = $3",
        get_password_hash(payload.password),
        now,
        record["user_id"],
    )
    await conn.execute(
        """
        UPDATE refresh_tokens
        SET revoked_at = $1
        WHERE user_id = $2 AND revoked_at IS NULL
        """,
        now,
        record["user_id"],
    )
    return {"status": "password_updated"}


@router.post("/api-key")
@limiter.limit("5/minute")
async def generate_api_key(
    request: Request,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
) -> Any:
    """Generate a scoped API key (1 year) for the Chrome Extension."""
    token = secrets.token_urlsafe(32)
    prefix = token[:8]
    hashed = hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=365)
    
    await conn.execute(
        """
        INSERT INTO api_keys (user_id, prefix, token_hash, scopes, expires_at)
        VALUES ($1, $2, $3, $4, $5)
        """,
        current_user["id"],
        prefix,
        hashed,
        ["extension"],
        expires_at
    )
    return {"access_token": token, "token_type": "bearer", "prefix": prefix, "expires_at": expires_at}


@router.get("/api-keys")
async def list_api_keys(
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
) -> Any:
    """List active API keys."""
    keys = await conn.fetch(
        """
        SELECT id, prefix, scopes, expires_at, created_at
        FROM api_keys
        WHERE user_id = $1 AND revoked_at IS NULL
        """,
        current_user["id"],
    )
    return [dict(k) for k in keys]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
) -> Any:
    """Revoke an API key."""
    await conn.execute(
        """
        UPDATE api_keys
        SET revoked_at = CURRENT_TIMESTAMP
        WHERE id = $1::uuid AND user_id = $2
        """,
        key_id,
        current_user["id"],
    )
    return {"status": "revoked"}
