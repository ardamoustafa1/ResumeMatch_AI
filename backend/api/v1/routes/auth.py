from pydantic import BaseModel
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict

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
    create_mfa_token,
    verify_mfa_token,
    get_password_hash,
    hash_token,
    verify_password,
)
from backend.db.connection import get_db
from backend.db.queries import log_audit_event
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


class RequestContext(TypedDict):
    ip_address: str | None
    user_agent: str | None


def _request_context(request: Request) -> RequestContext:
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


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

    async with conn.transaction():
        query = """
            INSERT INTO users (email, hashed_password)
            VALUES ($1, $2)
            RETURNING id, email, is_active, is_superuser, email_verified, created_at
        """
        new_user = await conn.fetchrow(
            query, email, get_password_hash(user_in.password)
        )
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
    await log_audit_event(
        conn,
        "account.registered",
        user_id=str(new_user["id"]),
        **_request_context(request),
    )
    return dict(new_user)


@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("3/hour")
async def resend_verification(
    request: Request,
    payload: ForgotPasswordRequest,
    conn: Connection = Depends(get_db),
):
    user = await conn.fetchrow(
        "SELECT id, email, email_verified FROM users WHERE email = $1",
        str(payload.email).lower(),
    )
    if user and not user["email_verified"]:
        verification_token, token_hash, expires_at = create_one_time_token(
            timedelta(hours=24)
        )
        await conn.execute(
            """
            INSERT INTO email_verification_tokens (user_id, token_hash, expires_at)
            VALUES ($1, $2, $3)
            """,
            user["id"],
            token_hash,
            expires_at,
        )
        try:
            await send_verification_email(user["email"], verification_token)
        except Exception:
            logger.exception("Verification email delivery failed")
    return {
        "message": "If the account exists and is unverified, a new verification link was sent."
    }


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
        SELECT id, email, hashed_password, is_active, email_verified, mfa_enabled, totp_secret
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

    if user.get("mfa_enabled"):
        mfa_token = create_mfa_token(subject=user["email"])
        return {"status": "mfa_required", "mfa_token": mfa_token}

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
    await log_audit_event(
        conn,
        "session.login",
        user_id=str(user["id"]),
        **_request_context(request),
    )
    _set_auth_cookies(response, access_token, refresh_token)
    return {"status": "success"}


class MFAVerifyRequest(BaseModel):
    mfa_token: str
    code: str


@router.post("/mfa/verify")
@limiter.limit("5/minute")
async def verify_mfa_login(
    request: Request,
    response: Response,
    payload: MFAVerifyRequest,
    conn: Connection = Depends(get_db),
):
    import pyotp

    email = verify_mfa_token(payload.mfa_token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA token",
        )

    user = await conn.fetchrow(
        "SELECT id, email, mfa_enabled, totp_secret FROM users WHERE email = $1", email
    )
    if not user or not user["mfa_enabled"] or not user["totp_secret"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled for this user",
        )

    totp = pyotp.TOTP(user["totp_secret"])
    if not totp.verify(payload.code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code"
        )

    access_token = create_access_token(subject=user["email"])
    refresh_token, refresh_digest, expires_at = create_refresh_token()
    await conn.execute(
        "INSERT INTO refresh_tokens (user_id, token_hash, expires_at) VALUES ($1, $2, $3)",
        user["id"],
        refresh_digest,
        expires_at,
    )
    await log_audit_event(
        conn, "session.login_mfa", user_id=str(user["id"]), **_request_context(request)
    )
    _set_auth_cookies(response, access_token, refresh_token)
    return {"status": "success"}


@router.post("/mfa/setup")
async def mfa_setup(
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    import pyotp

    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        name=current_user["email"], issuer_name="NetworkForge"
    )

    await conn.execute(
        "UPDATE users SET totp_secret = $1 WHERE id = $2", secret, current_user["id"]
    )
    return {"secret": secret, "uri": provisioning_uri}


class MFAEnableRequest(BaseModel):
    code: str


