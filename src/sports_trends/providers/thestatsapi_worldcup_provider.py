"""TheStatsAPI World Cup 2026 fixtures — free, no API key, attribution only.

Source: https://www.thestatsapi.com/world-cup/data/fixtures.json
License: free to use with attribution to TheStatsAPI.

Provides all 104 fixtures with **clean absolute-UTC kick-off times**, official
stadium names and host cities. We use it as an additive source to (a) backfill
accurate kick-off timestamps onto the OpenFootball schedule and (b) act as an
independent fixtures fallback. Network failures degrade gracefully (return []).
"""

from __future__ import annotations

from typing import Any

from ..features.tournament_stage import normalize_stage
from ..logging_config import get_logger
from .worldcup_reference import confederation_of

logger = get_logger(__name__)

URL = "https://www.thestatsapi.com/world-cup/data/fixtures.json"
ATTRIBUTION = "Fixtures: TheStatsAPI (thestatsapi.com)"


def _key(home: str, away: str, date: str) -> str:
    return "|".join((str(home).lower().strip(), str(away).lower().strip(), str(date)))


def fetch_fixtures(timeout: int = 20) -> list[dict[str, Any]]:
    """Return normalised fixture records, or [] on failure."""
    try:
        import requests
        r = requests.get(URL, timeout=timeout)
        r.raise_for_status()
        data = r.json()
    except Exception as exc:
        logger.warning("TheStatsAPI fixtures fetch failed: %s", exc)
        return []

    out: list[dict[str, Any]] = []
    for f in data.get("fixtures", []):
        home, away = f.get("homeTeam"), f.get("awayTeam")
        if not home or not away:
            continue
        date = f.get("date", "")
        stage = normalize_stage(f.get("stage") or f.get("group") or "")
        out.append({
            "id": f"tsa-wc-{f.get('matchNumber', '')}",
            "sport": "football", "league": "FIFA World Cup 2026",
            "league_id": "fifa-world-cup", "season": "2026",
            "home": home, "home_id": str(home).lower().replace(" ", "-"),
            "away": away, "away_id": str(away).lower().replace(" ", "-"),
            "date": date, "kickoff": f.get("kickoffUtc"),
            "home_score": None, "away_score": None, "status": "scheduled",
            "status_detail": f.get("stage", ""),
            "competition_type": "world_cup", "confederation": "INTERNATIONAL",
            "home_confederation": confederation_of(home),
            "away_confederation": confederation_of(away),
            "stage": stage, "group": (f.get("group") or "").strip(),
            "is_country_match": True, "neutral_venue": True,
            "venue": f.get("stadium", ""),
            "host_city": (f.get("hostCity") or "").replace("-", " ").title(),
            "match_url": f.get("matchUrl", ""),
            "provider": "thestatsapi",
        })
    return out


def kickoff_index(timeout: int = 20) -> dict[str, str]:
    """Map ``home|away|date`` -> clean UTC kickoff, for enriching other sources."""
    idx: dict[str, str] = {}
    for f in fetch_fixtures(timeout=timeout):
        if f.get("kickoff"):
            idx[_key(f["home"], f["away"], f["date"])] = f["kickoff"]
    return idx


def fixture_key(home: str, away: str, date: str) -> str:
    return _key(home, away, date)
