from abc import ABC, abstractmethod
from typing import Any


class SportsProvider(ABC):
    """Provider interface. Implement one subclass per data vendor."""

    name: str = "base"

    @abstractmethod
    def fetch_today(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def fetch_tomorrow(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def fetch_live(self) -> list[dict[str, Any]]:
        raise NotImplementedError