@router.post("/mfa/enable")
async def mfa_enable(
    payload: MFAEnableRequest,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
):
    import pyotp

    user = await conn.fetchrow(
        "SELECT totp_secret FROM users WHERE id = $1", current_user["id"]
    )
    if not user or not user["totp_secret"]:
        raise HTTPException(status_code=400, detail="MFA setup not initiated.")

    totp = pyotp.TOTP(user["totp_secret"])
    if not totp.verify(payload.code):
        raise HTTPException(status_code=401, detail="Invalid MFA code")

    await conn.execute(
        "UPDATE users SET mfa_enabled = TRUE WHERE id = $1", current_user["id"]
    )
    return {"status": "mfa_enabled"}


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
    now = datetime.now(timezone.utc)

    async with conn.transaction():
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
        if not record or record["expires_at"] <= now or not record["is_active"]:
            _clear_auth_cookies(response)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

        if record["revoked_at"] is not None:
            # Token family reuse detection: a revoked token was presented.
            # Assume token theft and revoke ALL refresh tokens for this user.
            await conn.execute(
                "UPDATE refresh_tokens SET revoked_at = $1 WHERE user_id = $2 AND revoked_at IS NULL",
                now,
                record["user_id"],
            )
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
    await log_audit_event(
        conn,
        "session.logout",
        **_request_context(request),
    )
    _clear_auth_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: dict = Depends(get_current_user),
) -> Any:
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_users_me(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
) -> Response:
    """Delete the current user account and all associated data."""
    # The database schema has ON DELETE CASCADE for users -> analyses, api_keys, refresh_tokens, etc.
    await log_audit_event(
        conn,
        "account.deleted",
        user_id=str(current_user["id"]),
        **_request_context(request),
    )
    await conn.execute("DELETE FROM users WHERE id = $1::uuid", current_user["id"])
    _clear_auth_cookies(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/export")
@limiter.limit("2/hour")
async def export_user_data(
    request: Request,
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
) -> Any:
    """Export all user data in JSON format."""
    # Fetch all analyses and their results
    analyses = await conn.fetch(
        "SELECT id, cv_text, jd_text, company, recruiter_name, status, result, created_at FROM analyses WHERE user_id = $1",
        current_user["id"],
    )

    # Fetch all api keys
    api_keys = await conn.fetch(
        "SELECT id, name, prefix, scopes, created_at, last_used_at, device_info FROM api_keys WHERE user_id = $1",
        current_user["id"],
    )

    export_data = {
        "user": {
            "id": str(current_user["id"]),
            "email": current_user["email"],
            "created_at": current_user["created_at"].isoformat()
            if current_user.get("created_at")
            else None,
        },
        "analyses": [dict(a) for a in analyses],
        "api_keys": [dict(k) for k in api_keys],
        "exported_at": datetime.now(timezone.utc).isoformat(),
    }

    # Convert uuids and datetimes to string for JSON serialization
    def convert_serializable(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        import uuid

        if isinstance(obj, uuid.UUID):
            return str(obj)
        return obj

    import json

    json_str = json.dumps(export_data, default=convert_serializable)
    await log_audit_event(
        conn,
        "account.exported",
        user_id=str(current_user["id"]),
        **_request_context(request),
    )
    return Response(
        content=json_str,
        media_type="application/json",
        headers={
            "Content-Disposition": 'attachment; filename="resumematch-export.json"',
            "Cache-Control": "no-store",
        },
    )


@router.post("/verify-email")
@limiter.limit("10/hour")
async def verify_email(
    request: Request,
    payload: VerifyEmailRequest,
    conn: Connection = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    async with conn.transaction():
        record = await conn.fetchrow(
            """
            SELECT id, user_id, expires_at, used_at
            FROM email_verification_tokens
            WHERE token_hash = $1
            FOR UPDATE
            """,
            hash_token(payload.token),
        )
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
    now = datetime.now(timezone.utc)

    async with conn.transaction():
        record = await conn.fetchrow(
            """
            SELECT id, user_id, expires_at, used_at
            FROM password_reset_tokens
            WHERE token_hash = $1
            FOR UPDATE
            """,
            hash_token(payload.token),
        )
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
    # Check max limit
    count = await conn.fetchval(
        "SELECT COUNT(*) FROM api_keys WHERE user_id = $1 AND revoked_at IS NULL",
        current_user["id"],
    )
    if count >= 5:
        raise HTTPException(
            status_code=400, detail="Maximum of 5 active API keys allowed."
        )

    token = secrets.token_urlsafe(32)
    prefix = token[:8]
    hashed = hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=365)
    name = "Extension Key"

    await conn.execute(
        """
        INSERT INTO api_keys (user_id, prefix, token_hash, scopes, expires_at, name)
        VALUES ($1, $2, $3, $4, $5, $6)
        """,
        current_user["id"],
        prefix,
        hashed,
        ["extension", "read:analysis", "write:analysis", "extract"],
        expires_at,
        name,
    )
    await log_audit_event(
        conn,
        "api_key.created",
        user_id=str(current_user["id"]),
        **_request_context(request),
        metadata={
            "prefix": prefix,
            "scopes": ["read:analysis", "write:analysis", "extract"],
        },
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "prefix": prefix,
        "name": name,
        "expires_at": expires_at,
    }


@router.get("/api-keys")
async def list_api_keys(
    current_user: dict = Depends(get_current_user),
    conn: Connection = Depends(get_db),
) -> Any:
    """List active API keys."""
    keys = await conn.fetch(
        """
        SELECT id, name, prefix, scopes, expires_at, created_at, last_used_at, device_info
        FROM api_keys
        WHERE user_id = $1 AND revoked_at IS NULL
        """,
        current_user["id"],
    )
    return [dict(k) for k in keys]


@router.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    request: Request,
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
    await log_audit_event(
        conn,
        "api_key.revoked",
        user_id=str(current_user["id"]),
        **_request_context(request),
        metadata={"key_id": key_id},
    )
    return {"status": "revoked"}
