"""Normalize provider match payloads into the sports-trends match schema."""

from __future__ import annotations

from typing import Any


def normalize_match(raw: dict[str, Any], provider: str) -> dict[str, Any]:
    """Normalize the minimal common match fields used by tests and fixtures."""
    return {
        "match_id": str(raw.get("match_id") or raw.get("id") or ""),
        "provider": provider,
        "sport": raw.get("sport", "unknown"),
        "league": raw.get("league", "unknown"),
        "home_team": raw.get("home_team") or raw.get("home") or "",
        "away_team": raw.get("away_team") or raw.get("away") or "",
        "kickoff": raw.get("kickoff"),
        "status": raw.get("status", "scheduled"),
    }


def normalize_matches(rows: list[dict[str, Any]] | None = None, provider: str = "placeholder") -> list[dict[str, Any]]:
    """Normalize a list of provider match records."""
    return [normalize_match(row, provider) for row in (rows or [])]
