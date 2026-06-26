from typing import Any
from .base import SportsProvider


class EspnProvider(SportsProvider):
    name = "espn"

    def fetch_today(self) -> list[dict[str, Any]]:
        # TODO: Implement provider API call.
        return []

    def fetch_tomorrow(self) -> list[dict[str, Any]]:
        # TODO: Implement provider API call.
        return []

    def fetch_live(self) -> list[dict[str, Any]]:
        # TODO: Implement provider API call.
        return []
