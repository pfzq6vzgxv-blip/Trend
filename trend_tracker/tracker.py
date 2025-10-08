"""Coordinator module that combines fetching, analytics, and forecasting."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .analyzer import TrendMetrics, calculate_metrics
from .config import TrackerConfig, load_config
from .data_models import TrendRecord
from .data_sources import build_instagram_source, build_tiktok_source
from .data_sources.base import TrendDataSource
from .forecaster import TrendForecast, forecast
from .storage import TrendStore


logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TrackerResult:
    fetched: List[TrendRecord]
    metrics: List[TrendMetrics]
    forecasts: List[TrendForecast]


class TrendTracker:
    """Coordinates the workflow for meme trend analytics."""

    def __init__(
        self,
        config: Optional[TrackerConfig] = None,
        *,
        tiktok_source: Optional[TrendDataSource] = None,
        instagram_source: Optional[TrendDataSource] = None,
        storage: Optional[TrendStore] = None,
    ) -> None:
        self.config = config or load_config()
        self.store = storage or TrendStore(self.config.storage_path)
        self.tiktok_source = tiktok_source or build_tiktok_source(self.config.tiktok)
        self.instagram_source = instagram_source or build_instagram_source(self.config.instagram)

    def run_once(self) -> TrackerResult:
        """Fetch latest data, compute analytics, and produce forecasts."""

        logger.info("Fetching fresh data from TikTok and Instagram")
        fetched: List[TrendRecord] = []
        for source in (self.tiktok_source, self.instagram_source):
            try:
                fetched.extend(source.fetch_latest())
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.exception("Failed to fetch data from %s", source.platform)
        logger.debug("Fetched %d records", len(fetched))

        merged_records = self.store.update(fetched)
        metrics = calculate_metrics(merged_records)
        forecasts = forecast([metric.record for metric in metrics])
        metrics.sort(key=lambda m: m.virality_score, reverse=True)
        return TrackerResult(fetched=merged_records, metrics=metrics, forecasts=forecasts)

    def render_report(self, result: TrackerResult, *, limit: int = 10) -> str:
        """Format the results in a human-readable table."""

        lines = [
            "Live Meme Trend Tracker",
            "======================",
            f"Generated at: {datetime.utcnow().isoformat()}Z",
            "",
            f"Top {limit} Memes by Virality Score:",
            "",
        ]
        for metric in result.metrics[:limit]:
            record = metric.record
            forecast_entry = next((f for f in result.forecasts if f.record == record), None)
            future_views = (
                forecast_entry.projected_views[-1][1]
                if forecast_entry and forecast_entry.projected_views
                else record.views
            )
            lines.extend(
                [
                    f"[{record.platform}] {record.title or 'Untitled'}",
                    f"  Creator: {record.author} | Views: {record.views:,} | Engagement: {metric.engagement_rate:.2%}",
                    f"  Velocity: {metric.velocity_per_hour:,.0f} views/hr | Accel: {metric.acceleration_per_hour:,.0f}",
                    f"  Virality Score: {metric.virality_score:.2f} | Projected Views (+{forecast_entry.horizon_hours}h): {future_views:,.0f}",
                    f"  URL: {record.url}",
                    "",
                ]
            )
        return "\n".join(lines)


__all__ = ["TrendTracker", "TrackerResult"]
