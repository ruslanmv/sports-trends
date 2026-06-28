"""Extract canonical team records from normalized matches."""

from __future__ import annotations

from typing import Any


def teams_from_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a de-duplicated list of {team_id, name, sport, country}."""
    teams: dict[str, dict[str, Any]] = {}
    for m in matches:
        for side in ("home", "away"):
            tid = m.get(f"{side}_team_id")
            name = m.get(f"{side}_team")
            if not tid or not name:
                continue
            teams.setdefault(tid, {
                "team_id": tid,
                "name": name,
                "sport": m.get("sport", "unknown"),
                "country": m.get("country", ""),
            })
    return sorted(teams.values(), key=lambda t: t["team_id"])
