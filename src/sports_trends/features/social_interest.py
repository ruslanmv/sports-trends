"""Social interest score placeholder (deterministic until a real signal lands)."""

from __future__ import annotations

from typing import Any

from .league_strength import league_importance_score


def social_interest_score(match: dict[str, Any]) -> int:
    """Blend league importance with an explicit interest hint if present."""
    base = league_importance_score(match.get("league_name") or match.get("league") or "")
    hint = match.get("interest_score")
    if isinstance(hint, (int, float)):
        return int(round(0.5 * base + 0.5 * float(hint)))
    return base
