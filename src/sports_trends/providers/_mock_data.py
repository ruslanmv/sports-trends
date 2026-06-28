"""Deterministic mock fixtures used when no real API key is configured.

The data mirrors the public reference dashboard (Real Madrid vs Man City,
Lakers vs Celtics, Sinner vs Alcaraz, India vs Australia, the live Arsenal /
Heat / England / Zverev results, etc.) so the whole pipeline and frontend can
run end-to-end offline. Dates are computed relative to "now" so fixtures are
always plausibly "today" / "tomorrow".
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

_NOW = datetime.now(timezone.utc)
_TODAY = _NOW.date()
_TOMORROW = _TODAY + timedelta(days=1)


def _iso(d: date, hh: int, mm: int, offset_hours: int = 0) -> str:
    tz = timezone(timedelta(hours=offset_hours))
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=tz).isoformat()


# Raw provider-shaped records (intentionally a little messy so the normalizer
# has real work to do). Keys: id, sport, league/league_id, country, season,
# venue, home/away (+ *_id), date, kickoff, status, scores.
_TOMORROW_RAW: list[dict[str, Any]] = [
    {
        "id": "rma-mci",
        "sport": "football",
        "league": "UEFA Champions League",
        "league_id": "ucl",
        "country": "Europe",
        "season": "2026",
        "venue": "Santiago Bernabéu",
        "home": "Real Madrid", "home_id": "real-madrid",
        "away": "Man City", "away_id": "man-city",
        "date": _TOMORROW.isoformat(), "kickoff": _iso(_TOMORROW, 21, 0, 2),
        "status": "scheduled",
        "win_prob": {"home": 0.56, "draw": 0.22, "away": 0.22},
        "interest_score": 98, "trend_badge": "Global #1", "audience": "1.2M",
    },
    {
        "id": "lal-bos",
        "sport": "basketball",
        "league": "NBA Finals", "league_id": "nba",
        "country": "USA", "season": "2026",
        "venue": "Crypto.com Arena",
        "home": "Lakers", "home_id": "lakers",
        "away": "Celtics", "away_id": "celtics",
        "date": _TOMORROW.isoformat(), "kickoff": _iso(_TOMORROW, 8, 30, 0),
        "status": "scheduled",
        "win_prob": {"home": 0.48, "draw": 0.20, "away": 0.32},
        "interest_score": 91, "trend_badge": "US Hot", "audience": "689K",
    },
    {
        "id": "sin-alc",
        "sport": "tennis",
        "league": "Wimbledon Men's SF", "league_id": "wimbledon",
        "country": "United Kingdom", "season": "2026",
        "venue": "Centre Court",
        "home": "Jannik Sinner", "home_id": "sinner",
        "away": "Carlos Alcaraz", "away_id": "alcaraz",
        "date": _TOMORROW.isoformat(), "kickoff": _iso(_TOMORROW, 15, 0, 1),
        "status": "scheduled",
        "win_prob": {"home": 0.44, "draw": 0.16, "away": 0.40},
        "interest_score": 88, "trend_badge": "Italy rising", "audience": "512K",
    },
    {
        "id": "ind-aus",
        "sport": "cricket",
        "league": "ICC Test Championship", "league_id": "icc-test",
        "country": "India", "season": "2026",
        "venue": "Eden Gardens",
        "home": "India", "home_id": "india",
        "away": "Australia", "away_id": "australia",
        "date": _TOMORROW.isoformat(), "kickoff": _iso(_TOMORROW, 10, 0, 5),
        "status": "scheduled",
        "win_prob": {"home": 0.41, "draw": 0.18, "away": 0.41},
        "interest_score": 86, "trend_badge": "Global #2", "audience": "842K",
    },
    {
        "id": "psg-bay",
        "sport": "football",
        "league": "UEFA Champions League", "league_id": "ucl",
        "country": "Europe", "season": "2026",
        "venue": "Parc des Princes",
        "home": "PSG", "home_id": "psg",
        "away": "Bayern Munich", "away_id": "bayern",
        "date": _TOMORROW.isoformat(), "kickoff": _iso(_TOMORROW, 21, 0, 2),
        "status": "scheduled",
        "win_prob": {"home": 0.39, "draw": 0.24, "away": 0.37},
        "interest_score": 83, "trend_badge": "EU Hot", "audience": "451K",
    },
]

_LIVE_RAW: list[dict[str, Any]] = [
    {
        "id": "ars-tot",
        "sport": "football",
        "league": "Premier League", "league_id": "epl",
        "country": "England", "season": "2026",
        "home": "Arsenal", "home_id": "arsenal",
        "away": "Tottenham", "away_id": "tottenham",
        "date": _TODAY.isoformat(), "kickoff": _iso(_TODAY, 16, 30, 1),
        "home_score": 2, "away_score": 1,
        "status": "live", "status_detail": "2H 78'",
    },
    {
        "id": "mia-den",
        "sport": "basketball",
        "league": "NBA", "league_id": "nba",
        "country": "USA", "season": "2026",
        "home": "Heat", "home_id": "heat",
        "away": "Nuggets", "away_id": "nuggets",
        "date": _TODAY.isoformat(), "kickoff": _iso(_TODAY, 1, 0, 0),
        "home_score": 89, "away_score": 94,
        "status": "live", "status_detail": "4Q 03:12",
    },
    {
        "id": "eng-rsa",
        "sport": "cricket",
        "league": "T20 World Cup", "league_id": "t20-wc",
        "country": "West Indies", "season": "2026",
        "home": "England", "home_id": "england",
        "away": "South Africa", "away_id": "south-africa",
        "date": _TODAY.isoformat(), "kickoff": _iso(_TODAY, 14, 0, 0),
        "home_score": "147/6", "away_score": None,
        "status": "live", "status_detail": "18.2 overs",
    },
    {
        "id": "zve-med",
        "sport": "tennis",
        "league": "ATP Halle", "league_id": "atp-halle",
        "country": "Germany", "season": "2026",
        "home": "A. Zverev", "home_id": "zverev",
        "away": "D. Medvedev", "away_id": "medvedev",
        "date": _TODAY.isoformat(), "kickoff": _iso(_TODAY, 12, 0, 1),
        "home_score": "6-4, 3-6, 6-2", "away_score": None,
        "status": "finished", "status_detail": "Finished",
    },
]


def tomorrow_raw(sport: str | None = None) -> list[dict[str, Any]]:
    rows = [dict(r) for r in _TOMORROW_RAW]
    return [r for r in rows if sport is None or r["sport"] == sport]


def today_raw(sport: str | None = None) -> list[dict[str, Any]]:
    # "Today" = the live + finished slate (kickoffs are today).
    rows = [dict(r) for r in _LIVE_RAW]
    return [r for r in rows if sport is None or r["sport"] == sport]


def live_raw(sport: str | None = None) -> list[dict[str, Any]]:
    rows = [dict(r) for r in _LIVE_RAW if r["status"] == "live"]
    return [r for r in rows if sport is None or r["sport"] == sport]


def finished_raw(sport: str | None = None) -> list[dict[str, Any]]:
    rows = [dict(r) for r in _LIVE_RAW if r["status"] == "finished"]
    return [r for r in rows if sport is None or r["sport"] == sport]


def historical_results(sport: str = "football", n_matches: int = 120) -> list[dict[str, Any]]:
    """Deterministic synthetic match history for feature/leakage tests.

    Generates a round-robin-ish schedule of finished matches over the past
    ``n_matches`` days. Results are pseudo-random but seeded so output is
    reproducible across runs (important for leakage checks and unit tests).
    """
    teams_by_sport = {
        "football": ["Real Madrid", "Man City", "PSG", "Bayern Munich", "Arsenal", "Tottenham"],
        "basketball": ["Lakers", "Celtics", "Heat", "Nuggets"],
        "tennis": ["Sinner", "Alcaraz", "Zverev", "Medvedev"],
        "cricket": ["India", "Australia", "England", "South Africa"],
    }
    teams = teams_by_sport.get(sport, teams_by_sport["football"])
    rows: list[dict[str, Any]] = []
    seed = sum(ord(c) for c in sport)
    for i in range(n_matches):
        home = teams[(i + seed) % len(teams)]
        away = teams[(i * 3 + seed + 1) % len(teams)]
        if home == away:
            away = teams[(i * 3 + seed + 2) % len(teams)]
        match_date = _TODAY - timedelta(days=n_matches - i)
        # Deterministic pseudo-random scores.
        hs = (i * 7 + seed) % 4
        as_ = (i * 5 + seed + 1) % 4
        rows.append({
            "id": f"hist-{sport}-{i}",
            "sport": sport,
            "league": teams_by_sport and "Synthetic League",
            "home": home, "home_id": home.lower().replace(" ", "-"),
            "away": away, "away_id": away.lower().replace(" ", "-"),
            "date": match_date.isoformat(),
            "kickoff": _iso(match_date, 18, 0, 0),
            "home_score": hs, "away_score": as_,
            "status": "finished",
        })
    return rows


# Dashboard headline stats (reference image).
DASHBOARD_STATS = {
    "top_matches": 24,
    "live_games": 128,
    "update_cycle_minutes": 30,
    "global_fans": "4.8M",
}

# "Explore Sports" live counts (reference image).
EXPLORE_SPORTS = [
    {"sport": "football", "label": "Football", "live": 1842},
    {"sport": "basketball", "label": "Basketball", "live": 320},
    {"sport": "tennis", "label": "Tennis", "live": 156},
    {"sport": "cricket", "label": "Cricket", "live": 98},
    {"sport": "baseball", "label": "Baseball", "live": 64},
    {"sport": "esports", "label": "Esports", "live": 212},
]
