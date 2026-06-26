"""Provider interfaces for sports data sources."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

@dataclass(slots=True)
class ProviderResult:
    sport: str
    records: list[dict[str, Any]]
    source: str = "placeholder"

class SportsProvider(Protocol):
    def fetch_today(self) -> list[dict[str, Any]]: ...
    def fetch_tomorrow(self) -> list[dict[str, Any]]: ...
    def fetch_live(self) -> list[dict[str, Any]]: ...
