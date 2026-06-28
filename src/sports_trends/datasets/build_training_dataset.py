"""Build model-ready training datasets from finished-match history.

For every finished match we compute features using *only* matches that finished
strictly earlier (reusing the leakage-safe feature pipeline), then attach labels
derived from that match's own result. Rows are emitted in chronological order so
a time-based train/val/test split never leaks the future into the past.
"""

from __future__ import annotations

from typing import Any

from ..features.feature_pipeline import FEATURE_COLUMNS, features_for_fixture

# Label columns per sport (kept separate from FEATURE_COLUMNS so leakage checks
# can assert the two sets never overlap).
LABELS_BY_SPORT: dict[str, tuple[str, ...]] = {
    "football": ("target", "home_win", "draw", "away_win", "total_goals", "both_teams_scored", "over_2_5_goals"),
    "basketball": ("target", "home_win", "away_win", "total_points", "point_difference"),
    "tennis": ("target", "player_1_win", "player_2_win"),
    "cricket": ("target", "home_win", "away_win"),
}

# Classes used by the baseline classifier for each sport.
TARGET_CLASSES: dict[str, list[str]] = {
    "football": ["home_win", "draw", "away_win"],
    "basketball": ["home_win", "away_win"],
    "tennis": ["player_1_win", "player_2_win"],
    "cricket": ["home_win", "away_win"],
}


def _scores(match: dict[str, Any]) -> tuple[float, float] | None:
    try:
        return float(match.get("home_score")), float(match.get("away_score"))
    except (TypeError, ValueError):
        return None


def label_row(match: dict[str, Any], sport: str) -> dict[str, Any] | None:
    s = _scores(match)
    if s is None:
        return None
    hs, as_ = s
    if sport == "football":
        target = 0 if hs > as_ else (1 if hs == as_ else 2)
        return {
            "target": target,
            "home_win": int(hs > as_), "draw": int(hs == as_), "away_win": int(hs < as_),
            "total_goals": hs + as_, "both_teams_scored": int(hs > 0 and as_ > 0),
            "over_2_5_goals": int(hs + as_ > 2.5),
        }
    if sport == "basketball":
        return {
            "target": 0 if hs > as_ else 1,
            "home_win": int(hs > as_), "away_win": int(hs < as_),
            "total_points": hs + as_, "point_difference": hs - as_,
        }
    if sport == "tennis":
        return {"target": 0 if hs > as_ else 1, "player_1_win": int(hs > as_), "player_2_win": int(hs < as_)}
    # cricket / default: binary home/away
    return {"target": 0 if hs > as_ else 1, "home_win": int(hs > as_), "away_win": int(hs < as_)}


def build_training_dataset(history: list[dict[str, Any]], sport: str) -> list[dict[str, Any]]:
    """Return chronologically-ordered training rows (features + labels)."""
    finished = [m for m in history if (m.get("status") == "finished") and _scores(m) is not None]
    finished.sort(key=lambda m: str(m.get("date") or m.get("match_date") or ""))
    rows: list[dict[str, Any]] = []
    for match in finished:
        labels = label_row(match, sport)
        if labels is None:
            continue
        feats = features_for_fixture(match, history)  # uses strictly-earlier matches only
        feature_only = {c: feats[c] for c in FEATURE_COLUMNS}
        rows.append({
            "match_id": feats["match_id"],
            "sport": sport,
            "match_date": feats["match_date"],
            **feature_only,
            **labels,
        })
    return rows


def time_split(rows: list[dict[str, Any]], train: float = 0.7, val: float = 0.15) -> dict[str, list[dict[str, Any]]]:
    """Chronological split (rows must already be time-ordered)."""
    n = len(rows)
    i_train = int(n * train)
    i_val = int(n * (train + val))
    return {"train": rows[:i_train], "validation": rows[i_train:i_val], "test": rows[i_val:]}
