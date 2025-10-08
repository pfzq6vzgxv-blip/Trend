"""Compute engagement metrics for trend records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable, List

from .data_models import MetricSnapshot, TrendRecord


@dataclass(slots=True)
class TrendMetrics:
    record: TrendRecord
    engagement_rate: float
    velocity_per_hour: float
    acceleration_per_hour: float
    virality_score: float


def calculate_metrics(records: Iterable[TrendRecord]) -> List[TrendMetrics]:
    """Return computed metrics for each meme clip."""

    metrics: List[TrendMetrics] = []
    for record in records:
        snapshots = list(record.iter_history())
        if len(snapshots) < 2:
            snapshots.append(record.current_snapshot())
        engagement_rate = _engagement_rate(record)
        velocity = _velocity_per_hour(snapshots)
        acceleration = _acceleration_per_hour(snapshots)
        virality_score = _virality(record, engagement_rate, velocity)
        metrics.append(
            TrendMetrics(
                record=record,
                engagement_rate=engagement_rate,
                velocity_per_hour=velocity,
                acceleration_per_hour=acceleration,
                virality_score=virality_score,
            )
        )
    return metrics


def _engagement_rate(record: TrendRecord) -> float:
    denominator = max(record.views, 1)
    return (record.likes + record.comments + record.shares) / denominator


def _velocity_per_hour(snapshots: List[MetricSnapshot]) -> float:
    if len(snapshots) < 2:
        return 0.0
    start, end = snapshots[-2], snapshots[-1]
    delta_views = end.views - start.views
    delta_time = (end.timestamp - start.timestamp).total_seconds() / 3600 or 1e-6
    return delta_views / delta_time


def _acceleration_per_hour(snapshots: List[MetricSnapshot]) -> float:
    if len(snapshots) < 3:
        return 0.0
    velocities = []
    for first, second in zip(snapshots[:-1], snapshots[1:]):
        delta_views = second.views - first.views
        delta_time = (second.timestamp - first.timestamp).total_seconds() / 3600 or 1e-6
        velocities.append(delta_views / delta_time)
    if len(velocities) < 2:
        return 0.0
    return velocities[-1] - velocities[-2]


def _virality(record: TrendRecord, engagement_rate: float, velocity: float) -> float:
    now = datetime.now(timezone.utc)
    timestamp = record.timestamp
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    freshness_hours = max((now - timestamp).total_seconds() / 3600, 1)
    weighted_velocity = velocity / freshness_hours
    normalization = max(record.views, 1)
    return (engagement_rate * 0.6 + min(weighted_velocity / normalization, 1.0) * 0.4) * 100
