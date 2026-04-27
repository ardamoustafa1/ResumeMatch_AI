import os
import uuid
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.db.connection import db_pool
from backend.tasks.progress_events import async_redis_client

from backend.api.v1.routes import analysis, telegram, health, extract
from backend.api.v1 import websocket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application Startup
    logger.info("Initializing NetworkForge application...")
    
    logger.info("Connecting to PostgreSQL pool...")
    await db_pool.connect()
    
    logger.info("Verifying Redis connection...")
    await async_redis_client.ping()
    
    logger.info("NetworkForge API is ready to receive traffic.")
    yield
    # Application Shutdown
    logger.info("Shutting down NetworkForge application...")
    await db_pool.disconnect()
    await async_redis_client.close()

app = FastAPI(
    title="NetworkForge API",
    description="AI-powered LinkedIn recruiter outreach engine",
    version="1.0.0",
    lifespan=lifespan,
)

# Configurable CORS Middleware
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Request ID Middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Standardized Error Handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc), "code": "INTERNAL_ERROR"},
    )

# Include HTTP Routers
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
app.include_router(extract.router, prefix="/api/v1/extract-text", tags=["Extraction"])
app.include_router(telegram.router, prefix="/api/v1/telegram", tags=["Telegram"])

# Include WebSocket Router
app.include_router(websocket.router, prefix="/ws", tags=["WebSockets"])

@app.get("/")
def read_root():
    return {"message": "Welcome to NetworkForge API"}
