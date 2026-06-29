"""OpenFootball worldcup.json provider — free, public-domain, no API key.

Source: https://github.com/openfootball/worldcup.json (years 1930..2026).
Parses the schedule/results into the project's raw record shape. Network
failures degrade gracefully (return []), so the orchestrator can fall back.

The 2026 file ships the full 104-match schedule (group stage + knockouts) with
real teams, venues and kick-off times expressed in *local* time with a UTC
offset (e.g. ``"17:00 UTC-4"``). We normalise those to absolute UTC so the
site can render correct kick-off labels and countdowns.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any

from ..features.tournament_stage import normalize_stage
from ..logging_config import get_logger
from .worldcup_reference import confederation_of, host_country_for_venue

logger = get_logger(__name__)

BASE = "https://raw.githubusercontent.com/openfootball/worldcup.json/master"

# Matches "13:00 UTC-6", "20:30 UTC-4", "9:05 UTC+1" etc.
_TIME_RE = re.compile(r"^\s*(\d{1,2}):(\d{2})(?:\s*UTC\s*([+-]\d{1,2}))?")


def _kickoff(d: str | None, t: str | None) -> str | None:
    """Return an absolute UTC ISO timestamp from an OpenFootball date/time.

    Handles the local-time + UTC-offset format used by the 2026 file as well
    as the older bare ``"HH:MM"`` form. Unknown/blank times fall back to 00:00.
    """
    if not d:
        return None
    try:
        y, mo, da = (int(x) for x in d.split("-"))
    except Exception:
        return None
    hh, mm, off = 0, 0, 0
    m = _TIME_RE.match(t or "")
    if m:
        hh, mm = int(m.group(1)), int(m.group(2))
        off = int(m.group(3)) if m.group(3) else 0
    try:
        # local = UTC + offset  ->  UTC = local - offset
        local = datetime(y, mo, da, hh, mm, tzinfo=timezone.utc)
        return (local - timedelta(hours=off)).isoformat()
    except Exception:
        return None


def _scorers(goals: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    out = []
    for g in goals or []:
        name = g.get("name")
        if name:
            out.append({"name": name, "minute": str(g.get("minute", "")),
                        "penalty": bool(g.get("penalty"))})
    return out


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
        # Skip knockout placeholders ("Winner Group A", "1A", "Runner-up …").
        if _is_placeholder(t1) or _is_placeholder(t2):
            placeholder = True
        else:
            placeholder = False
        ft = (m.get("score") or {}).get("ft")
        finished = isinstance(ft, list) and len(ft) == 2
        raw_round = m.get("round") or m.get("group") or ""
        stage = normalize_stage(raw_round)
        venue = m.get("ground", "")
        host_country = host_country_for_venue(venue)
        out.append({
            "id": f"wc-{year}-" + "-".join(
                str(x).lower().replace(" ", "") for x in (t1, t2, m.get("date", ""))),
            "sport": "football", "league": data.get("name", f"World Cup {year}"),
            "league_id": "fifa-world-cup", "season": str(year),
            "home": t1, "home_id": str(t1).lower().replace(" ", "-"),
            "away": t2, "away_id": str(t2).lower().replace(" ", "-"),
            "date": m.get("date"), "kickoff": _kickoff(m.get("date"), m.get("time")),
            "kickoff_local": m.get("time", ""),
            "home_score": ft[0] if finished else None,
            "away_score": ft[1] if finished else None,
            "status": "finished" if finished else "scheduled",
            "status_detail": raw_round,
            "matchday": str(m.get("round", "")) if str(m.get("round", "")).startswith("Matchday") else "",
            "competition_type": "world_cup", "confederation": "INTERNATIONAL",
            "home_confederation": confederation_of(t1),
            "away_confederation": confederation_of(t2),
            "stage": stage, "group": m.get("group", ""),
            "is_country_match": True,
            "neutral_venue": host_country not in (t1, t2),
            "host_advantage": (t1 in {"USA", "Canada", "Mexico"})
            or (t2 in {"USA", "Canada", "Mexico"}),
            "venue": venue, "host_city": venue.split(" (")[0] if venue else "",
            "home_scorers": _scorers(m.get("goals1")) if finished else [],
            "away_scorers": _scorers(m.get("goals2")) if finished else [],
            "is_placeholder": placeholder,
        })
    return out


def _is_placeholder(name: str) -> bool:
    """True for OpenFootball knockout stand-ins (not yet a real qualified team).

    Examples: "Winner Group A", "Runner-up B", "W74"/"L101"/"RU2" (winner /
    loser / runner-up of match N), "1A"/"2B"/"3C" (group-position seeds).
    """
    n = str(name).strip()
    if not n:
        return True
    low = n.lower()
    if low.startswith(("winner", "runner", "loser", "third", "1st", "2nd", "3rd")):
        return True
    if re.match(r"^(w|l|ru)\d+$", low):     # W74, L101, RU2
        return True
    if re.match(r"^[123][a-z]$", low):       # 1A, 2B, 3C
        return True
    return False
