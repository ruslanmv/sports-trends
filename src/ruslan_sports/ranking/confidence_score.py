from typing import Any


def confidence_score(match: dict[str, Any]) -> float:
    return float(match.get("prediction", {}).get("confidence", 0)) * 100
