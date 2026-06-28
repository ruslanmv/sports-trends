"""Sports data providers.

Exposes the per-sport providers, the fallback aggregator, a registry keyed by
sport, and a :func:`provider_health_report` for diagnostics.
"""

from __future__ import annotations

from typing import Any

from .base import BaseSportsProvider, ProviderResult
from .football_provider import FootballProvider
from .basketball_provider import BasketballProvider
from .tennis_provider import TennisProvider
from .cricket_provider import CricketProvider
from .baseball_provider import BaseballProvider
from .esports_provider import EsportsProvider
from .fallback_provider import FallbackProvider

PROVIDER_REGISTRY: dict[str, type[BaseSportsProvider]] = {
    "football": FootballProvider,
    "basketball": BasketballProvider,
    "tennis": TennisProvider,
    "cricket": CricketProvider,
    "baseball": BaseballProvider,
    "esports": EsportsProvider,
}


def get_provider(sport: str) -> BaseSportsProvider:
    """Return a provider instance for ``sport`` (falls back to mock aggregator)."""
    cls = PROVIDER_REGISTRY.get(sport)
    return cls() if cls else FallbackProvider()


def provider_health_report() -> list[dict[str, Any]]:
    """Return a health row per provider (mode = ``live`` or ``fallback``)."""
    return [cls().health() for cls in PROVIDER_REGISTRY.values()]


__all__ = [
    "BaseSportsProvider",
    "ProviderResult",
    "FootballProvider",
    "BasketballProvider",
    "TennisProvider",
    "CricketProvider",
    "BaseballProvider",
    "EsportsProvider",
    "FallbackProvider",
    "PROVIDER_REGISTRY",
    "get_provider",
    "provider_health_report",
]
