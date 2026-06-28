"""Days of rest since a team's previous match."""

from __future__ import annotations

from datetime import date
from typing import Any


def _parse(day: str):
    try:
        return date.fromisoformat(day[:10])
    except (TypeError, ValueError):
        return None


def rest_days(history: list[dict[str, Any]], team: str, as_of: str, cap: int = 14) -> int:
    target = _parse(as_of)
    if target is None:
        return cap
    last = None
    for m in history:
        if (m.get("home_team") or m.get("home")) != team and (m.get("away_team") or m.get("away")) != team:
            continue
        d = _parse(str(m.get("date") or m.get("match_date") or ""))
        if d is None or d >= target:
            continue
        if last is None or d > last:
            last = d
    if last is None:
        return cap
    return min((target - last).days, cap)
