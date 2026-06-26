"""Placeholder esports provider."""

from __future__ import annotations

class EsportsProvider:
    sport = "esports"

    def fetch_today(self) -> list[dict]:
        return []

    def fetch_tomorrow(self) -> list[dict]:
        return []

    def fetch_live(self) -> list[dict]:
        return []
