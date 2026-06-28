"""OpenFootball worldcup.json provider — free, public-domain, no API key.

Source: https://github.com/openfootball/worldcup.json (years 1930..2026).
Parses the schedule/results into the project's raw record shape. Network
failures degrade gracefully (return []), so the orchestrator can fall back.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..features.tournament_stage import normalize_stage
from ..logging_config import get_logger

logger = get_logger(__name__)

BASE = "https://raw.githubusercontent.com/openfootball/worldcup.json/master"


def _kickoff(d: str, t: str | None) -> str | None:
    if not d:
        return None
    try:
        hh, mm = (t or "00:00").split(":")[:2]
        return datetime(*map(int, d.split("-")), int(hh), int(mm), tzinfo=timezone.utc).isoformat()
    except Exception:
        return None


def fetch_worldcup_year(year: int = 2026, timeout: int = 20) -> list[dict[str, Any]]:
    """Return raw World Cup records for ``year`` from OpenFootball, or []."""
    try:
        import requests
        resp = requests.get(f"{BASE}/{year}/worldcup.json", timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:  # offline / rate-limited / not published yet
        logger.warning("OpenFootball fetch failed for %s: %s", year, exc)
        return []

    out: list[dict[str, Any]] = []
    for m in data.get("matches", []):
        t1, t2 = m.get("team1"), m.get("team2")
        if not t1 or not t2:
            continue
        ft = (m.get("score") or {}).get("ft")
        finished = isinstance(ft, list) and len(ft) == 2
        stage = normalize_stage(m.get("round") or m.get("group"))
        out.append({
            "id": f"wc-{year}-" + "-".join(str(x).lower().replace(' ', '') for x in (t1, t2, m.get('date', ''))),
            "sport": "football", "league": data.get("name", f"World Cup {year}"),
            "league_id": "fifa-world-cup", "season": str(year),
            "home": t1, "home_id": t1.lower().replace(" ", "-"),
            "away": t2, "away_id": t2.lower().replace(" ", "-"),
            "date": m.get("date"), "kickoff": _kickoff(m.get("date"), m.get("time")),
            "home_score": ft[0] if finished else None,
            "away_score": ft[1] if finished else None,
            "status": "finished" if finished else "scheduled",
            "status_detail": m.get("round", ""),
            "competition_type": "world_cup", "confederation": "INTERNATIONAL",
            "stage": stage, "group": m.get("group", ""),
            "is_country_match": True, "neutral_venue": True,
            "host_advantage": False, "venue": m.get("ground", ""),
        })
    return out
