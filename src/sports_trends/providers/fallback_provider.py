"""Fallback provider: real keyless feed in production, mock everywhere else.

By default this returns deterministic mock data, so local development, tests and
CI dry-runs always have a realistic dataset with zero network calls.

In production the real, **keyless** TheSportsDB feed is enabled by setting
``SPORTS_ENABLE_LIVE_FEED=1`` (the data workflows do this). Real fixtures and
results then flow for the major leagues — no API key required — and mock is used
only as a safety net if the network call fails, so the dashboard is never blank.
Set ``SPORTS_DISABLE_NETWORK=1`` to force mock even when the feed is enabled.
"""

from __future__ import annotations

import os
from datetime import date, timedelta
from typing import Any

from ..logging_config import get_logger
from . import _mock_data
from . import thesportsdb_provider as tsd
from .base import BaseSportsProvider

logger = get_logger(__name__)


class FallbackProvider(BaseSportsProvider):
    sport = "all"

    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(api_key)
        self.live_feed = (
            os.getenv("SPORTS_ENABLE_LIVE_FEED") == "1"
            and os.getenv("SPORTS_DISABLE_NETWORK") != "1"
        )

    @property
    def mode(self) -> str:
        return "live-feed" if self.live_feed else "fallback"

    def _on_date(self, rows: list[dict[str, Any]], day: str) -> list[dict[str, Any]]:
        return [r for r in rows if (r.get("date") or "")[:10] == day]

    def fetch_today_matches(self) -> list[dict[str, Any]]:
        if self.live_feed:
            try:
                rows = self._on_date(tsd.fetch_for_keys(), date.today().isoformat())
                if rows:
                    return rows
                logger.warning("live feed (today) returned no rows, using mock")
            except Exception as exc:  # network failure → don't blank the board
                logger.warning("live feed (today) failed, using mock: %s", exc)
        return _mock_data.today_raw()

    def fetch_tomorrow_matches(self) -> list[dict[str, Any]]:
        if self.live_feed:
            try:
                tomorrow = (date.today() + timedelta(days=1)).isoformat()
                all_rows = tsd.fetch_for_keys()
                rows = self._on_date(all_rows, tomorrow)
                # Free tier is sparse per-day — fall back to the next scheduled
                # fixtures so predictions always have a slate. If the provider is
                # rate-limited or empty, use bundled mock data instead of
                # publishing a blank dashboard.
                live_rows = rows or all_rows
                if live_rows:
                    return live_rows
                logger.warning("live feed (tomorrow) returned no rows, using mock")
            except Exception as exc:
                logger.warning("live feed (tomorrow) failed, using mock: %s", exc)
        return _mock_data.tomorrow_raw()

    def fetch_live_results(self) -> list[dict[str, Any]]:
        # Keyless in-play scores aren't on the free tier; report no live games
        # rather than fabricate them (finished results still carry scores).
        if self.live_feed:
            return []
        return _mock_data.live_raw()

    def fetch_finished_results(self) -> list[dict[str, Any]]:
        if self.live_feed:
            try:
                rows = tsd.fetch_results_for_keys()
                if rows:
                    return rows
                logger.warning("live feed (results) returned no rows, using mock")
            except Exception as exc:
                logger.warning("live feed (results) failed, using mock: %s", exc)
        return _mock_data.finished_raw()
