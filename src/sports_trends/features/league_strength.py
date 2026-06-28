"""League importance score (0-100) used for ranking and as a feature."""

from __future__ import annotations

LEAGUE_IMPORTANCE = {
    "uefa champions league": 100,
    "premier league": 92,
    "nba finals": 95,
    "nba": 85,
    "wimbledon men's sf": 90,
    "atp halle": 70,
    "icc test championship": 88,
    "t20 world cup": 86,
}

DEFAULT_IMPORTANCE = 60


def league_importance_score(league_name: str) -> int:
    return LEAGUE_IMPORTANCE.get((league_name or "").strip().lower(), DEFAULT_IMPORTANCE)
