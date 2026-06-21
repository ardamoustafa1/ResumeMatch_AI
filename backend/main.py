import os
import sys
import time
import uuid
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


from backend.api.v1 import websocket
from backend.api.v1.routes import analysis, auth, extract, health, telegram, metrics, admin, oauth, saml, workspaces
from backend.core.config import settings
from backend.core.rate_limit import limiter
from backend.db.connection import db_pool
from backend.tasks.progress_events import async_redis_client
from backend.core.prometheus_metrics import (
    http_request_duration_seconds,
    http_requests_total,
)

from backend.core.context import request_id_var, user_id_var



logger.remove()


def log_filter(record):
    record["extra"]["request_id"] = request_id_var.get()
    record["extra"]["user_id"] = user_id_var.get()
    return True


logger.add(
    sys.stderr,
    format="{time} {level} [Req={extra[request_id]} User={extra[user_id]}] {message}",
    level="INFO",
    filter=log_filter,
)


SENSITIVE_FIELDS = {
    "authorization",
    "cookie",
    "password",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "cv_text",
    "jd_text",
    "email",
    "phone",
}


def _scrub_value(value):
    if isinstance(value, dict):
        return {
            key: "[Filtered]" if key.lower() in SENSITIVE_FIELDS else _scrub_value(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_scrub_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_scrub_value(item) for item in value)
    return value


def strip_sensitive_data(event, hint):
    del hint
    scrubbed = _scrub_value(event)
    if isinstance(scrubbed, dict):
        event.clear()
        event.update(scrubbed)
    return event


SENTRY_DSN = os.getenv("SENTRY_DSN", "")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        before_send=strip_sensitive_data,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate()
    logger.info("Initializing NetworkForge application...")
    await db_pool.connect()
    res = async_redis_client.ping()
    if hasattr(res, "__await__"):
        await res
    logger.info("NetworkForge API is ready to receive traffic.")
    yield
    logger.info("Shutting down NetworkForge application...")
    await db_pool.disconnect()
    # async_redis_client is global, do not close it here otherwise tests fail


app = FastAPI(
    title="NetworkForge API",
    description="AI-powered LinkedIn recruiter outreach engine",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.middleware("http")
async def api_version_middleware(request: Request, call_next):
    # Enforce API Versioning via headers
    # Clients should ideally send X-API-Version: 1
    response = await call_next(request)
    response.headers["X-API-Version"] = "1"
    response.headers["X-API-Deprecated"] = "false"
    return response


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
    if settings.is_production:
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none';"
        )
    else:
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; connect-src 'self' wss: https:;"
        )
    if request.url.path.startswith(("/api/v1/auth", "/api/v1/analysis")):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.middleware("http")
async def record_http_metrics(request: Request, call_next):
    started_at = time.perf_counter()
    status_code = 500
    route_template = request.url.path
    try:
        response = await call_next(request)
        status_code = response.status_code
        route = request.scope.get("route")
        route_template = getattr(route, "path", route_template)
        return response
    finally:
        elapsed = time.perf_counter() - started_at
        http_requests_total.labels(
            method=request.method,
            endpoint=route_template,
            status=str(status_code),
        ).inc()
        http_request_duration_seconds.labels(
            method=request.method,
            endpoint=route_template,
        ).observe(elapsed)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        uses_bearer = request.headers.get("authorization", "").startswith("Bearer ")
        uses_auth_cookie = bool(
            request.cookies.get("access_token") or request.cookies.get("refresh_token")
        )
        invalid_cookie_origin = (
            settings.is_production
            and uses_auth_cookie
            and not uses_bearer
            and (not origin or origin not in settings.allowed_origins)
        )
        if (
            origin and origin not in settings.allowed_origins and not uses_bearer
        ) or invalid_cookie_origin:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Origin is not allowed",
                    "code": "ORIGIN_FORBIDDEN",
                    "request_id": request_id,
                },
            )
    request_id_var.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(
        "Unhandled exception on {} (request_id={})",
        request.url.path,
        request_id,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "code": "INTERNAL_ERROR",
            "request_id": request_id,
        },
    )


app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(extract.router, prefix="/api/v1/extract-text", tags=["Extraction"])
app.include_router(telegram.router, prefix="/api/v1/telegram", tags=["Telegram"])
app.include_router(websocket.router, prefix="/api/v1/ws", tags=["WebSockets"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(oauth.router, prefix="/api/v1/oauth", tags=["OAuth SSO"])
app.include_router(saml.router, prefix="/api/v1/saml", tags=["Enterprise SAML"])
app.include_router(workspaces.router, prefix="/api/v1/workspaces", tags=["Workspaces"])
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])


@app.get("/")
def read_root():
    return {
        "name": "NetworkForge API",
        "version": app.version,
        "docs": "/docs",
    }
