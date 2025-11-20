"""API v1 router."""

from fastapi import APIRouter

from app.api.v1 import analytics, collections, patterns, sessions

api_router = APIRouter()

# Include all v1 routers
api_router.include_router(patterns.router, prefix="/patterns", tags=["patterns"])
api_router.include_router(
    collections.router, prefix="/collections", tags=["collections"]
)
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
