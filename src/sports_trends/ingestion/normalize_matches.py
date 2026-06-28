"""Normalize provider match payloads into the canonical sports-trends schema.

Canonical fields (Batch 3):
    match_id, sport, league_id, league_name, season, country, match_date,
    kickoff, venue, home_team_id, home_team, away_team_id, away_team,
    home_score, away_score, status, is_live, is_finished, provider, last_updated
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

_SLUG_RE = re.compile(r"[^a-z0-9]+")

CANONICAL_FIELDS = (
    "match_id", "sport", "league_id", "league_name", "season", "country",
    "match_date", "kickoff", "venue", "home_team_id", "home_team",
    "away_team_id", "away_team", "home_score", "away_score", "status",
    "is_live", "is_finished", "provider", "last_updated",
)


def slugify(value: Any) -> str:
    return _SLUG_RE.sub("-", str(value or "").strip().lower()).strip("-")


def make_match_id(sport: str, league: str, home: str, away: str, match_date: str) -> str:
    """Deterministic, human-readable match id stable across providers/runs."""
    parts = [slugify(sport), slugify(league), slugify(home), slugify(away), str(match_date or "")]
    return "-".join(p for p in parts if p)


def _first(raw: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if raw.get(key) not in (None, ""):
            return raw[key]
    return None


def normalize_match(raw: dict[str, Any], provider: str) -> dict[str, Any]:
    """Map a single provider record onto the canonical schema."""
    sport = raw.get("sport", "unknown")
    league_name = _first(raw, "league_name", "league") or "unknown"
    home = _first(raw, "home_team", "home") or ""
    away = _first(raw, "away_team", "away") or ""
    match_date = _first(raw, "match_date", "date") or ""
    status = (raw.get("status") or "scheduled").lower()

    match_id = str(_first(raw, "match_id", "id") or "") or make_match_id(
        sport, league_name, home, away, match_date
    )

    return {
        "match_id": match_id,
        "sport": sport,
        "league_id": str(_first(raw, "league_id") or slugify(league_name)),
        "league_name": league_name,
        "season": str(_first(raw, "season") or ""),
        "country": _first(raw, "country") or "",
        "match_date": match_date,
        "kickoff": raw.get("kickoff"),
        "venue": raw.get("venue") or "",
        "home_team_id": str(_first(raw, "home_team_id", "home_id") or slugify(home)),
        "home_team": home,
        "away_team_id": str(_first(raw, "away_team_id", "away_id") or slugify(away)),
        "away_team": away,
        "home_score": raw.get("home_score"),
        "away_score": raw.get("away_score"),
        "status": status,
        "is_live": status == "live",
        "is_finished": status in ("finished", "ft", "completed"),
        "provider": provider,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


def normalize_matches(
    rows: list[dict[str, Any]] | None = None, provider: str = "fallback"
) -> list[dict[str, Any]]:
    """Normalize and de-duplicate a list of provider match records."""
    normalized = [normalize_match(row, provider) for row in (rows or [])]
    return deduplicate_matches(normalized)


def deduplicate_matches(matches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop duplicate ``match_id`` values, keeping the first occurrence."""
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for match in matches:
        mid = match.get("match_id")
        if mid in seen:
            continue
        seen.add(mid)
        unique.append(match)
    return unique


def find_duplicate_ids(matches: list[dict[str, Any]]) -> list[str]:
    """Return match_ids that appear more than once (for the quality report)."""
    counts: dict[str, int] = {}
    for match in matches:
        mid = str(match.get("match_id"))
        counts[mid] = counts.get(mid, 0) + 1
    return sorted(mid for mid, c in counts.items() if c > 1)
