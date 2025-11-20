"""Analytics API endpoints."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Query
from sqlalchemy import desc, func, select

from app.api.deps import DatabaseSession
from app.models.analytics import AnalyticsEvent
from app.models.pattern import Pattern
from app.schemas.analytics import ExhibitUsage, PopularParameters, TrendingPattern

router = APIRouter()


@router.get("/popular-parameters", response_model=list[PopularParameters])
async def get_popular_parameters(
    db: DatabaseSession,
    exhibit_type: str | None = None,
    limit: int = Query(10, ge=1, le=50),
) -> list[PopularParameters]:
    """Get most popular parameter combinations."""
    # This is a simplified implementation
    # In production, you'd want to aggregate parameter usage from patterns
    query = select(Pattern)

    if exhibit_type:
        query = query.where(Pattern.exhibit_type == exhibit_type)

    query = query.where(Pattern.is_public == True).limit(1000)  # noqa: E712

    result = await db.execute(query)
    patterns = list(result.scalars().all())

    # Analyze parameters
    param_stats: dict[str, dict] = {}

    for pattern in patterns:
        for param_name, param_value in pattern.parameters.items():
            if param_name not in param_stats:
                param_stats[param_name] = {
                    "values": [],
                    "exhibit_type": pattern.exhibit_type,
                }

            if isinstance(param_value, (int, float)):
                param_stats[param_name]["values"].append(param_value)

    # Build response
    popular_params = []
    for param_name, stats in list(param_stats.items())[:limit]:
        if stats["values"]:
            import numpy as np

            values = np.array(stats["values"])
            popular_params.append(
                PopularParameters(
                    exhibit_type=stats["exhibit_type"],
                    parameter_name=param_name,
                    value_distribution={},  # Simplified
                    avg_value=float(np.mean(values)),
                    median_value=float(np.median(values)),
                    sample_count=len(values),
                )
            )

    return popular_params


@router.get("/exhibit-usage", response_model=list[ExhibitUsage])
async def get_exhibit_usage(
    db: DatabaseSession,
) -> list[ExhibitUsage]:
    """Get usage statistics by exhibit type."""
    result = await db.execute(
        select(
            Pattern.exhibit_type,
            func.count(Pattern.id).label("pattern_count"),
            func.sum(Pattern.views_count).label("total_views"),
            func.sum(Pattern.likes_count).label("total_likes"),
            func.avg(Pattern.likes_count).label("avg_likes"),
            func.max(Pattern.created_at).label("most_recent"),
        )
        .where(Pattern.is_public == True)  # noqa: E712
        .group_by(Pattern.exhibit_type)
        .order_by(desc("pattern_count"))
    )

    rows = result.all()

    return [
        ExhibitUsage(
            exhibit_type=row.exhibit_type,
            pattern_count=row.pattern_count,
            total_views=row.total_views or 0,
            total_likes=row.total_likes or 0,
            avg_likes_per_pattern=float(row.avg_likes or 0),
            most_recent_created_at=row.most_recent,
        )
        for row in rows
    ]


@router.get("/trends", response_model=list[TrendingPattern])
async def get_trends(
    db: DatabaseSession,
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(20, ge=1, le=100),
) -> list[TrendingPattern]:
    """Get trending patterns over time period."""
    since = datetime.utcnow() - timedelta(days=days)

    # Calculate trending score: recent activity weighted
    result = await db.execute(
        select(Pattern)
        .where(Pattern.is_public == True, Pattern.created_at >= since)  # noqa: E712
        .order_by(
            desc(
                Pattern.likes_count * 3
                + Pattern.views_count * 0.5
                + Pattern.forks_count * 5
            )
        )
        .limit(limit)
    )

    patterns = list(result.scalars().all())

    return [
        TrendingPattern(
            pattern_id=p.id,
            title=p.title,
            exhibit_type=p.exhibit_type,
            likes_count=p.likes_count,
            views_count=p.views_count,
            forks_count=p.forks_count,
            trending_score=float(
                p.likes_count * 3 + p.views_count * 0.5 + p.forks_count * 5
            ),
            created_at=p.created_at,
        )
        for p in patterns
    ]


@router.post("/events", status_code=201)
async def track_event(
    event_type: str,
    pattern_id: str | None = None,
    event_metadata: dict | None = None,
    db: DatabaseSession = None,
) -> dict:
    """Track analytics event."""
    # Simplified implementation - in production, use background tasks
    return {"success": True, "event_type": event_type}
