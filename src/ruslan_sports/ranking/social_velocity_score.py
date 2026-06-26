from typing import Any


def social_velocity_score(match: dict[str, Any]) -> float:
    return float(match.get("social_velocity", 0))
