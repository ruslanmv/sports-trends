#!/usr/bin/env python3
"""Log today's predictions to the prediction ledger (step 1 of the feedback loop).

Builds the inference window exactly like the frontend predictor, runs the
per-sport models (or the Elo heuristic), then records one *open* ledger row per
fixture — feature snapshot + model version + probabilities + pick — partitioned
by sport/date. Uploads to Hugging Face when ``HF_TOKEN`` is set, else dry-runs
to the local data lake.

Usage:
    python scripts/run_log_predictions.py            # auto (dry-run if no token)
    python scripts/run_log_predictions.py --dry-run  # never contact Hugging Face
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from sports_trends.datasets.prediction_ledger import build_ledger_records
from sports_trends.hf.dataset_client import DatasetClient
from sports_trends.hf.partitions import predictions_partition
from sports_trends.inference.build_window import build_inference_window
from sports_trends.inference.predict import predict_window
from sports_trends.logging_config import get_logger
from sports_trends.models.registry import LOCAL_MODELS_DIR
from sports_trends.providers.fallback_provider import FallbackProvider
from sports_trends.providers import _mock_data

logger = get_logger("run_log_predictions")


def _history() -> list[dict]:
    rows: list[dict] = []
    for sport in ("football", "basketball", "tennis", "cricket"):
        rows.extend(_mock_data.historical_results(sport, n_matches=200))
    return rows


def _model_versions() -> dict[str, str]:
    """Read current production model versions from the local registry, if any."""
    reg = LOCAL_MODELS_DIR / "registry" / "latest_versions.json"
    if reg.exists():
        try:
            data = json.loads(reg.read_text())
            return {s: v.get("version", "unknown") for s, v in data.items()}
        except Exception:  # pragma: no cover - corrupt file
            pass
    return {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    client = DatasetClient(dry_run=True if args.dry_run else None)

    raw = FallbackProvider().fetch_tomorrow_matches()
    window = build_inference_window(raw, _history())
    predictions = predict_window(window)
    rows = build_ledger_records(predictions, model_versions=_model_versions())

    day = datetime.now(timezone.utc).date().isoformat()
    by_sport: dict[str, list[dict]] = {}
    for r in rows:
        by_sport.setdefault(r["sport"], []).append(r)

    uploaded = []
    for sport, sport_rows in by_sport.items():
        path = predictions_partition(sport, day)
        local = Path(client.local_dir) / path
        local.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(sport_rows).to_parquet(local, index=False)
        res = client.upload_file(local, path)
        uploaded.append({"sport": sport, "rows": len(sport_rows), "status": res["status"]})
        logger.info("logged %-10s %d predictions -> %s", sport, len(sport_rows), path)

    print(json.dumps({"mode": client.mode, "date": day, "logged": uploaded,
                      "total": len(rows)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
