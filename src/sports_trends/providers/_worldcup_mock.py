"""Deterministic World Cup mock data (offline / no-key fallback).

Reflects the 2026 FIFA World Cup at the Round-of-32 stage. Used when no live
source is reachable, so the World Cup feature (predictions, standings,
qualifiers) always renders. Host nations 2026: USA, Canada, Mexico.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

_NOW = datetime.now(timezone.utc)
_TODAY = _NOW.date()

HOSTS_2026 = {"USA", "Canada", "Mexico"}

CONFEDERATION = {
    "Brazil": "CONMEBOL", "Argentina": "CONMEBOL", "Uruguay": "CONMEBOL", "Colombia": "CONMEBOL",
    "France": "UEFA", "England": "UEFA", "Spain": "UEFA", "Germany": "UEFA", "Portugal": "UEFA",
    "Netherlands": "UEFA", "Croatia": "UEFA", "Norway": "UEFA", "Italy": "UEFA",
    "USA": "CONCACAF", "Mexico": "CONCACAF", "Canada": "CONCACAF",
    "Morocco": "CAF", "Senegal": "CAF", "Nigeria": "CAF",
    "Japan": "AFC", "South Korea": "AFC", "Saudi Arabia": "AFC", "Australia": "AFC",
    "Ecuador": "CONMEBOL",
}

# Approx national-team Elo seeds (relative strength) for offline predictions.
NATIONAL_ELO = {
    "Argentina": 2100, "France": 2080, "Brazil": 2050, "England": 2030, "Spain": 2020,
    "Portugal": 2000, "Netherlands": 1980, "Germany": 1970, "Croatia": 1900, "Morocco": 1880,
    "Uruguay": 1900, "Colombia": 1870, "USA": 1820, "Mexico": 1810, "Senegal": 1830,
    "Japan": 1840, "South Korea": 1790, "Australia": 1760, "Norway": 1800, "Ecuador": 1790,
    "Canada": 1750, "Nigeria": 1800, "Saudi Arabia": 1700, "Italy": 1960,
}


def _iso(days_from_today: int, hh: int, mm: int) -> str:
    d = _TODAY + timedelta(days=days_from_today)
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=timezone.utc).isoformat()


def _wc_match(mid, t1, t2, stage, day_off, hh, group="", scores=None) -> dict[str, Any]:
    status = "finished" if scores else ("live" if day_off == 0 and hh <= _NOW.hour else "scheduled")
    venue_host = next((h for h in (t1, t2) if h in HOSTS_2026), "USA")
    return {
        "id": mid,
        "sport": "football",
        "league": "FIFA World Cup", "league_id": "fifa-world-cup",
        "season": "2026", "country": "USA/Canada/Mexico",
        "home": t1, "home_id": t1.lower().replace(" ", "-"),
        "away": t2, "away_id": t2.lower().replace(" ", "-"),
        "date": (_TODAY + timedelta(days=day_off)).isoformat(),
        "kickoff": _iso(day_off, hh, 0),
        "home_score": scores[0] if scores else None,
        "away_score": scores[1] if scores else None,
        "status": status, "status_detail": "Round of 32" if not scores else "Finished",
        # World Cup specific
        "competition_type": "world_cup",
        "confederation": "INTERNATIONAL",
        "stage": stage,
        "group": group,
        "is_country_match": True,
        "neutral_venue": venue_host not in (t1, t2),
        "host_advantage": (t1 in HOSTS_2026) or (t2 in HOSTS_2026),
        "venue": f"{venue_host} stadium",
    }


# Round of 32 fixtures around "today" (the current 2026 stage).
_ROUND_OF_32 = [
    _wc_match("wc-bra-jpn", "Brazil", "Japan", "round_of_32", 1, 21),
    _wc_match("wc-arg-nor", "Argentina", "Norway", "round_of_32", 1, 18),
    _wc_match("wc-fra-sen", "France", "Senegal", "round_of_32", 1, 15),
    _wc_match("wc-eng-mex", "England", "Mexico", "round_of_32", 2, 21),
    _wc_match("wc-esp-cro", "Spain", "Croatia", "round_of_32", 2, 18),
    _wc_match("wc-ger-mar", "Germany", "Morocco", "round_of_32", 2, 15),
    _wc_match("wc-por-usa", "Portugal", "USA", "round_of_32", 0, 23),
    _wc_match("wc-ned-ecu", "Netherlands", "Ecuador", "round_of_32", 0, 20),
]

# A couple of already-finished group matches (history / standings basis).
_FINISHED = [
    _wc_match("wc-bra-srb-grp", "Brazil", "Senegal", "group_stage", -3, 18, "Group G", scores=[2, 0]),
    _wc_match("wc-arg-aus-grp", "Argentina", "Australia", "group_stage", -3, 21, "Group C", scores=[2, 1]),
]

# Qualifier fixtures (next World Cup cycle) — shows the qualifier feature.
_QUALIFIERS = [
    {
        "id": "wcq-ita-nor", "sport": "football", "league": "World Cup Qualifying — UEFA",
        "league_id": "wcq-uefa", "season": "2027", "country": "Italy",
        "home": "Italy", "home_id": "italy", "away": "Norway", "away_id": "norway",
        "date": (_TODAY + timedelta(days=2)).isoformat(), "kickoff": _iso(2, 20, 45),
        "home_score": None, "away_score": None, "status": "scheduled", "status_detail": "Qualifying",
        "competition_type": "world_cup_qualifier", "confederation": "UEFA",
        "stage": "qualifying_group", "group": "Group I", "is_country_match": True,
        "neutral_venue": False, "host_advantage": True, "venue": "Stadio Olimpico",
    },
    {
        "id": "wcq-bra-col", "sport": "football", "league": "World Cup Qualifying — CONMEBOL",
        "league_id": "wcq-conmebol", "season": "2027", "country": "Brazil",
        "home": "Brazil", "home_id": "brazil", "away": "Colombia", "away_id": "colombia",
        "date": (_TODAY + timedelta(days=3)).isoformat(), "kickoff": _iso(3, 1, 30),
        "home_score": None, "away_score": None, "status": "scheduled", "status_detail": "Qualifying",
        "competition_type": "world_cup_qualifier", "confederation": "CONMEBOL",
        "stage": "qualifying_group", "group": "CONMEBOL Table", "is_country_match": True,
        "neutral_venue": False, "host_advantage": True, "venue": "Maracanã",
    },
]

# Group standings snapshot (subset of the 12 groups).
_STANDINGS = {
    "Group A": [
        {"team": "Mexico", "played": 3, "won": 2, "draw": 1, "lost": 0, "gd": 4, "points": 7},
        {"team": "Norway", "played": 3, "won": 2, "draw": 0, "lost": 1, "gd": 2, "points": 6},
        {"team": "Saudi Arabia", "played": 3, "won": 1, "draw": 0, "lost": 2, "gd": -2, "points": 3},
        {"team": "Canada", "played": 3, "won": 0, "draw": 1, "lost": 2, "gd": -4, "points": 1},
    ],
    "Group G": [
        {"team": "Brazil", "played": 3, "won": 3, "draw": 0, "lost": 0, "gd": 6, "points": 9},
        {"team": "Senegal", "played": 3, "won": 1, "draw": 1, "lost": 1, "gd": 0, "points": 4},
        {"team": "Japan", "played": 3, "won": 1, "draw": 1, "lost": 1, "gd": 1, "points": 4},
        {"team": "Nigeria", "played": 3, "won": 0, "draw": 0, "lost": 3, "gd": -7, "points": 0},
    ],
}


def upcoming() -> list[dict[str, Any]]:
    return [dict(m) for m in _ROUND_OF_32 if m["status"] != "finished"]


def live() -> list[dict[str, Any]]:
    return [dict(m) for m in _ROUND_OF_32 if m["status"] == "live"]


def finished() -> list[dict[str, Any]]:
    return [dict(m) for m in _FINISHED]


def qualifiers() -> list[dict[str, Any]]:
    return [dict(m) for m in _QUALIFIERS]


def standings() -> dict[str, list[dict[str, Any]]]:
    return {g: [dict(r) for r in rows] for g, rows in _STANDINGS.items()}
