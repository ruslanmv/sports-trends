#!/usr/bin/env python3
"""Build per-sport training datasets, run leakage checks, split, save Parquet.

Uploads gold/training partitions + a leakage report to Hugging Face when an
HF_TOKEN is available; otherwise runs in dry-run against the local data lake.

Usage:
    python scripts/run_build_training_dataset.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from sports_trends.config import LOCAL_LAKE_DIR
from sports_trends.datasets.build_prediction_dataset import (
    build_prediction_dataset, merge_training_rows,
)
from sports_trends.datasets.build_training_dataset import build_training_dataset, time_split
from sports_trends.datasets.leakage_checks import leakage_report
from sports_trends.hf.dataset_client import DatasetClient
from sports_trends.hf.partitions import quality_path, training_partition
from sports_trends.logging_config import get_logger
from sports_trends.providers import _mock_data


def _settled_outcomes(lake: Path, sport: str) -> list[dict]:
    """Real, accumulated settled-prediction rows for ``sport`` from the lake."""
    rows: list[dict] = []
    for f in sorted((lake / "gold" / "outcomes" / sport).glob("date=*/settled.parquet")):
        try:
            rows.extend(pd.read_parquet(f).to_dict("records"))
        except Exception:  # pragma: no cover - skip unreadable partition
            continue
    return rows

logger = get_logger("run_build_training_dataset")
TRAIN_SPORTS = ("football", "basketball", "tennis", "cricket")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    client = DatasetClient(dry_run=True if args.dry_run else None)

    summary = {}
    leak_errors_total = 0
    lake = Path(client.local_dir)
    for sport in TRAIN_SPORTS:
        history = _mock_data.historical_results(sport, n_matches=200)
        history_rows = build_training_dataset(history, sport)
        # Feedback loop: fold in real, accumulated settled predictions so each
        # retrain is coherent with the latest observed results.
        settled = _settled_outcomes(lake, sport)
        prediction_rows = build_prediction_dataset(settled, sport=sport)
        rows = merge_training_rows(history_rows, prediction_rows)
        report = leakage_report(rows, sport)
        leak_errors_total += report["leakage_errors"]
        splits = time_split(rows)

        for split_name, split_rows in splits.items():
            if not split_rows:
                continue
            path_in_repo = training_partition(sport, f"{split_name}.parquet")
            local = Path(client.local_dir) / path_in_repo
            local.parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(split_rows).to_parquet(local, index=False)
            client.upload_file(local, path_in_repo)

        summary[sport] = {
            "rows": len(rows),
            "history_rows": len(history_rows),
            "settled_prediction_rows": len(prediction_rows),
            "splits": {k: len(v) for k, v in splits.items()},
            "leakage_passed": report["passed"],
        }
        logger.info("%-10s rows=%d (+%d settled) splits=%s leakage_ok=%s",
                    sport, len(rows), len(prediction_rows), summary[sport]["splits"],
                    report["passed"])

    # Publish a combined leakage report to quality/.
    quality_local = Path(client.local_dir) / quality_path("leakage_report.json")
    quality_local.parent.mkdir(parents=True, exist_ok=True)
    quality_local.write_text(json.dumps({"sports": summary, "total_leakage_errors": leak_errors_total}, indent=2))
    client.upload_file(quality_local, quality_path("leakage_report.json"))

    print(json.dumps({"mode": client.mode, "sports": summary, "total_leakage_errors": leak_errors_total}, indent=2))
    return 1 if leak_errors_total else 0


if __name__ == "__main__":
    raise SystemExit(main())
