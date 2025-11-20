"""
FastAPI application entrypoint for the Visual Noise Museum backend.
This implementation uses async SQLAlchemy with PostgreSQL/pgvector,
Redis-backed rate limiting, and structured logging with correlation IDs.
"""
from __future__ import annotations

import contextvars
from typing import Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.api.v1.router import api_router
from app.core.config import settings

logger = structlog.get_logger()
correlation_id_ctx = contextvars.ContextVar("correlation_id", default=None)


def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ]
    )


def add_correlation_id(request: Request) -> str:
    cid = request.headers.get("x-correlation-id") or str(uuid4())
    correlation_id_ctx.set(cid)
    structlog.contextvars.bind_contextvars(correlation_id=cid, path=request.url.path)
    return cid


def correlation_middleware(app: FastAPI) -> Callable:
    async def middleware(request: Request, call_next: Callable) -> Response:
        add_correlation_id(request)
        response = await call_next(request)
        response.headers["x-correlation-id"] = correlation_id_ctx.get() or ""
        return response

    return middleware


configure_logging()
app = FastAPI(
    title="Visual Noise Museum API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
)

app.middleware("http")(correlation_middleware(app))

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    logger.info("health_check")
    return {"status": "ok"}


@app.get("/readiness", tags=["ops"])
async def readiness() -> dict[str, str]:
    logger.info("readiness_check")
    return {"status": "ready"}
