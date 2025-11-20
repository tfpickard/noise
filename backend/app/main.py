"""
FastAPI application entrypoint for the Visual Noise Museum backend.
This lightweight implementation sketches the full API surface with
progressive enhancement hooks and structured logging. Data storage is an
in-memory placeholder to keep the repo self-contained; swap with the
PostgreSQL/Redis stack for production deployments.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from app.api.v1.router import api_router

logger = structlog.get_logger()

app = FastAPI(
    title="Visual Noise Museum API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    """Liveness probe."""
    logger.info("health_check")
    return {"status": "ok"}


@app.get("/readiness", tags=["ops"])
async def readiness() -> dict[str, str]:
    """Readiness probe; in production checks DB/Redis connectivity."""
    logger.info("readiness_check")
    return {"status": "ready"}
