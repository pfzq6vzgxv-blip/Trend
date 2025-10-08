"""Data source factories."""

from __future__ import annotations

from typing import Optional

from ..config import InstagramConfig, TikTokConfig
from .base import TrendDataSource
from .http_source import HTTPJSONSource, LocalJSONSource


def build_tiktok_source(config: TikTokConfig, sample_path: Optional[str] = None) -> TrendDataSource:
    if sample_path:
        return LocalJSONSource("tiktok", sample_path)
    if config.dataset_url:
        return HTTPJSONSource("tiktok", config.dataset_url)
    headers = {
        "User-Agent": "Mozilla/5.0",
    }
    params = {}
    if config.country:
        params["region"] = config.country
    return HTTPJSONSource("tiktok", config.api_url, headers=headers, params=params)


def build_instagram_source(config: InstagramConfig, sample_path: Optional[str] = None) -> TrendDataSource:
    if sample_path:
        return LocalJSONSource("instagram", sample_path)
    if config.dataset_url:
        return HTTPJSONSource("instagram", config.dataset_url)
    headers = {"User-Agent": "Mozilla/5.0"}
    if config.rapidapi_key:
        headers.update(
            {
                "X-RapidAPI-Key": config.rapidapi_key,
                "X-RapidAPI-Host": "instagram28.p.rapidapi.com",
            }
        )
    params = {}
    if config.country:
        params["country"] = config.country
    return HTTPJSONSource("instagram", config.api_url, headers=headers, params=params, payload_path="result")
