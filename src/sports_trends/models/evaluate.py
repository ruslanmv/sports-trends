"""Evaluation metrics for baseline classifiers."""

from __future__ import annotations

from typing import Any


def evaluate_classifier(model, X, y) -> dict[str, Any]:
    """Return accuracy + log loss (when probabilities are available)."""
    from sklearn.metrics import accuracy_score, log_loss

    preds = model.predict(X)
    metrics: dict[str, Any] = {
        "n": int(len(y)),
        "accuracy": round(float(accuracy_score(y, preds)), 4),
    }
    try:
        proba = model.predict_proba(X)
        metrics["log_loss"] = round(float(log_loss(y, proba, labels=list(model.classes_))), 4)
    except Exception:  # pragma: no cover - proba not available / single class
        metrics["log_loss"] = None
    return metrics
