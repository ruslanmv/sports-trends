"""Turn settled prediction-ledger rows into leakage-safe training rows.

Settled rows already carry the exact feature snapshot used at prediction time
*and* the realized label columns (added during reconciliation). So building a
training row is a pure projection — no feature recomputation, no risk of peeking
at the result. These rows augment ``gold/training`` with real, accumulated
outcomes so each retrain is coherent with the latest matches.
"""

from __future__ import annotations

from typing import Any

from ..features.feature_pipeline import FEATURE_COLUMNS
from .build_training_dataset import LABELS_BY_SPORT


def build_prediction_dataset(settled_rows: list[dict[str, Any]] | None = None,
                             sport: str | None = None) -> list[dict[str, Any]]:
    """Project settled ledger rows into chronological training rows.

    Args:
        settled_rows: rows produced by ``prediction_ledger.reconcile`` (status
            ``settled``), each holding the feature snapshot + ``label_*`` columns.
        sport: optional filter; when given, only rows for that sport are emitted.

    Returns rows shaped exactly like :func:`build_training_dataset.build_training_dataset`
    output (``match_id``, ``sport``, ``match_date``, features…, labels…), sorted
    chronologically so a time-based split never leaks the future.
    """
    settled_rows = settled_rows or []
    out: list[dict[str, Any]] = []
    for r in settled_rows:
        if r.get("status") != "settled":
            continue
        s = r.get("sport", "football")
        if sport and s != sport:
            continue
        labels = {k: r[f"label_{k}"] for k in LABELS_BY_SPORT.get(s, ("target",))
                  if f"label_{k}" in r}
        if "target" not in labels:
            continue
        out.append({
            "match_id": r.get("match_id"),
            "sport": s,
            "match_date": r.get("match_date") or "",
            **{c: r.get(c, 0) for c in FEATURE_COLUMNS},
            **labels,
        })
    out.sort(key=lambda x: str(x.get("match_date") or ""))
    return out


def merge_training_rows(history_rows: list[dict[str, Any]],
                        prediction_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge history-derived rows with settled-prediction rows.

    Settled real outcomes win on a shared ``match_id`` (they reflect what we
    actually predicted and observed). Rows without a usable id (e.g. mock
    history) are all kept — de-duplication only applies to real ids — and the
    result is re-sorted chronologically.
    """
    settled_ids = {row.get("match_id") for row in prediction_rows
                   if row.get("match_id") is not None}
    merged = [row for row in history_rows
              if row.get("match_id") is None or row.get("match_id") not in settled_ids]
    merged.extend(prediction_rows)
    merged.sort(key=lambda x: str(x.get("match_date") or ""))
    return merged
