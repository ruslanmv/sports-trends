"""TheSportsDB free multi-sport provider (no real key — uses the public test key).

Year-round "next events" across sports/leagues, used to keep the portal fresh in
any season. Free and keyless; network failures degrade to []. Docs:
https://www.thesportsdb.com/free_sports_api
"""

from __future__ import annotations

import os
from typing import Any

from ..logging_config import get_logger

logger = get_logger(__name__)

# Public free test key (rate-limited). Override with THESPORTSDB_KEY if you have one.
KEY = os.getenv("THESPORTSDB_KEY", "3")
BASE = f"https://www.thesportsdb.com/api/v1/json/{KEY}"

# A few notable league ids (TheSportsDB), expandable.
LEAGUES = {
    "epl": 4328, "laliga": 4335, "seriea": 4332, "bundesliga": 4331, "ligue1": 4334,
    "ucl": 4480, "nba": 4387, "mlb": 4424,
}


def _sport_of(strsport: str | None) -> str:
    m = {"Soccer": "football", "Basketball": "basketball", "Tennis": "tennis",
         "Cricket": "cricket", "Baseball": "baseball", "ESports": "esports"}
    return m.get(strsport or "", "football")


def fetch_next_events(league_id: int, timeout: int = 15) -> list[dict[str, Any]]:
    try:
        import requests
        r = requests.get(f"{BASE}/eventsnextleague.php?id={league_id}", timeout=timeout)
        r.raise_for_status()
        events = r.json().get("events") or []
    except Exception as exc:
        logger.warning("TheSportsDB fetch failed for league %s: %s", league_id, exc)
        return []
    out = []
    for e in events:
        home, away = e.get("strHomeTeam"), e.get("strAwayTeam")
        if not home or not away:
            continue
        date_s = e.get("dateEvent")
        out.append({
            "id": "tsdb-" + str(e.get("idEvent")),
            "sport": _sport_of(e.get("strSport")),
            "league": e.get("strLeague", ""), "league_id": str(e.get("idLeague", "")),
            "season": e.get("strSeason", ""), "country": e.get("strCountry", ""),
            "home": home, "home_id": (home or "").lower().replace(" ", "-"),
            "away": away, "away_id": (away or "").lower().replace(" ", "-"),
            "date": date_s,
            "kickoff": (date_s + "T" + (e.get("strTime") or "00:00:00")) if date_s else None,
            "home_score": None, "away_score": None, "status": "scheduled",
            "venue": e.get("strVenue", ""), "provider": "thesportsdb",
        })
    return out


def fetch_past_events(league_id: int, timeout: int = 15) -> list[dict[str, Any]]:
    """Recent FINISHED events for a league (keyless), with scores."""
    try:
        import requests
        r = requests.get(f"{BASE}/eventspastleague.php?id={league_id}", timeout=timeout)
        r.raise_for_status()
        events = r.json().get("events") or []
    except Exception as exc:
        logger.warning("TheSportsDB past fetch failed for league %s: %s", league_id, exc)
        return []
    out = []
    for e in events:
        home, away = e.get("strHomeTeam"), e.get("strAwayTeam")
        if not home or not away:
            continue
        hs, as_ = e.get("intHomeScore"), e.get("intAwayScore")
        date_s = e.get("dateEvent")
        out.append({
            "id": "tsdb-" + str(e.get("idEvent")),
            "sport": _sport_of(e.get("strSport")),
            "league": e.get("strLeague", ""), "league_id": str(e.get("idLeague", "")),
            "season": e.get("strSeason", ""), "country": e.get("strCountry", ""),
            "home": home, "home_id": (home or "").lower().replace(" ", "-"),
            "away": away, "away_id": (away or "").lower().replace(" ", "-"),
            "date": date_s,
            "kickoff": (date_s + "T" + (e.get("strTime") or "00:00:00")) if date_s else None,
            "home_score": int(hs) if hs not in (None, "") else None,
            "away_score": int(as_) if as_ not in (None, "") else None,
            "status": "finished" if hs not in (None, "") else "scheduled",
            "venue": e.get("strVenue", ""), "provider": "thesportsdb",
        })
    return out


def fetch_for_keys(keys: list[str] | None = None) -> list[dict[str, Any]]:
    """Upcoming (scheduled) events across the configured leagues."""
    rows: list[dict[str, Any]] = []
    for k in (keys or list(LEAGUES)):
        lid = LEAGUES.get(k)
        if lid:
            rows.extend(fetch_next_events(lid))
    return rows


def fetch_results_for_keys(keys: list[str] | None = None) -> list[dict[str, Any]]:
    """Recent finished results across the configured leagues."""
    rows: list[dict[str, Any]] = []
    for k in (keys or list(LEAGUES)):
        lid = LEAGUES.get(k)
        if lid:
            rows.extend(r for r in fetch_past_events(lid) if r.get("status") == "finished")
    return rows
