"""HTTP-backed data source implementations."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional

import requests

from ..data_models import TrendRecord
from .base import TrendDataSource


class HTTPJSONSource(TrendDataSource):
    """Generic HTTP source that expects JSON payloads."""

    def __init__(
        self,
        platform: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, str]] = None,
        payload_path: Optional[str] = None,
    ) -> None:
        self.platform = platform
        self.url = url
        self.headers = headers or {}
        self.params = params or {}
        self.payload_path = payload_path

    def fetch_latest(self) -> List[TrendRecord]:  # noqa: D401 - see base class
        response = requests.get(self.url, headers=self.headers, params=self.params, timeout=30)
        response.raise_for_status()
        data = response.json()
        if self.payload_path:
            for segment in self.payload_path.split("."):
                data = data[segment]
        if isinstance(data, dict):
            data = data.get("items") or data.get("list") or data.get("data") or []
        records: List[TrendRecord] = []
        for entry in data:
            normalized = self._normalize(entry)
            records.append(normalized)
        return records

    def _normalize(self, payload: Dict[str, object]) -> TrendRecord:
        timestamp = payload.get("timestamp") or payload.get("createTime")
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(float(timestamp))
        item = {
            "id": payload.get("id") or payload.get("video_id") or payload.get("aweme_id"),
            "title": payload.get("title") or payload.get("desc") or payload.get("caption", ""),
            "author": payload.get("author", {}).get("uniqueId")
            if isinstance(payload.get("author"), dict)
            else payload.get("author")
            or payload.get("username")
            or payload.get("user"),
            "url": payload.get("permalink")
            or payload.get("video_url")
            or payload.get("share_url")
            or payload.get("url"),
            "caption": payload.get("caption") or payload.get("desc"),
            "language": payload.get("language"),
            "tags": payload.get("hashtags") or payload.get("challenges") or [],
            "timestamp": timestamp,
            "views": payload.get("playCount")
            or payload.get("view_count")
            or payload.get("views")
            or 0,
            "likes": payload.get("diggCount")
            or payload.get("like_count")
            or payload.get("likes")
            or 0,
            "comments": payload.get("commentCount")
            or payload.get("comment_count")
            or payload.get("comments")
            or 0,
            "shares": payload.get("shareCount")
            or payload.get("share_count")
            or payload.get("shares")
            or 0,
            "history": payload.get("history", []),
        }
        return TrendRecord.from_dict(item, self.platform)


class LocalJSONSource(TrendDataSource):
    """Local file source used for sample or offline runs."""

    def __init__(self, platform: str, path: str) -> None:
        self.platform = platform
        self.path = path

    def fetch_latest(self) -> List[TrendRecord]:  # noqa: D401 - see base class
        with open(self.path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return [TrendRecord.from_dict(item, self.platform) for item in data]
