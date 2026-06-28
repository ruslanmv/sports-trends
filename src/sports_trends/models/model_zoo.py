"""Sport-optimized model registry (the "right model for each game").

Each sport has different dynamics, so each gets a different algorithm:

| Sport      | Outcome space          | Model (this zoo)                | Why |
|------------|------------------------|---------------------------------|-----|
| Football   | home / draw / away (3) | HistGradientBoosting (cal.)     | Draws + non-linear Elo×form interactions; gradient boosting handles the 3-way target and feature interactions best. |
| Basketball | home / away (2)        | Logistic Regression (cal.)      | No draws, strong linear Elo signal; logistic gives well-calibrated 2-way probabilities. |
| Tennis     | player1 / player2 (2)  | Gradient Boosting (cal.)        | Head-to-head + surface/form interactions are non-linear; GBDT captures them on small player histories. |
| Cricket    | home / away (2)        | Random Forest (cal.)            | Noisy, format-dependent results; bagged trees are robust to variance and outliers. |

All estimators are wrapped in probability calibration (isotonic/sigmoid) so the
published win probabilities are trustworthy, with a safe fallback to the raw
estimator when the dataset is too small to calibrate.
"""

from __future__ import annotations

from typing import Any

# Per-sport algorithm + human-readable metadata (surfaced in the README/docs).
SPORT_MODELS: dict[str, dict[str, str]] = {
    "football": {
        "algo": "hist_gradient_boosting",
        "model_name": "football-hgb",
        "task": "multiclass: home / draw / away",
        "rationale": "Gradient-boosted trees capture non-linear Elo×form interactions and the 3-way draw outcome.",
    },
    "basketball": {
        "algo": "logistic_regression",
        "model_name": "basketball-logreg",
        "task": "binary: home / away win",
        "rationale": "No draws and a strong linear Elo signal — calibrated logistic regression gives clean probabilities.",
    },
    "tennis": {
        "algo": "gradient_boosting",
        "model_name": "tennis-gbdt",
        "task": "binary: player 1 / player 2 win",
        "rationale": "Head-to-head and form interactions are non-linear; boosting models them on short player histories.",
    },
    "cricket": {
        "algo": "random_forest",
        "model_name": "cricket-rf",
        "task": "binary: home / away win",
        "rationale": "Format-dependent, noisy results — bagged trees are robust to variance and outliers.",
    },
}

DEFAULT_ALGO = "logistic_regression"


def algo_for(sport: str) -> str:
    return SPORT_MODELS.get(sport, {}).get("algo", DEFAULT_ALGO)


def _base_estimator(algo: str):
    from sklearn.ensemble import (
        GradientBoostingClassifier,
        HistGradientBoostingClassifier,
        RandomForestClassifier,
    )
    from sklearn.linear_model import LogisticRegression

    if algo == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, random_state=42)
    if algo == "gradient_boosting":
        return GradientBoostingClassifier(n_estimators=200, learning_rate=0.08, random_state=42)
    if algo == "random_forest":
        return RandomForestClassifier(n_estimators=200, random_state=42)
    return LogisticRegression(max_iter=1000)


def build_model(algo: str, *, calibrate: bool = True):
    """Return a (possibly calibrated) estimator for ``algo``.

    Calibration is attempted with isotonic CV; the caller falls back to the raw
    estimator if the dataset is too small (handled in training).
    """
    base = _base_estimator(algo)
    if not calibrate:
        return base
    from sklearn.calibration import CalibratedClassifierCV

    method = "isotonic" if algo in ("random_forest", "hist_gradient_boosting", "gradient_boosting") else "sigmoid"
    return CalibratedClassifierCV(base, method=method, cv=3)


def registry_table() -> list[dict[str, Any]]:
    """Flat list used by the README / model-registry generators."""
    return [{"sport": s, **meta} for s, meta in SPORT_MODELS.items()]
