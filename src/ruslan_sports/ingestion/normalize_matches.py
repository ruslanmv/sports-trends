from typing import Any


def normalize_match(raw: dict[str, Any], provider: str) -> dict[str, Any]:
    """Normalize a provider-specific match into the canonical schema."""
    return {
        "provider": provider,
        "provider_id": raw.get("id") or raw.get("provider_id"),
        "sport": raw.get("sport", "unknown"),
        "league": raw.get("league", "unknown"),
        "home_team": raw.get("home_team") or raw.get("home"),
        "away_team": raw.get("away_team") or raw.get("away"),
        "kickoff": raw.get("kickoff") or raw.get("start_time"),
        "status": raw.get("status", "scheduled"),
    }
