"""Tennis data provider (live API when keyed, mock data otherwise)."""

from __future__ import annotations

from .base import BaseSportsProvider


class TennisProvider(BaseSportsProvider):
    sport = "tennis"
