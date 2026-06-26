from typing import Any


LEAGUE_WEIGHTS = {
    "UEFA Champions League": 100,
    "Premier League": 95,
    "NBA": 90,
    "ATP": 85,
    "ICC Cricket": 85,
}


def league_importance_score(match: dict[str, Any]) -> float:
    return float(LEAGUE_WEIGHTS.get(match.get("league"), 50))
