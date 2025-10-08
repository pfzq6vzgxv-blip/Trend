"""Persistence utilities for the tracker state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterable, List

from .data_models import MetricSnapshot, TrendRecord


class TrendStore:
    """Persist history to disk so the tracker can compute deltas over time."""

    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self._cache: Dict[str, TrendRecord] = {}
        if self.path.exists():
            self._load()

    def _key(self, record: TrendRecord) -> str:
        return f"{record.platform}:{record.external_id}"

    def _load(self) -> None:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        for payload in raw:
            record = TrendRecord.from_dict(payload, payload.get("platform", "unknown"))
            self._cache[self._key(record)] = record

    def save(self) -> None:
        serialized: List[Dict[str, object]] = []
        for record in self._cache.values():
            payload = {
                "platform": record.platform,
                "id": record.external_id,
                "title": record.title,
                "author": record.author,
                "url": record.url,
                "caption": record.caption,
                "language": record.language,
                "tags": record.tags,
                "country": record.country,
                "timestamp": record.timestamp.isoformat(),
                "views": record.views,
                "likes": record.likes,
                "comments": record.comments,
                "shares": record.shares,
                "history": [
                    {
                        "timestamp": snap.timestamp.isoformat(),
                        "views": snap.views,
                        "likes": snap.likes,
                        "comments": snap.comments,
                        "shares": snap.shares,
                    }
                    for snap in record.history
                ],
            }
            serialized.append(payload)
        self.path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")

    def update(self, records: Iterable[TrendRecord]) -> List[TrendRecord]:
        merged: List[TrendRecord] = []
        for record in records:
            key = self._key(record)
            if key in self._cache:
                stored = self._cache[key]
                history = stored.history + [stored.current_snapshot()]
                merged_record = TrendRecord(
                    platform=record.platform,
                    external_id=record.external_id,
                    title=record.title or stored.title,
                    author=record.author or stored.author,
                    url=record.url or stored.url,
                    caption=record.caption or stored.caption,
                    language=record.language or stored.language,
                    tags=record.tags or stored.tags,
                    country=record.country or stored.country,
                    timestamp=record.timestamp,
                    views=record.views,
                    likes=record.likes,
                    comments=record.comments,
                    shares=record.shares,
                    history=history,
                    extra=record.extra or stored.extra,
                )
            else:
                merged_record = record
            self._cache[key] = merged_record
            merged.append(merged_record)
        self.save()
        return merged

    def records(self) -> List[TrendRecord]:
        return list(self._cache.values())
