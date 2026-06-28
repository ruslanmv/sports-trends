"""Home-advantage feature (constant prior; refined per-league later)."""

from __future__ import annotations

DEFAULT_HOME_ADVANTAGE = 0.15


def home_advantage(sport: str = "football") -> float:
    return {
        "football": 0.15,
        "basketball": 0.10,
        "tennis": 0.0,
        "cricket": 0.08,
    }.get(sport, DEFAULT_HOME_ADVANTAGE)
