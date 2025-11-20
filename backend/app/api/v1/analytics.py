from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter

from app.schemas.analytics import AnalyticsResponse, AnalyticsSlice

router = APIRouter()


def _simple_response(metric: str) -> AnalyticsResponse:
    return AnalyticsResponse(
        generated_at=datetime.now(timezone.utc),
        slices=[AnalyticsSlice(label=metric, count=1)],
    )


@router.get("/popular-parameters", response_model=AnalyticsResponse)
async def popular_parameters() -> AnalyticsResponse:
    return _simple_response("popular_parameters")


@router.get("/exhibit-usage", response_model=AnalyticsResponse)
async def exhibit_usage() -> AnalyticsResponse:
    return _simple_response("exhibit_usage")


@router.get("/trends", response_model=AnalyticsResponse)
async def trends() -> AnalyticsResponse:
    return _simple_response("trends")
