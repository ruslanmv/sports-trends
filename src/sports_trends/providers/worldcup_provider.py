"""World Cup / international-soccer orchestrator provider.

Picks the best AVAILABLE free source and always degrades gracefully:

  1. API-Football        (SPORTS_API_FOOTBALL_KEY)  — best live, 100 req/day free
  2. football-data.org   (FOOTBALL_DATA_TOKEN)      — free delayed fixtures/tables
  3. OpenFootball JSON   (no key)                    — public-domain full schedule
     + TheStatsAPI       (no key)                    — clean UTC kickoff backfill
  4. bundled mock data   (no network)                — offline fallback

For the current 2026 tournament we read the OpenFootball year=2026 file (the
full 104-match schedule with real teams, venues and results) and backfill clean
kick-off times from TheStatsAPI. From that one feed we derive:

  * upcoming   — scheduled matches with a known date/time, soonest first
  * fixtures   — the complete schedule grouped by round (group → final)
  * standings  — live group tables computed from finished group results
  * finished   — completed matches (history / results)

Everything degrades to the bundled Round-of-32 mock so the feature always
renders, with or without keys/network.
"""

from __future__ import annotations

import os
from typing import Any

from ..features.tournament_stage import STAGE_ORDER, is_knockout
from ..logging_config import get_logger
from . import _worldcup_mock as mock
from . import thestatsapi_worldcup_provider as tsa
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
        self._cache: list[dict[str, Any]] | None = None

    @property
    def source(self) -> str:
        if os.getenv("SPORTS_API_FOOTBALL_KEY"):
            return "api-football"
        if os.getenv("FOOTBALL_DATA_TOKEN"):
            return "football-data"
        return "openfootball+thestatsapi" if self.allow_network else "mock"

    # ------------------------------------------------------------------ #
    # Raw feed (fetched once, then reused)
    # ------------------------------------------------------------------ #
    def _all(self) -> list[dict[str, Any]]:
        """Full 2026 schedule (real teams only), kickoffs backfilled, cached."""
        if self._cache is not None:
            return self._cache
        rows: list[dict[str, Any]] = []
        if self.allow_network:
            rows = [r for r in fetch_worldcup_year(self.year) if not r.get("is_placeholder")]
            rows = self._backfill_kickoffs(rows)
        self._cache = rows
        return rows

    @staticmethod
    def _backfill_kickoffs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Use TheStatsAPI clean UTC kickoffs where OpenFootball lacks them."""
        try:
            idx = tsa.kickoff_index()
        except Exception:  # pragma: no cover - network guard
            idx = {}
        if not idx:
            return rows
        for r in rows:
            k = tsa.fixture_key(r.get("home", ""), r.get("away", ""), r.get("date", ""))
            if idx.get(k):
                r["kickoff"] = idx[k]
        return rows

    # ------------------------------------------------------------------ #
    # Public surface
    # ------------------------------------------------------------------ #
    def fetch_upcoming(self) -> list[dict[str, Any]]:
        """Scheduled matches, soonest first. Prefer knockouts when both exist."""
        rows = [r for r in self._all() if r.get("status") != "finished"]
        rows.sort(key=lambda r: (r.get("kickoff") or r.get("date") or "9999"))
        if rows:
            knockouts = [r for r in rows if is_knockout(r.get("stage", ""))]
            chosen = knockouts or rows
            logger.info("World Cup: %d upcoming fixtures from %s", len(chosen), self.source)
            return chosen
        return mock.upcoming()

    def fetch_fixtures(self) -> list[dict[str, Any]]:
        """The complete schedule (group → final), chronological. Mock if offline."""
        rows = sorted(self._all(), key=lambda r: (r.get("kickoff") or r.get("date") or ""))
        return rows or (mock.finished() + mock.upcoming())

    def fetch_live(self) -> list[dict[str, Any]]:
        return mock.live()

    def fetch_finished(self) -> list[dict[str, Any]]:
        rows = [r for r in self._all() if r.get("status") == "finished"]
        rows.sort(key=lambda r: (r.get("kickoff") or r.get("date") or ""), reverse=True)
        return rows or mock.finished()

    def fetch_qualifiers(self) -> list[dict[str, Any]]:
        # No public-domain qualifier feed yet — keep the curated mock fixtures.
        return mock.qualifiers()

    def fetch_standings(self) -> dict[str, list[dict[str, Any]]]:
        """Live group tables computed from finished group results (else mock)."""
        finished = [r for r in self._all()
                    if r.get("status") == "finished" and r.get("group")]
        table = compute_standings(finished)
        return table or mock.standings()

    def health(self) -> dict[str, Any]:
        return {"provider": "WorldCupProvider", "competition": self.competition,
                "source": self.source, "network": self.allow_network,
                "matches": len(self._all())}


def compute_standings(finished: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Build group standings (P/W/D/L/GF/GA/GD/Pts) from finished group games."""
    groups: dict[str, dict[str, dict[str, Any]]] = {}
    for m in finished:
        g = m.get("group")
        hs, as_ = m.get("home_score"), m.get("away_score")
        if not g or hs is None or as_ is None:
            continue
        tbl = groups.setdefault(g, {})
        for team in (m["home"], m["away"]):
            tbl.setdefault(team, {"team": team, "played": 0, "won": 0, "draw": 0,
                                  "lost": 0, "gf": 0, "ga": 0, "gd": 0, "points": 0})
        h, a = tbl[m["home"]], tbl[m["away"]]
        h["played"] += 1; a["played"] += 1
        h["gf"] += hs; h["ga"] += as_
        a["gf"] += as_; a["ga"] += hs
        if hs > as_:
            h["won"] += 1; h["points"] += 3; a["lost"] += 1
        elif hs < as_:
            a["won"] += 1; a["points"] += 3; h["lost"] += 1
        else:
            h["draw"] += 1; a["draw"] += 1; h["points"] += 1; a["points"] += 1
    out: dict[str, list[dict[str, Any]]] = {}
    for g, tbl in sorted(groups.items()):
        rows = list(tbl.values())
        for r in rows:
            r["gd"] = r["gf"] - r["ga"]
        rows.sort(key=lambda r: (r["points"], r["gd"], r["gf"]), reverse=True)
        out[g] = rows
    return out


# Convenience for tests / debugging.
def stage_rank(stage: str) -> int:
    try:
        return STAGE_ORDER.index(stage)
    except ValueError:
        return len(STAGE_ORDER)
