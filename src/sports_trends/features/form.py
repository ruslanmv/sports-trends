"""Recent-form features (last N finished matches before a date)."""

from __future__ import annotations

from typing import Any


def _team_history(history, team, as_of):
    rows = [m for m in history
            if (m.get("home_team") or m.get("home")) == team
            or (m.get("away_team") or m.get("away")) == team]
    rows = [m for m in rows if str(m.get("date") or m.get("match_date") or "") < (as_of or "9999")]
    return sorted(rows, key=lambda r: str(r.get("date") or r.get("match_date") or ""))[-50:]


def form_features(history: list[dict[str, Any]], team: str, as_of: str | None, n: int = 5) -> dict[str, float]:
    rows = _team_history(history, team, as_of)[-n:]
    points = goals_for = goals_against = 0
    for m in rows:
        is_home = (m.get("home_team") or m.get("home")) == team
        try:
            hs, as_ = float(m.get("home_score")), float(m.get("away_score"))
        except (TypeError, ValueError):
            continue
        gf, ga = (hs, as_) if is_home else (as_, hs)
        goals_for += gf
        goals_against += ga
        points += 3 if gf > ga else (1 if gf == ga else 0)
    n_played = max(len(rows), 1)
    return {
        f"form_last_{n}": round(points / (3 * n_played), 4),
        f"goals_for_last_{n}": round(goals_for / n_played, 3),
        f"goals_against_last_{n}": round(goals_against / n_played, 3),
    }
