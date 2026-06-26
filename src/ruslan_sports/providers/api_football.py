from typing import Any
from .base import SportsProvider


class ApiFootballProvider(SportsProvider):
    name = "api-football"

    def fetch_today(self) -> list[dict[str, Any]]:
        # TODO: Implement provider API call.
        return []

    def fetch_tomorrow(self) -> list[dict[str, Any]]:
        # TODO: Implement provider API call.
        return []

    def fetch_live(self) -> list[dict[str, Any]]:
        # TODO: Implement provider API call.
        return []
