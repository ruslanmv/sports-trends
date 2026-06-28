"""Shared training core for the per-sport baseline models."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from ..datasets.build_training_dataset import build_training_dataset, time_split
from ..datasets.leakage_checks import leakage_report
from ..features.feature_pipeline import FEATURE_COLUMNS
from ..logging_config import get_logger
from ..providers import _mock_data
from .evaluate import evaluate_classifier
from .model_zoo import algo_for, build_model
from .registry import ModelRegistry, model_card

logger = get_logger(__name__)


def _fit_with_fallback(algo: str, X, y):
    """Fit the sport-optimized model; fall back to the uncalibrated estimator
    when the dataset is too small for cross-validated calibration."""
    try:
        model = build_model(algo, calibrate=True)
        model.fit(X, y)
        return model, True
    except Exception as exc:  # calibration CV can fail on tiny/imbalanced data
        logger.warning("calibration failed for %s (%s); using uncalibrated estimator", algo, exc)
        model = build_model(algo, calibrate=False)
        model.fit(X, y)
        return model, False


def train_sport(
    sport: str,
    kind: str | None = None,
    history: list[dict[str, Any]] | None = None,
    publish: bool = False,
    registry: ModelRegistry | None = None,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    """Train, evaluate, persist, and (optionally) publish the sport-optimized model.

    ``kind`` overrides the per-sport algorithm from the model zoo when provided.
    """
    algo = kind or algo_for(sport)
    history = history or _mock_data.historical_results(sport, n_matches=200)
    rows = build_training_dataset(history, sport)
    report = leakage_report(rows, sport)
    if not report["passed"]:
        raise RuntimeError(f"leakage check failed for {sport}: {report['errors']}")

    splits = time_split(rows)
    train_df = pd.DataFrame(splits["train"])
    test_df = pd.DataFrame(splits["test"] or splits["validation"] or splits["train"])

    X_train, y_train = train_df[list(FEATURE_COLUMNS)], train_df["target"]
    model, calibrated = _fit_with_fallback(algo, X_train, y_train)

    metrics = evaluate_classifier(model, test_df[list(FEATURE_COLUMNS)], test_df["target"])
    metrics["calibrated"] = calibrated
    version = f"{sport}-{algo}-{datetime.now(timezone.utc).strftime('%Y%m%d')}"

    out_dir = Path(out_dir or (registry.local_dir if registry else Path(".models")) / sport / "build")
    out_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out_dir / "model.pkl")
    (out_dir / "feature_schema.json").write_text(json.dumps({
        "sport": sport, "model_kind": algo, "model_version": version, "calibrated": calibrated,
        "features": list(FEATURE_COLUMNS), "target_classes": sorted(set(map(int, y_train))),
    }, indent=2))
    (out_dir / "metrics.json").write_text(json.dumps({"version": version, "algo": algo, **metrics}, indent=2))
    (out_dir / "README.md").write_text(model_card(sport, version, metrics))

    logger.info("%-10s trained (%s) acc=%.3f rows=%d", sport, algo, metrics["accuracy"], len(rows))

    published = None
    if publish:
        registry = registry or ModelRegistry()
        published = registry.publish(sport, out_dir, version, metrics)

    return {"sport": sport, "version": version, "metrics": metrics,
            "artifact_dir": str(out_dir), "published": published}
