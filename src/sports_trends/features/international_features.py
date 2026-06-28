"""Feature construction for international (country-vs-country) matches."""

from __future__ import annotations

from typing import Any

from ..providers._worldcup_mock import HOSTS_2026, NATIONAL_ELO
from .tournament_stage import confederation_strength, stage_importance

HOST_ELO_BONUS = 60.0
DEFAULT_ELO = 1750.0


def national_elo(team: str) -> float:
    return float(NATIONAL_ELO.get(team, DEFAULT_ELO))


def international_features(match: dict[str, Any]) -> dict[str, Any]:
    home, away = match.get("home", match.get("home_team", "")), match.get("away", match.get("away_team", ""))
    stage = match.get("stage", "group_stage")
    neutral = bool(match.get("neutral_venue", True))

    home_elo = national_elo(home)
    away_elo = national_elo(away)
    # Host advantage only applies at a non-neutral venue for the host nation.
    if not neutral:
        if home in HOSTS_2026:
            home_elo += HOST_ELO_BONUS
        if away in HOSTS_2026:
            away_elo += HOST_ELO_BONUS

    return {
        "home_elo": home_elo,
        "away_elo": away_elo,
        "elo_diff": home_elo - away_elo,
        "neutral_venue": neutral,
        "host_advantage": bool(match.get("host_advantage", False)),
        "stage": stage,
        "stage_importance": stage_importance(stage),
        "confederation_strength": confederation_strength(match.get("confederation")),
        "is_country_match": bool(match.get("is_country_match", True)),
    }
