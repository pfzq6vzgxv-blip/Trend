"""Base utilities for fetching trend data."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List

from ..data_models import TrendRecord


class TrendDataSource(ABC):
    """Interface for retrieving normalized trend records."""

    platform: str

    @abstractmethod
    def fetch_latest(self) -> List[TrendRecord]:
        """Retrieve the most recent records from the platform."""

    def __iter__(self) -> Iterable[TrendRecord]:
        return iter(self.fetch_latest())
