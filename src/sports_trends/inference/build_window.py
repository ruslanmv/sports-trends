"""Build the compact inference window for tomorrow's fixtures.

Combines normalized fixtures with leakage-safe features into one row per match
containing exactly the model-input columns plus identity/metadata fields.
"""

from __future__ import annotations

from typing import Any

from ..features.feature_pipeline import FEATURE_COLUMNS, generate_features
from ..ingestion.normalize_matches import normalize_matches

WINDOW_META = ("match_id", "sport", "league", "match_date", "home_team", "away_team")
MODEL_INPUT_VERSION = "v1"


def build_inference_window(
    raw_fixtures: list[dict[str, Any]] | None = None,
    history: list[dict[str, Any]] | None = None,
    provider: str = "fallback",
) -> list[dict[str, Any]]:
    fixtures = normalize_matches(raw_fixtures or [], provider=provider)
    feature_rows = generate_features(fixtures, history or [])
    window = []
    for fx, feats in zip(fixtures, feature_rows):
        row = {
            "match_id": fx["match_id"],
            "sport": fx["sport"],
            "league": fx["league_name"],
            "match_date": fx["match_date"],
            "kickoff": fx.get("kickoff"),
            "home_team_id": fx["home_team_id"],
            "home_team": fx["home_team"],
            "away_team_id": fx["away_team_id"],
            "away_team": fx["away_team"],
            **{c: feats[c] for c in FEATURE_COLUMNS},
            "model_input_version": MODEL_INPUT_VERSION,
        }
        window.append(row)
    return window
