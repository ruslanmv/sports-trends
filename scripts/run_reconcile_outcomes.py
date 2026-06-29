#!/usr/bin/env python3
"""Reconcile open predictions against real results (step 2 of the feedback loop).

For every *open* prediction-ledger partition we join to the finished results by
``match_id``, score each prediction (correct? / prob of realized class / Brier /
log loss), and:

  * append the *settled* rows to ``gold/outcomes/<sport>/date=<day>/settled.parquet``
    (real, labelled training data), and
  * rewrite the ledger partition to keep only the still-open rows (so the ledger
    stays a clean queue and matches are never settled twice).

Finally we refresh ``quality/model_performance.json`` — rolling accuracy / log
loss / Brier / calibration per sport & model version, including a
model-vs-heuristic breakdown that shows the trained models beating the baseline.

Dual-mode like the rest of the lake: uploads when ``HF_TOKEN`` is set, otherwise
dry-runs against the local data lake.

Usage:
    python scripts/run_reconcile_outcomes.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from sports_trends.datasets.prediction_ledger import performance_report, reconcile
from sports_trends.hf.dataset_client import DatasetClient
from sports_trends.hf.partitions import outcomes_partition, quality_path
from sports_trends.ingestion.normalize_matches import normalize_matches
from sports_trends.logging_config import get_logger
from sports_trends.providers.fallback_provider import FallbackProvider

logger = get_logger("run_reconcile_outcomes")


def _finished_results() -> list[dict]:
    fb = FallbackProvider()
    raw = fb.fetch_finished_results() + fb.fetch_live_results()
    norm = normalize_matches(raw, provider="fallback")
    return [r for r in norm if r.get("status") == "finished"]


def _read_rows(path: Path) -> list[dict]:
    return pd.read_parquet(path).to_dict("records")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    client = DatasetClient(dry_run=True if args.dry_run else None)
    lake = Path(client.local_dir)

    results = _finished_results()
    day = datetime.now(timezone.utc).date().isoformat()

    ledger_files = sorted((lake / "predictions").glob("*/date=*/predictions.parquet"))
    all_settled: list[dict] = []
    settled_count = open_count = 0

    for f in ledger_files:
        rows = _read_rows(f)
        out = reconcile(rows, results)
        settled, still_open = out["settled"], out["still_open"]
        newly = [r for r in settled if r.get("settled_at")]
        if not newly:
            continue
        all_settled.extend(settled)
        settled_count += len(settled)
        open_count += len(still_open)

        # Append settled rows to the gold outcomes partition for their sport.
        for sport in sorted({r["sport"] for r in settled}):
            sp_rows = [r for r in settled if r["sport"] == sport]
            opath = outcomes_partition(sport, day)
            olocal = lake / opath
            olocal.parent.mkdir(parents=True, exist_ok=True)
            existing = _read_rows(olocal) if olocal.exists() else []
            seen = {r.get("match_id") for r in existing}
            merged = existing + [r for r in sp_rows if r.get("match_id") not in seen]
            pd.DataFrame(merged).to_parquet(olocal, index=False)
            client.upload_file(olocal, opath)

        # Rewrite the ledger partition with only the still-open rows.
        if still_open:
            pd.DataFrame(still_open).to_parquet(f, index=False)
        else:
            f.unlink()
        rel = f.relative_to(lake).as_posix()
        if not args.dry_run and client.token:
            # keep the remote ledger in step with the local queue
            if still_open:
                client.upload_file(f, rel)

    # Refresh the rolling performance report from ALL settled outcomes on disk.
    history_settled = []
    for f in sorted((lake / "gold" / "outcomes").glob("*/date=*/settled.parquet")):
        history_settled.extend(_read_rows(f))
    report = performance_report(history_settled or all_settled)
    qlocal = lake / quality_path("model_performance.json")
    qlocal.parent.mkdir(parents=True, exist_ok=True)
    qlocal.write_text(json.dumps(report, indent=2))
    client.upload_file(qlocal, quality_path("model_performance.json"))

    print(json.dumps({"mode": client.mode, "date": day,
                      "settled": settled_count, "still_open": open_count,
                      "performance": report.get("overall")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
