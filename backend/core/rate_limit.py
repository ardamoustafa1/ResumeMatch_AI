from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url if settings.redis_url else "memory://",
)
