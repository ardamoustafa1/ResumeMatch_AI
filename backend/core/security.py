import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from pwdlib import PasswordHash

from backend.core.config import settings

SECRET_KEY = settings.secret_key or secrets.token_urlsafe(48)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_minutes

password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password or hashed_password == "!":
        return False
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def create_access_token(
    subject: str | Any, expires_delta: timedelta | None = None
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {
        "exp": expire,
        "iat": now,
        "sub": str(subject),
        "type": "access",
        "jti": secrets.token_urlsafe(16),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token() -> tuple[str, str, datetime]:
    token = secrets.token_urlsafe(48)
    digest = hash_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_days
    )
    return token, digest, expires_at


def create_one_time_token(
    lifetime: timedelta,
) -> tuple[str, str, datetime]:
    token = secrets.token_urlsafe(48)
    return token, hash_token(token), datetime.now(timezone.utc) + lifetime


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
