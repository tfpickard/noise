from __future__ import annotations

from fastapi import APIRouter

from . import patterns, collections, analytics, collaborate, sessions, export, auth, similarity

api_router = APIRouter()
api_router.include_router(patterns.router, prefix="/patterns", tags=["patterns"])
api_router.include_router(collections.router, prefix="/collections", tags=["collections"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(collaborate.router, prefix="/collaborate", tags=["collaborate"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(similarity.router, prefix="/patterns", tags=["similarity"])
