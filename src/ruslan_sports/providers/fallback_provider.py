from typing import Any
from .base import SportsProvider


class FallbackProvider(SportsProvider):
    name = "fallback"

    def fetch_today(self) -> list[dict[str, Any]]:
        return []

    def fetch_tomorrow(self) -> list[dict[str, Any]]:
        return []

    def fetch_live(self) -> list[dict[str, Any]]:
        return []
