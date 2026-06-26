from typing import Any
from .global_interest_score import global_interest_score
from .league_importance_score import league_importance_score
from .social_velocity_score import social_velocity_score
from .confidence_score import confidence_score


def rank_top_matches(matches: list[dict[str, Any]], limit: int = 24) -> list[dict[str, Any]]:
    """Rank matches by blended global relevance."""
    def score(match: dict[str, Any]) -> float:
        return (
            global_interest_score(match) * 0.40
            + league_importance_score(match) * 0.25
            + social_velocity_score(match) * 0.20
            + confidence_score(match) * 0.15
        )

    ranked = sorted(matches, key=score, reverse=True)
    return ranked[:limit]
