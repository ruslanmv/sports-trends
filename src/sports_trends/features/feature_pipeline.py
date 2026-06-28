"""Assemble per-fixture feature rows from match history (leakage-safe).

For each fixture, only matches that finished strictly before the fixture date
are used, so no feature can encode the outcome it is meant to predict.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .elo import compute_elo_features
from .form import form_features
from .head_to_head import head_to_head
from .home_advantage import home_advantage
from .league_strength import league_importance_score
from .rest_days import rest_days
from .social_interest import social_interest_score

FEATURE_COLUMNS = (
    "home_elo", "away_elo", "elo_diff",
    "home_form_last_5", "away_form_last_5",
    "home_form_last_10", "away_form_last_10",
    "home_goals_for_last_5", "away_goals_for_last_5",
    "home_goals_against_last_5", "away_goals_against_last_5",
    "home_rest_days", "away_rest_days", "home_advantage",
    "h2h_home_wins", "h2h_draws", "h2h_away_wins",
    "league_importance_score", "social_interest_score",
)


def features_for_fixture(fixture: dict[str, Any], history: list[dict[str, Any]]) -> dict[str, Any]:
    home = fixture.get("home_team") or fixture.get("home")
    away = fixture.get("away_team") or fixture.get("away")
    as_of = str(fixture.get("match_date") or fixture.get("date") or "")
    sport = fixture.get("sport", "football")

    elo = compute_elo_features(history, home, away, as_of)
    h_form5 = form_features(history, home, as_of, 5)
    a_form5 = form_features(history, away, as_of, 5)
    h_form10 = form_features(history, home, as_of, 10)
    a_form10 = form_features(history, away, as_of, 10)
    h2h = head_to_head(history, home, away, as_of)

    row: dict[str, Any] = {
        "match_id": fixture.get("match_id"),
        "sport": sport,
        "league": fixture.get("league_name") or fixture.get("league"),
        "match_date": as_of,
        "home_team": home,
        "away_team": away,
        **elo,
        "home_form_last_5": h_form5["form_last_5"],
        "away_form_last_5": a_form5["form_last_5"],
        "home_form_last_10": h_form10["form_last_10"],
        "away_form_last_10": a_form10["form_last_10"],
        "home_goals_for_last_5": h_form5["goals_for_last_5"],
        "away_goals_for_last_5": a_form5["goals_for_last_5"],
        "home_goals_against_last_5": h_form5["goals_against_last_5"],
        "away_goals_against_last_5": a_form5["goals_against_last_5"],
        "home_rest_days": rest_days(history, home, as_of),
        "away_rest_days": rest_days(history, away, as_of),
        "home_advantage": home_advantage(sport),
        **h2h,
        "league_importance_score": league_importance_score(
            fixture.get("league_name") or fixture.get("league") or ""
        ),
        "social_interest_score": social_interest_score(fixture),
    }
    return row


def generate_features(
    fixtures: list[dict[str, Any]] | None = None,
    history: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Return one feature row per fixture (empty list if no fixtures)."""
    fixtures = fixtures or []
    history = history or []
    return [features_for_fixture(f, history) for f in fixtures]


def save_features_parquet(rows: list[dict[str, Any]], path: str | Path) -> Path:
    """Persist feature rows as Parquet (the on-disk format for ML datasets)."""
    import pandas as pd

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_parquet(path, index=False)
    return path
