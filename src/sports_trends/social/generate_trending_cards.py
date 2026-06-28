"""Build trending-card payloads (data for OG image / social cards)."""

from __future__ import annotations

from typing import Any


def generate_trending_cards(matches: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    cards = []
    for m in (matches or []):
        cards.append({
            "match_id": m.get("match_id", ""),
            "title": f"{m.get('home_team','')} vs {m.get('away_team','')}",
            "subtitle": m.get("league", ""),
            "badge": m.get("trend_badge"),
            "audience": m.get("audience"),
            "interest_score": m.get("interest_score"),
        })
    return cards
