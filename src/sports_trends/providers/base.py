"""Provider interfaces for sports data sources.

Every concrete provider subclasses :class:`BaseSportsProvider`. When a real API
key is configured the subclass can call its live API; otherwise it transparently
falls back to deterministic mock data so the whole system runs offline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..config import api_key_for
from . import _mock_data


@dataclass(slots=True)
class ProviderResult:
    sport: str
    records: list[dict[str, Any]]
    source: str = "fallback"


class BaseSportsProvider:
    """Base class implementing the common provider contract.

    Subclasses set :attr:`sport` and may override the ``_live_*`` hooks to call a
    real API. The public ``fetch_*`` methods automatically use mock data when no
    API key is available, guaranteeing ``list[dict]`` output in every environment.
    """

    sport: str = "generic"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key if api_key is not None else api_key_for(self.sport)

    # -- mode --------------------------------------------------------------
    @property
    def uses_live_api(self) -> bool:
        return bool(self.api_key)

    @property
    def mode(self) -> str:
        return "live" if self.uses_live_api else "fallback"

    # -- live API hooks (override in subclasses that have a real integration) --
    def _live_today_matches(self) -> list[dict[str, Any]] | None:
        return None

    def _live_tomorrow_matches(self) -> list[dict[str, Any]] | None:
        return None

    def _live_results(self) -> list[dict[str, Any]] | None:
        return None

    def _live_finished_results(self) -> list[dict[str, Any]] | None:
        return None

    # -- public contract ---------------------------------------------------
    def fetch_today_matches(self) -> list[dict[str, Any]]:
        if self.uses_live_api:
            live = self._live_today_matches()
            if live is not None:
                return live
        return _mock_data.today_raw(self.sport)

    def fetch_tomorrow_matches(self) -> list[dict[str, Any]]:
        if self.uses_live_api:
            live = self._live_tomorrow_matches()
            if live is not None:
                return live
        return _mock_data.tomorrow_raw(self.sport)

    def fetch_live_results(self) -> list[dict[str, Any]]:
        if self.uses_live_api:
            live = self._live_results()
            if live is not None:
                return live
        return _mock_data.live_raw(self.sport)

    def fetch_finished_results(self) -> list[dict[str, Any]]:
        if self.uses_live_api:
            live = self._live_finished_results()
            if live is not None:
                return live
        return _mock_data.finished_raw(self.sport)

    # -- back-compat aliases ----------------------------------------------
    def fetch_today(self) -> list[dict[str, Any]]:
        return self.fetch_today_matches()

    def fetch_tomorrow(self) -> list[dict[str, Any]]:
        return self.fetch_tomorrow_matches()

    def fetch_live(self) -> list[dict[str, Any]]:
        return self.fetch_live_results()

    # -- diagnostics -------------------------------------------------------
    def health(self) -> dict[str, Any]:
        return {
            "provider": type(self).__name__,
            "sport": self.sport,
            "has_api_key": self.uses_live_api,
            "mode": self.mode,
        }
