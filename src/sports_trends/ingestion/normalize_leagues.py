"""Extract canonical league records from normalized matches."""

from __future__ import annotations

from typing import Any


def leagues_from_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a de-duplicated list of {league_id, name, sport, country, season}."""
    leagues: dict[str, dict[str, Any]] = {}
    for m in matches:
        lid = m.get("league_id")
        if not lid:
            continue
        leagues.setdefault(lid, {
            "league_id": lid,
            "name": m.get("league_name", "unknown"),
            "sport": m.get("sport", "unknown"),
            "country": m.get("country", ""),
            "season": m.get("season", ""),
        })
    return sorted(leagues.values(), key=lambda l: l["league_id"])
