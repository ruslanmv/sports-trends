"""Outcome prediction: trained model when available, Elo heuristic otherwise."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..features.feature_pipeline import FEATURE_COLUMNS
from ..datasets.build_training_dataset import TARGET_CLASSES


def _load_local_model(sport: str, models_root: Path):
    import joblib
    candidates = [models_root / sport / "latest" / "model.pkl",
                  models_root / sport / "build" / "model.pkl"]
    for c in candidates:
        if c.exists():
            return joblib.load(c)
    return None


def _heuristic_probs(row: dict[str, Any], sport: str) -> dict[str, float]:
    """Elo-difference logistic heuristic so predictions work with no model."""
    import math
    diff = float(row.get("elo_diff", 0.0)) + 400 * float(row.get("home_advantage", 0.0))
    p_home = 1.0 / (1.0 + 10 ** (-diff / 400.0))
    classes = TARGET_CLASSES.get(sport, ["home_win", "away_win"])
    if "draw" in classes:
        draw = 0.26 * (1 - abs(2 * p_home - 1))
        home = p_home * (1 - draw)
        away = (1 - p_home) * (1 - draw)
        total = home + draw + away
        return {"home_win": home / total, "draw": draw / total, "away_win": away / total}
    return {classes[0]: p_home, classes[1]: 1 - p_home}


def predict_matches(rows: list[dict[str, Any]] | None = None, sport: str = "football",
                    models_root: str | Path = ".models") -> list[dict[str, Any]]:
    rows = rows or []
    model = _load_local_model(sport, Path(models_root))
    classes = TARGET_CLASSES.get(sport, ["home_win", "away_win"])
    out = []
    for row in rows:
        if model is not None:
            import pandas as pd
            X = pd.DataFrame([{c: row.get(c, 0) for c in FEATURE_COLUMNS}])
            proba = model.predict_proba(X)[0]
            probs = {classes[i]: float(proba[idx]) for idx, i in enumerate(model.classes_)} \
                if len(model.classes_) == len(classes) else \
                {classes[int(c)]: float(p) for c, p in zip(model.classes_, proba)}
        else:
            probs = _heuristic_probs(row, sport)
        out.append({**row, "probabilities": probs, "model_used": model is not None})
    return out
