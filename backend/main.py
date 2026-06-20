import os
import sys
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
from backend.api.v1.routes import analysis, auth, extract, health, telegram
from backend.core.config import settings
from backend.core.rate_limit import limiter
from backend.db.connection import db_pool
from backend.tasks.progress_events import async_redis_client

logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")


def strip_sensitive_data(event, hint):
    if "request" in event:
        request = event["request"]
        # Scrub headers
        if "headers" in request:
            headers = request["headers"]
            if "authorization" in headers:
                headers["authorization"] = "[Filtered]"
            if "cookie" in headers:
                headers["cookie"] = "[Filtered]"
        # Scrub data
        if "data" in request and isinstance(request["data"], dict):
            data = request["data"]
            for field in ["password", "token", "cv_text", "jd_text", "email", "phone"]:
                if field in data:
                    data[field] = "[Filtered]"
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
    logger.info("Initializing ResumeMatch AI application...")
    await db_pool.connect()
    await async_redis_client.ping()
    logger.info("ResumeMatch AI API is ready to receive traffic.")
    yield
    logger.info("Shutting down ResumeMatch AI application...")
    await db_pool.disconnect()
    await async_redis_client.aclose()


app = FastAPI(
    title="ResumeMatch AI API",
    description="AI-powered LinkedIn recruiter outreach engine",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore[arg-type]

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
)


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
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self' wss: https:;"
    )
    return response


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        uses_bearer = request.headers.get("authorization", "").startswith("Bearer ")
        if origin and origin not in settings.allowed_origins and not uses_bearer:
            return JSONResponse(
                status_code=403,
                content={
                    "error": "Origin is not allowed",
                    "code": "ORIGIN_FORBIDDEN",
                    "request_id": request_id,
                },
            )
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


@app.get("/")
def read_root():
    return {
        "name": "ResumeMatch AI API",
        "version": app.version,
        "docs": "/docs",
    }
