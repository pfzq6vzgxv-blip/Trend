"""Shared data models for the trend tracker."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Iterable, List, Optional


@dataclass(slots=True)
class MetricSnapshot:
    """Historical snapshot of engagement metrics for a meme clip."""

    timestamp: datetime
    views: int
    likes: int
    comments: int
    shares: int

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "MetricSnapshot":
        return cls(
            timestamp=_ensure_datetime(payload["timestamp"]),
            views=int(payload.get("views", 0)),
            likes=int(payload.get("likes", 0)),
            comments=int(payload.get("comments", 0)),
            shares=int(payload.get("shares", 0)),
        )


@dataclass(slots=True)
class TrendRecord:
    """Normalized payload across the supported platforms."""

    platform: str
    external_id: str
    title: str
    author: str
    url: str
    caption: Optional[str]
    language: Optional[str]
    tags: List[str] = field(default_factory=list)
    country: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    history: List[MetricSnapshot] = field(default_factory=list)
    extra: Dict[str, object] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: Dict[str, object], platform: str) -> "TrendRecord":
        history_payload = payload.get("history") or []
        history: List[MetricSnapshot] = [
            MetricSnapshot.from_dict(item) for item in history_payload
        ]
        return cls(
            platform=platform,
            external_id=str(payload.get("id") or payload.get("external_id")),
            title=str(payload.get("title") or payload.get("description") or ""),
            author=str(payload.get("author") or payload.get("username") or "unknown"),
            url=str(payload.get("url") or payload.get("permalink") or ""),
            caption=payload.get("caption"),
            language=payload.get("language"),
            tags=list(payload.get("tags") or []),
            country=payload.get("country"),
            timestamp=_ensure_datetime(payload.get("timestamp") or datetime.utcnow()),
            views=int(payload.get("views", 0)),
            likes=int(payload.get("likes", 0)),
            comments=int(payload.get("comments", 0)),
            shares=int(payload.get("shares", 0)),
            history=history,
            extra={k: v for k, v in payload.items() if k not in {
                "id",
                "external_id",
                "title",
                "description",
                "author",
                "username",
                "url",
                "permalink",
                "caption",
                "language",
                "tags",
                "country",
                "timestamp",
                "views",
                "likes",
                "comments",
                "shares",
                "history",
            }},
        )

    def iter_history(self) -> Iterable[MetricSnapshot]:
        yield from sorted(self.history + [self.current_snapshot()], key=lambda snap: snap.timestamp)

    def current_snapshot(self) -> MetricSnapshot:
        return MetricSnapshot(
            timestamp=self.timestamp,
            views=self.views,
            likes=self.likes,
            comments=self.comments,
            shares=self.shares,
        )


def _ensure_datetime(value: object) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value))
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"Unsupported datetime string: {value}") from exc
    raise TypeError(f"Unsupported datetime type: {type(value)!r}")
