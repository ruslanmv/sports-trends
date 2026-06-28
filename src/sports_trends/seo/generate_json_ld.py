"""Schema.org SportsEvent JSON-LD for match pages (rich results)."""

from __future__ import annotations

import json
from typing import Any

from ..config import SITE_BASE_URL


def sport_event_jsonld(match: dict[str, Any]) -> dict[str, Any]:
    home, away = match.get("home_team", ""), match.get("away_team", "")
    slug = match.get("match_id", "")
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "SportsEvent",
        "name": f"{home} vs {away}",
        "sport": match.get("sport", ""),
        "url": f"{SITE_BASE_URL.rstrip('/')}/match/{slug}/",
        "startDate": match.get("kickoff"),
        "eventStatus": "https://schema.org/EventScheduled",
        "competitor": [
            {"@type": "SportsTeam", "name": home},
            {"@type": "SportsTeam", "name": away},
        ],
        "organizer": {"@type": "Organization", "name": match.get("league", "")},
    }
    return {k: v for k, v in data.items() if v not in (None, "")}


def generate_json_ld(matches: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return [sport_event_jsonld(m) for m in (matches or [])]


def jsonld_script(match: dict[str, Any]) -> str:
    return '<script type="application/ld+json">\n' + json.dumps(sport_event_jsonld(match), indent=2) + "\n</script>"
