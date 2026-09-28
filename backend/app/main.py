import time
import uuid
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.errors import SentinelException, global_exception_handler, sentinel_exception_handler
from app.core.logging import logger, setup_logging
from app.database.session import AsyncSessionLocal
from app.api.v1.auth import router as auth_router
from app.api.v1.admin import router as admin_router
from app.api.v1.events import router as events_router
from app.api.v1.dlp import router as dlp_router
from app.api.v1.incidents import router as incidents_router
from app.api.v1.threats import router as threats_router

# Initialize logging
setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise AI-Powered Data Security, Threat Investigation & DevSecOps Platform",
    docs_url="/docs" if not settings.is_production() else None,
    redoc_url="/redoc" if not settings.is_production() else None,
    openapi_url="/openapi.json" if not settings.is_production() else None,
)

# Exception Handlers
app.add_exception_handler(SentinelException, sentinel_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Mount API Routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
app.include_router(dlp_router, prefix="/api/v1")
app.include_router(incidents_router, prefix="/api/v1")
app.include_router(threats_router, prefix="/api/v1")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "Content-Disposition"],
)


@app.middleware("http")
async def security_and_tracing_middleware(request: Request, call_next) -> Response:
    """
    Attaches X-Request-ID, security response headers, and measures request latency.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception as exc:
        # Defense-in-depth: intercept unhandled exception, log and sanitize
        response = await global_exception_handler(request, exc)

    process_time = time.perf_counter() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"

    # Security Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    if settings.is_production():
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    # Log request summary
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} ({process_time:.4f}s)",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
        },
    )

    return response


@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """
    Liveness probe: returns basic platform status.
    """
    return {
        "status": "HEALTHY",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/ready", tags=["System"])
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness probe: validates connectivity to backing services (Database).
    """
    checks = {
        "database": "UNKNOWN",
    }

    # Verify DB connectivity
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "READY"
    except Exception as e:
        logger.warning(f"Database readiness check failed: {str(e)}")
        checks["database"] = "NOT_READY"

    is_ready = checks["database"] == "READY"
    return {
        "ready": is_ready,
        "components": checks,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
