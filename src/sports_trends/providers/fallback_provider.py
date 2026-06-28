"""Fallback provider: aggregates deterministic mock data across all sports.

Always returns data regardless of API keys, so local development, tests, and CI
dry-runs have a realistic dataset that mirrors the public reference dashboard.
"""

from __future__ import annotations

from typing import Any

from . import _mock_data
from .base import BaseSportsProvider


class FallbackProvider(BaseSportsProvider):
    sport = "all"

    def fetch_today_matches(self) -> list[dict[str, Any]]:
        return _mock_data.today_raw()

    def fetch_tomorrow_matches(self) -> list[dict[str, Any]]:
        return _mock_data.tomorrow_raw()

    def fetch_live_results(self) -> list[dict[str, Any]]:
        return _mock_data.live_raw()

    def fetch_finished_results(self) -> list[dict[str, Any]]:
        return _mock_data.finished_raw()
