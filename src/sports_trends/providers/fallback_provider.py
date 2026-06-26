"""Placeholder fallback provider."""

from __future__ import annotations

class FallbackProvider:
    sport = "fallback"

    def fetch_today(self) -> list[dict]:
        return []

    def fetch_tomorrow(self) -> list[dict]:
        return []

    def fetch_live(self) -> list[dict]:
        return []
