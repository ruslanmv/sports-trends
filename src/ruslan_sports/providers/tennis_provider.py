from typing import Any
from .base import SportsProvider


class TennisProvider(SportsProvider):
    name = "tennis-provider"

    def fetch_today(self) -> list[dict[str, Any]]:
        # TODO: Implement provider API call.
        return []

    def fetch_tomorrow(self) -> list[dict[str, Any]]:
        # TODO: Implement provider API call.
        return []

    def fetch_live(self) -> list[dict[str, Any]]:
        # TODO: Implement provider API call.
        return []
