"""Main FastAPI application."""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1 import api_router
from app.core.cache import close_redis, get_redis
from app.core.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ANN201, ARG001
    """Application lifespan events."""
    # Startup
    logger.info("application_startup", environment=settings.environment)

    # Initialize Redis connection
    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("redis_connected")
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))

    yield

    # Shutdown
    logger.info("application_shutdown")
    await close_redis()


# Create FastAPI application
app = FastAPI(
    title="Visual Noise Museum API",
    description="Backend API for Visual Noise Museum - A bleeding-edge full-stack application",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):  # noqa: ANN001, ANN201
    """Log all HTTP requests with timing."""
    start_time = time.time()

    # Generate correlation ID
    correlation_id = request.headers.get("X-Correlation-ID", str(time.time()))

    # Bind correlation ID to logger
    log = logger.bind(correlation_id=correlation_id)

    # Log request
    log.info(
        "request_started",
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )

    try:
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        log.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration * 1000, 2),
        )

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response

    except Exception as e:
        duration = time.time() - start_time
        log.error(
            "request_failed",
            method=request.method,
            path=request.url.path,
            error=str(e),
            duration_ms=round(duration * 1000, 2),
        )
        raise


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions."""
    logger.error(
        "unhandled_exception",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True,
    )

    if settings.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc), "type": type(exc).__name__},
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


# Health check endpoints
@app.get("/health")
async def health_check() -> dict[str, str]:
    """Basic health check."""
    return {"status": "healthy"}


@app.get("/readiness")
async def readiness_check() -> dict[str, Any]:
    """Readiness check with dependencies."""
    checks = {"database": "unknown", "redis": "unknown"}

    # Check Redis
    try:
        redis = await get_redis()
        await redis.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {e}"

    # Overall status
    is_ready = all(v == "healthy" for v in checks.values() if v != "unknown")

    return {
        "status": "ready" if is_ready else "not_ready",
        "checks": checks,
    }


# Include API routers
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "name": "Visual Noise Museum API",
        "version": "0.1.0",
        "docs": "/docs" if settings.debug else "disabled",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
