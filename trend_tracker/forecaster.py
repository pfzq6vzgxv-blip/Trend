"""Simple forecasting utilities for meme trend metrics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Tuple

from .data_models import MetricSnapshot, TrendRecord


@dataclass(slots=True)
class TrendForecast:
    record: TrendRecord
    horizon_hours: int
    projected_views: List[Tuple[datetime, float]]
    projected_engagement_rate: float


def forecast(records: List[TrendRecord], horizon_hours: int = 6) -> List[TrendForecast]:
    """Return linear projections for the supplied records."""

    outputs: List[TrendForecast] = []
    for record in records:
        snapshots = list(record.iter_history())
        if len(snapshots) < 2:
            snapshots = _bootstrap_snapshots(record)
        times, views = _snapshots_to_series(snapshots)
        slope, intercept = _linear_regression(times, views)
        projections: List[Tuple[datetime, float]] = []
        last_timestamp = snapshots[-1].timestamp
        for hour in range(1, horizon_hours + 1):
            future_time = last_timestamp + timedelta(hours=hour)
            future_epoch = future_time.timestamp()
            future_views = max(slope * future_epoch + intercept, 0)
            projections.append((future_time, future_views))
        projected_engagement = _project_engagement(record)
        outputs.append(
            TrendForecast(
                record=record,
                horizon_hours=horizon_hours,
                projected_views=projections,
                projected_engagement_rate=projected_engagement,
            )
        )
    return outputs


def _bootstrap_snapshots(record: TrendRecord) -> List[MetricSnapshot]:
    snapshot = record.current_snapshot()
    earlier = MetricSnapshot(
        timestamp=snapshot.timestamp - timedelta(hours=1),
        views=max(snapshot.views - 1000, 0),
        likes=max(snapshot.likes - 100, 0),
        comments=max(snapshot.comments - 10, 0),
        shares=max(snapshot.shares - 10, 0),
    )
    return [earlier, snapshot]


def _snapshots_to_series(snapshots: List[MetricSnapshot]) -> Tuple[List[float], List[float]]:
    return [snap.timestamp.timestamp() for snap in snapshots], [snap.views for snap in snapshots]


def _linear_regression(xs: List[float], ys: List[float]) -> Tuple[float, float]:
    n = len(xs)
    if n == 0:
        return 0.0, 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs) or 1e-6
    slope = numerator / denominator
    intercept = mean_y - slope * mean_x
    return slope, intercept


def _project_engagement(record: TrendRecord) -> float:
    total_interactions = record.likes + record.comments + record.shares
    return total_interactions / max(record.views, 1)
