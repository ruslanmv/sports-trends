"""Prediction ledger — the closed feedback loop that lets our models improve.

The loop has three moves, all leakage-safe and reproducible:

1. **Log** (at prediction time) — every published prediction is recorded with
   the exact feature snapshot it was made from, the model version that produced
   it, the per-class probabilities, the pick and the confidence. Stored *open*.

2. **Reconcile** (after the match finishes) — open predictions are joined to the
   real result by ``match_id``. We attach the realized outcome + label columns,
   and score the prediction (correct?, probability assigned to the realized
   class, Brier score). The row becomes a *settled* record.

3. **Learn** — settled records are (a) aggregated into rolling performance
   metrics (accuracy / log loss / Brier / calibration) so we can prove the model
   adds value over the Elo baseline, and (b) fed back as fresh, real labelled
   training rows so the next retrain is coherent with the latest results.

Because each ledger row carries the feature snapshot used at prediction time,
reconciliation never recomputes features (no chance of peeking at the result),
and the settled rows drop straight into the training pipeline.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any, Iterable

from ..features.feature_pipeline import FEATURE_COLUMNS
from .build_training_dataset import TARGET_CLASSES, label_row

# Columns persisted per ledger row (besides the feature snapshot).
LEDGER_META = (
    "match_id", "sport", "league", "home_team", "away_team",
    "match_date", "kickoff", "predicted_at",
    "model_version", "model_used",
    "predicted_label", "predicted_pick", "predicted_class", "confidence",
    "status",
)
SETTLED_EXTRA = (
    "settled_at", "home_score", "away_score", "actual_class", "actual_label",
    "correct", "prob_actual", "brier", "log_loss",
)

_CLASS_TO_PICK = {
    "home_win": "home", "away_win": "away", "draw": "draw",
    "player_1_win": "home", "player_2_win": "away",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _prob_cols(probs: dict[str, float]) -> dict[str, float]:
    """Flatten per-class probabilities to stable ``prob_<class>`` columns."""
    return {f"prob_{k}": round(float(v), 6) for k, v in probs.items()}


def build_ledger_records(
    predictions: list[dict[str, Any]],
    *,
    model_versions: dict[str, str] | None = None,
    predicted_at: str | None = None,
) -> list[dict[str, Any]]:
    """Build *open* ledger rows from enriched predictions.

    ``predictions`` are rows from :func:`inference.predict.predict_window` (they
    carry the feature snapshot, ``probabilities`` and ``model_used``).
    ``model_versions`` maps ``sport -> version`` (from the model registry).
    """
    model_versions = model_versions or {}
    ts = predicted_at or _now()
    rows: list[dict[str, Any]] = []
    for p in predictions:
        sport = p.get("sport", "football")
        probs = p.get("probabilities") or {}
        if not probs:
            continue
        pick_class = max(probs, key=probs.get)
        snapshot = {c: p.get(c, 0) for c in FEATURE_COLUMNS}
        rows.append({
            "match_id": p.get("match_id"),
            "sport": sport,
            "league": p.get("league"),
            "home_team": p.get("home_team"),
            "away_team": p.get("away_team"),
            "match_date": p.get("match_date") or (p.get("kickoff") or "")[:10],
            "kickoff": p.get("kickoff"),
            "predicted_at": ts,
            "model_version": model_versions.get(sport, "heuristic-elo"),
            "model_used": bool(p.get("model_used", False)),
            "predicted_label": p.get("prediction_label"),
            "predicted_pick": _CLASS_TO_PICK.get(pick_class, pick_class),
            "predicted_class": pick_class,
            "confidence": round(float(max(probs.values())), 4),
            "status": "open",
            **_prob_cols(probs),
            **snapshot,
        })
    return rows


def _actual_class(match: dict[str, Any], sport: str) -> tuple[str, dict[str, Any]] | None:
    labels = label_row(match, sport)
    if labels is None:
        return None
    classes = TARGET_CLASSES.get(sport, ["home_win", "away_win"])
    cls = classes[int(labels["target"])]
    return cls, labels


def reconcile(
    ledger_rows: Iterable[dict[str, Any]],
    results: Iterable[dict[str, Any]],
    *,
    settled_at: str | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Join *open* ledger rows to finished ``results`` by ``match_id``.

    Returns ``{"settled": [...], "still_open": [...]}``. Each settled row gains
    the realized outcome, label columns, and scoring (correct / prob_actual /
    brier / log_loss). Rows whose match has no final score stay open.
    """
    ts = settled_at or _now()
    by_id: dict[Any, dict[str, Any]] = {}
    for r in results:
        mid = r.get("match_id") or r.get("id")
        if mid is not None and r.get("status") == "finished":
            by_id[mid] = r

    settled: list[dict[str, Any]] = []
    still_open: list[dict[str, Any]] = []
    for row in ledger_rows:
        if row.get("status") == "settled":
            settled.append(dict(row))
            continue
        match = by_id.get(row.get("match_id"))
        ac = _actual_class(match, row.get("sport", "football")) if match else None
        if ac is None:
            still_open.append(dict(row))
            continue
        actual_class, labels = ac
        probs = {k[len("prob_"):]: v for k, v in row.items() if k.startswith("prob_")}
        prob_actual = float(probs.get(actual_class, 0.0))
        # Brier across all classes for this row.
        brier = sum((float(probs.get(c, 0.0)) - (1.0 if c == actual_class else 0.0)) ** 2
                    for c in probs) if probs else None
        ll = -math.log(max(prob_actual, 1e-12))
        out = dict(row)
        out.update({
            "status": "settled",
            "settled_at": ts,
            "home_score": match.get("home_score"),
            "away_score": match.get("away_score"),
            "actual_class": actual_class,
            "actual_label": _CLASS_TO_PICK.get(actual_class, actual_class),
            "correct": int(row.get("predicted_class") == actual_class),
            "prob_actual": round(prob_actual, 6),
            "brier": round(brier, 6) if brier is not None else None,
            "log_loss": round(ll, 6),
            **{f"label_{k}": v for k, v in labels.items()},
        })
        settled.append(out)
    return {"settled": settled, "still_open": still_open}


