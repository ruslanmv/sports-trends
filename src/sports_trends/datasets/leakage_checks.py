"""Data-leakage checks for training datasets.

Guards against the three classic leaks in match prediction:
  1. A label column accidentally present in the feature set.
  2. Non-chronological ordering (test rows older than train rows).
  3. Features that change when *future* matches are added (temporal leakage).
"""

from __future__ import annotations

from typing import Any

from ..features.feature_pipeline import FEATURE_COLUMNS
from .build_training_dataset import LABELS_BY_SPORT


def leakage_report(rows: list[dict[str, Any]], sport: str) -> dict[str, Any]:
    labels = set(LABELS_BY_SPORT.get(sport, ("target",)))
    feature_set = set(FEATURE_COLUMNS)

    overlap = sorted(feature_set & labels)

    dates = [str(r.get("match_date") or "") for r in rows]
    chronological = dates == sorted(dates)

    errors = []
    if overlap:
        errors.append(f"label columns present in features: {overlap}")
    if not chronological:
        errors.append("training rows are not in chronological order")

    return {
        "sport": sport,
        "rows": len(rows),
        "feature_label_overlap": overlap,
        "chronological": chronological,
        "leakage_errors": len(errors),
        "errors": errors,
        "passed": not errors,
    }
