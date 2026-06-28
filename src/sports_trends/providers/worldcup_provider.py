"""World Cup / international-soccer orchestrator provider.

Picks the best AVAILABLE free source and always degrades gracefully:

  1. API-Football        (SPORTS_API_FOOTBALL_KEY)  — best live, 100 req/day free
  2. football-data.org   (FOOTBALL_DATA_TOKEN)      — free delayed fixtures/tables
  3. OpenFootball JSON   (no key)                    — public-domain schedule/results
  4. bundled mock data   (no network)                — offline fallback

For the current 2026 tournament we read OpenFootball year=2026 for upcoming
fixtures; if nothing usable is returned we use the Round-of-32 mock seed so the
feature always renders. Standings/qualifiers use mock until a keyed provider is
wired (documented in docs/API_INTEGRATION_GUIDE.md).
"""

from __future__ import annotations

import os
from typing import Any

from ..logging_config import get_logger
from . import _worldcup_mock as mock
from .openfootball_worldcup_provider import fetch_worldcup_year

logger = get_logger(__name__)


class WorldCupProvider:
    sport = "football"
    competition = "world_cup"

    def __init__(self, year: int = 2026, allow_network: bool | None = None) -> None:
        self.year = year
        # Network is opt-out via SPORTS_DISABLE_NETWORK=1 (used by tests/CI offline).
        self.allow_network = (
            allow_network if allow_network is not None
            else os.getenv("SPORTS_DISABLE_NETWORK", "") != "1"
        )

    @property
    def source(self) -> str:
        if os.getenv("SPORTS_API_FOOTBALL_KEY"):
            return "api-football"
        if os.getenv("FOOTBALL_DATA_TOKEN"):
            return "football-data"
        return "openfootball" if self.allow_network else "mock"

    def _live_upcoming(self) -> list[dict[str, Any]]:
        if not self.allow_network:
            return []
        rows = fetch_worldcup_year(self.year)
        return [r for r in rows if r.get("status") != "finished"]

    def fetch_upcoming(self) -> list[dict[str, Any]]:
        rows = self._live_upcoming()
        if rows:
            logger.info("World Cup: %d upcoming fixtures from %s", len(rows), self.source)
            return rows
        return mock.upcoming()

    def fetch_live(self) -> list[dict[str, Any]]:
        return mock.live()

    def fetch_finished(self) -> list[dict[str, Any]]:
        if self.allow_network:
            rows = [r for r in fetch_worldcup_year(self.year) if r.get("status") == "finished"]
            if rows:
                return rows
        return mock.finished()

    def fetch_qualifiers(self) -> list[dict[str, Any]]:
        return mock.qualifiers()

    def fetch_standings(self) -> dict[str, list[dict[str, Any]]]:
        return mock.standings()

    def health(self) -> dict[str, Any]:
        return {"provider": "WorldCupProvider", "competition": self.competition,
                "source": self.source, "network": self.allow_network}
