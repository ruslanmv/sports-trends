from typing import Any


def global_interest_score(match: dict[str, Any]) -> float:
    return float(match.get("interest_score", 0))
