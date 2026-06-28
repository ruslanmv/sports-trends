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


# Extra fixtures so every sport page and the all-sports table feel full.
_EXTRA_TOMORROW: list[dict[str, Any]] = [
    {"id": "liv-che", "sport": "football", "league": "Premier League", "league_id": "epl",
     "country": "England", "season": "2026", "home": "Liverpool", "home_id": "liverpool",
     "away": "Chelsea", "away_id": "chelsea", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 18, 30, 1), "status": "scheduled",
     "win_prob": {"home": 0.48, "draw": 0.25, "away": 0.27}, "interest_score": 80, "audience": "612K"},
    {"id": "bar-atm", "sport": "football", "league": "La Liga", "league_id": "laliga",
     "country": "Spain", "season": "2026", "home": "Barcelona", "home_id": "barcelona",
     "away": "Atletico Madrid", "away_id": "atletico", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 20, 0, 2), "status": "scheduled",
     "win_prob": {"home": 0.51, "draw": 0.25, "away": 0.24}, "interest_score": 78, "audience": "498K"},
    {"id": "gsw-phx", "sport": "basketball", "league": "NBA", "league_id": "nba",
     "country": "USA", "season": "2026", "home": "Warriors", "home_id": "warriors",
     "away": "Suns", "away_id": "suns", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 3, 0, 0), "status": "scheduled",
     "win_prob": {"home": 0.55, "draw": 0.0, "away": 0.45}, "interest_score": 74, "audience": "388K"},
    {"id": "mil-phi", "sport": "basketball", "league": "NBA", "league_id": "nba",
     "country": "USA", "season": "2026", "home": "Bucks", "home_id": "bucks",
     "away": "76ers", "away_id": "sixers", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 1, 30, 0), "status": "scheduled",
     "win_prob": {"home": 0.58, "draw": 0.0, "away": 0.42}, "interest_score": 70, "audience": "301K"},
    {"id": "djo-zve", "sport": "tennis", "league": "Wimbledon Men's QF", "league_id": "wimbledon",
     "country": "United Kingdom", "season": "2026", "home": "Novak Djokovic", "home_id": "djokovic",
     "away": "A. Zverev", "away_id": "zverev", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 13, 30, 1), "status": "scheduled",
     "win_prob": {"home": 0.62, "draw": 0.0, "away": 0.38}, "interest_score": 79, "audience": "455K"},
    {"id": "swi-sab", "sport": "tennis", "league": "Wimbledon Women's SF", "league_id": "wimbledon",
     "country": "United Kingdom", "season": "2026", "home": "Iga Swiatek", "home_id": "swiatek",
     "away": "Aryna Sabalenka", "away_id": "sabalenka", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 16, 0, 1), "status": "scheduled",
     "win_prob": {"home": 0.53, "draw": 0.0, "away": 0.47}, "interest_score": 72, "audience": "362K"},
    {"id": "pak-nzl", "sport": "cricket", "league": "ICC Test Championship", "league_id": "icc-test",
     "country": "Pakistan", "season": "2026", "home": "Pakistan", "home_id": "pakistan",
     "away": "New Zealand", "away_id": "new-zealand", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 6, 0, 5), "status": "scheduled",
     "win_prob": {"home": 0.45, "draw": 0.22, "away": 0.33}, "interest_score": 66, "audience": "224K"},
    {"id": "nyy-lad", "sport": "baseball", "league": "MLB", "league_id": "mlb",
     "country": "USA", "season": "2026", "home": "Yankees", "home_id": "yankees",
     "away": "Dodgers", "away_id": "dodgers", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 0, 5, 0), "status": "scheduled",
     "win_prob": {"home": 0.52, "draw": 0.0, "away": 0.48}, "interest_score": 68, "audience": "276K"},
    {"id": "nym-atl", "sport": "baseball", "league": "MLB", "league_id": "mlb",
     "country": "USA", "season": "2026", "home": "Mets", "home_id": "mets",
     "away": "Braves", "away_id": "braves", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 23, 10, 0), "status": "scheduled",
     "win_prob": {"home": 0.49, "draw": 0.0, "away": 0.51}, "interest_score": 60, "audience": "188K"},
    {"id": "t1-g2", "sport": "esports", "league": "LoL Worlds", "league_id": "lol-worlds",
     "country": "Global", "season": "2026", "home": "T1", "home_id": "t1",
     "away": "G2 Esports", "away_id": "g2", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 12, 0, 0), "status": "scheduled",
     "win_prob": {"home": 0.60, "draw": 0.0, "away": 0.40}, "interest_score": 75, "audience": "410K"},
    {"id": "faze-navi", "sport": "esports", "league": "CS2 Major", "league_id": "cs2-major",
     "country": "Global", "season": "2026", "home": "FaZe", "home_id": "faze",
     "away": "NAVI", "away_id": "navi", "date": _TOMORROW.isoformat(),
     "kickoff": _iso(_TOMORROW, 17, 0, 1), "status": "scheduled",
     "win_prob": {"home": 0.47, "draw": 0.0, "away": 0.53}, "interest_score": 64, "audience": "243K"},
]

_EXTRA_LIVE: list[dict[str, Any]] = [
    {"id": "lad-sfg", "sport": "baseball", "league": "MLB", "league_id": "mlb",
     "country": "USA", "season": "2026", "home": "Dodgers", "home_id": "dodgers",
     "away": "Giants", "away_id": "giants", "date": _TODAY.isoformat(),
     "kickoff": _iso(_TODAY, 2, 10, 0), "home_score": 4, "away_score": 3,
     "status": "live", "status_detail": "Top 8th"},
    {"id": "geng-t1", "sport": "esports", "league": "LoL Worlds", "league_id": "lol-worlds",
     "country": "Global", "season": "2026", "home": "Gen.G", "home_id": "geng",
     "away": "T1", "away_id": "t1", "date": _TODAY.isoformat(),
     "kickoff": _iso(_TODAY, 11, 0, 0), "home_score": 1, "away_score": 2,
     "status": "live", "status_detail": "Game 4"},
]


def tomorrow_raw(sport: str | None = None) -> list[dict[str, Any]]:
    rows = [dict(r) for r in (_TOMORROW_RAW + _EXTRA_TOMORROW)]
    return [r for r in rows if sport is None or r["sport"] == sport]


def today_raw(sport: str | None = None) -> list[dict[str, Any]]:
    # "Today" = the live + finished slate (kickoffs are today).
    rows = [dict(r) for r in (_LIVE_RAW + _EXTRA_LIVE)]
    return [r for r in rows if sport is None or r["sport"] == sport]


def live_raw(sport: str | None = None) -> list[dict[str, Any]]:
    rows = [dict(r) for r in (_LIVE_RAW + _EXTRA_LIVE) if r["status"] == "live"]
    return [r for r in rows if sport is None or r["sport"] == sport]


def finished_raw(sport: str | None = None) -> list[dict[str, Any]]:
    rows = [dict(r) for r in (_LIVE_RAW + _EXTRA_LIVE) if r["status"] == "finished"]
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
