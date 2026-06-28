"""Predict outcomes for an inference window and attach explanations."""

from __future__ import annotations

from typing import Any

from ..models.predict import predict_matches


def _explanation(row: dict[str, Any], probs: dict[str, float]) -> list[str]:
    notes = []
    elo_diff = float(row.get("elo_diff", 0))
    if abs(elo_diff) < 25:
        notes.append("Elo difference is small — closely matched sides.")
    else:
        leader = row.get("home_team") if elo_diff > 0 else row.get("away_team")
        notes.append(f"{leader} carries the stronger Elo rating.")
    hf, af = row.get("home_form_last_5", 0), row.get("away_form_last_5", 0)
    notes.append(f"Recent form (last 5): {row.get('home_team')} {hf:.2f} vs {row.get('away_team')} {af:.2f}.")
    h2h = (row.get("h2h_home_wins", 0), row.get("h2h_draws", 0), row.get("h2h_away_wins", 0))
    notes.append(f"Head-to-head: {h2h[0]}–{h2h[1]}–{h2h[2]} (home–draw–away).")
    return notes


def _label(probs: dict[str, float], row: dict[str, Any]) -> str:
    top = max(probs, key=probs.get)
    if top == "draw":
        return "AI: draw likely"
    team = row.get("home_team") if top in ("home_win", "player_1_win") else row.get("away_team")
    return f"AI: {team} favoured"


def predict_window(window: list[dict[str, Any]] | None = None,
                   models_root: str = ".models") -> list[dict[str, Any]]:
    window = window or []
    by_sport: dict[str, list[dict[str, Any]]] = {}
    for row in window:
        by_sport.setdefault(row.get("sport", "football"), []).append(row)

    predictions: list[dict[str, Any]] = []
    for sport, rows in by_sport.items():
        for pred in predict_matches(rows, sport=sport, models_root=models_root):
            probs = pred["probabilities"]
            confidence = round(max(probs.values()), 3)
            predictions.append({
                **pred,
                "confidence": confidence,
                "prediction_label": _label(probs, pred),
                "explanation": _explanation(pred, probs),
            })
    return predictions
