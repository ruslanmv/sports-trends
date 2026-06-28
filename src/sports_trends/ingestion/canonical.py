"""Pydantic model for the canonical match schema (validation layer).

Used by normalization tests and the dataset validator to guarantee every match
written to the data lake or to the frontend JSON shares one shape.
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class CanonicalMatch(BaseModel):
    match_id: str
    sport: str
    league_id: str
    league_name: str
    season: str = ""
    country: str = ""
    match_date: str = ""
    kickoff: Optional[str] = None
    venue: str = ""
    home_team_id: str
    home_team: str
    away_team_id: str
    away_team: str
    home_score: Optional[Any] = None
    away_score: Optional[Any] = None
    status: str = "scheduled"
    is_live: bool = False
    is_finished: bool = False
    provider: str = "fallback"
    last_updated: Optional[str] = None


def validate_match(record: dict[str, Any]) -> CanonicalMatch:
    """Validate one record, raising ``pydantic.ValidationError`` on failure."""
    return CanonicalMatch(**record)


def validate_matches(records: list[dict[str, Any]]) -> list[CanonicalMatch]:
    return [validate_match(r) for r in records]
