"""Elo ratings computed chronologically from finished matches.

Elo is leakage-safe by construction: a fixture's ratings are derived only from
matches that finished strictly before its date.
"""

from __future__ import annotations

from typing import Any

BASE_RATING = 1500.0
K_FACTOR = 20.0


def _expected(r_a: float, r_b: float) -> float:
    return 1.0 / (1.0 + 10 ** ((r_b - r_a) / 400.0))


def _result(home_score: Any, away_score: Any) -> float | None:
    try:
        hs, as_ = float(home_score), float(away_score)
    except (TypeError, ValueError):
        return None
    if hs > as_:
        return 1.0
    if hs < as_:
        return 0.0
    return 0.5


def compute_elo_ratings(history: list[dict[str, Any]], as_of: str | None = None) -> dict[str, float]:
    """Return team -> Elo rating using only matches before ``as_of``."""
    ratings: dict[str, float] = {}
    rows = sorted(history, key=lambda r: str(r.get("date") or r.get("match_date") or ""))
    for m in rows:
        day = str(m.get("date") or m.get("match_date") or "")
        if as_of is not None and day >= as_of:
            break
        home = m.get("home_team") or m.get("home")
        away = m.get("away_team") or m.get("away")
        outcome = _result(m.get("home_score"), m.get("away_score"))
        if not home or not away or outcome is None:
            continue
        r_home = ratings.get(home, BASE_RATING)
        r_away = ratings.get(away, BASE_RATING)
        exp_home = _expected(r_home, r_away)
        ratings[home] = r_home + K_FACTOR * (outcome - exp_home)
        ratings[away] = r_away + K_FACTOR * ((1 - outcome) - (1 - exp_home))
    return ratings


def compute_elo_features(history, home=None, away=None, as_of=None) -> dict[str, float]:
    """Backwards-compatible feature accessor for a single fixture."""
    ratings = compute_elo_ratings(history or [], as_of=as_of)
    home_elo = ratings.get(home, BASE_RATING)
    away_elo = ratings.get(away, BASE_RATING)
    return {"home_elo": home_elo, "away_elo": away_elo, "elo_diff": home_elo - away_elo}
