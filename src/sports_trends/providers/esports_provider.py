"""Esports data provider (live API when keyed, mock data otherwise)."""

from __future__ import annotations

from .base import BaseSportsProvider


class EsportsProvider(BaseSportsProvider):
    sport = "esports"
