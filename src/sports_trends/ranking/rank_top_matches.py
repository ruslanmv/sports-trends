"""Ranking helpers for tomorrow's top matches."""

from __future__ import annotations

from typing import Any


def rank_top_matches(matches: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    """Rank matches by interest score, confidence, then kickoff order."""
    return sorted(
        matches or [],
        key=lambda row: (row.get("interest_score", 0), row.get("confidence", 0), row.get("kickoff", "")),
        reverse=True,
    )
