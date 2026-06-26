"""Placeholder basketball provider."""

from __future__ import annotations

class BasketballProvider:
    sport = "basketball"

    def fetch_today(self) -> list[dict]:
        return []

    def fetch_tomorrow(self) -> list[dict]:
        return []

    def fetch_live(self) -> list[dict]:
        return []
