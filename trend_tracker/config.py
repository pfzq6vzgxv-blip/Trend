"""Configuration helpers for the trend tracker."""

from __future__ import annotations

from dataclasses import dataclass
from os import getenv
from typing import Optional


@dataclass(slots=True)
class TikTokConfig:
    api_url: str = "https://www.tiktok.com/api/recommend/item_list/"
    dataset_url: Optional[str] = None
    rapidapi_key: Optional[str] = None
    apify_token: Optional[str] = None
    country: Optional[str] = None


@dataclass(slots=True)
class InstagramConfig:
    api_url: str = "https://instagram28.p.rapidapi.com/instagram/reels/trending/"
    rapidapi_key: Optional[str] = None
    dataset_url: Optional[str] = None
    apify_token: Optional[str] = None
    country: Optional[str] = None


@dataclass(slots=True)
class TrackerConfig:
    tiktok: TikTokConfig
    instagram: InstagramConfig
    polling_interval: int = 900  # seconds
    storage_path: str = "tracker_state.json"


def load_config() -> TrackerConfig:
    """Load configuration from environment variables."""

    tiktok = TikTokConfig(
        api_url=getenv("TIKTOK_API_URL", TikTokConfig.api_url),
        dataset_url=getenv("TIKTOK_DATASET_URL"),
        rapidapi_key=getenv("TIKTOK_RAPIDAPI_KEY"),
        apify_token=getenv("TIKTOK_APIFY_TOKEN"),
        country=getenv("TIKTOK_COUNTRY"),
    )

    instagram = InstagramConfig(
        api_url=getenv("INSTAGRAM_API_URL", InstagramConfig.api_url),
        dataset_url=getenv("INSTAGRAM_DATASET_URL"),
        rapidapi_key=getenv("INSTAGRAM_RAPIDAPI_KEY"),
        apify_token=getenv("INSTAGRAM_APIFY_TOKEN"),
        country=getenv("INSTAGRAM_COUNTRY"),
    )

    polling_interval = int(getenv("TREND_TRACKER_INTERVAL", "900"))
    storage_path = getenv("TREND_TRACKER_STATE", "tracker_state.json")

    return TrackerConfig(
        tiktok=tiktok,
        instagram=instagram,
        polling_interval=polling_interval,
        storage_path=storage_path,
    )
