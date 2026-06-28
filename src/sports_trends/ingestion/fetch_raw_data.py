"""Fetch raw fixtures/results across all sports (live API or mock fallback)."""

from __future__ import annotations

from typing import Any

from ..providers import PROVIDER_REGISTRY


def fetch_raw_data(window: str = "all") -> dict[str, list[dict[str, Any]]]:
    """Return raw provider records keyed by window.

    window: "today" | "tomorrow" | "live" | "all".
    """
    today, tomorrow, live, finished = [], [], [], []
    for sport, cls in PROVIDER_REGISTRY.items():
        provider = cls()
        if window in ("today", "all"):
            today += provider.fetch_today_matches()
        if window in ("tomorrow", "all"):
            tomorrow += provider.fetch_tomorrow_matches()
        if window in ("live", "all"):
            live += provider.fetch_live_results()
            finished += provider.fetch_finished_results()
    return {"today": today, "tomorrow": tomorrow, "live": live, "finished": finished}