def performance_report(settled_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate settled rows into rolling quality metrics per sport & model.

    Includes a model-vs-heuristic breakdown so we can demonstrate the trained
    models beat the Elo baseline — the signal that justifies retraining.
    """
    def _agg(rows: list[dict[str, Any]]) -> dict[str, Any]:
        n = len(rows)
        if not n:
            return {"n": 0}
        acc = sum(r.get("correct", 0) for r in rows) / n
        lls = [r["log_loss"] for r in rows if r.get("log_loss") is not None]
        briers = [r["brier"] for r in rows if r.get("brier") is not None]
        return {
            "n": n,
            "accuracy": round(acc, 4),
            "log_loss": round(sum(lls) / len(lls), 4) if lls else None,
            "brier": round(sum(briers) / len(briers), 4) if briers else None,
        }

    by_sport: dict[str, list[dict[str, Any]]] = {}
    for r in settled_rows:
        by_sport.setdefault(r.get("sport", "football"), []).append(r)

    report: dict[str, Any] = {"generated_at": _now(), "overall": _agg(settled_rows), "sports": {}}
    for sport, rows in sorted(by_sport.items()):
        model_rows = [r for r in rows if r.get("model_used")]
        heur_rows = [r for r in rows if not r.get("model_used")]
        report["sports"][sport] = {
            **_agg(rows),
            "model": _agg(model_rows),
            "heuristic": _agg(heur_rows),
            "calibration": _calibration(rows),
            "model_versions": sorted({str(r.get("model_version")) for r in rows}),
        }
    return report


def _calibration(rows: list[dict[str, Any]], bins: int = 5) -> list[dict[str, Any]]:
    """Reliability buckets: predicted confidence vs realized hit-rate."""
    buckets: list[dict[str, Any]] = []
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        sel = [r for r in rows if lo <= float(r.get("confidence", 0)) < hi
               or (b == bins - 1 and float(r.get("confidence", 0)) == 1.0)]
        if not sel:
            continue
        buckets.append({
            "range": f"{lo:.1f}-{hi:.1f}",
            "n": len(sel),
            "avg_confidence": round(sum(float(r.get("confidence", 0)) for r in sel) / len(sel), 4),
            "hit_rate": round(sum(r.get("correct", 0) for r in sel) / len(sel), 4),
        })
    return buckets
