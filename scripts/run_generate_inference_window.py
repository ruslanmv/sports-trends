#!/usr/bin/env python3
"""Build tomorrow's inference window, save Parquet, and upload to the Hugging
Face dataset (gold/inference/tomorrow). Dry-run without HF_TOKEN.

Usage:
    python scripts/run_generate_inference_window.py [--dry-run]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from sports_trends.hf.dataset_client import DatasetClient
from sports_trends.hf.partitions import inference_partition
from sports_trends.inference.build_window import build_inference_window
from sports_trends.logging_config import get_logger
from sports_trends.providers import _mock_data
from sports_trends.providers.fallback_provider import FallbackProvider

logger = get_logger("run_generate_inference_window")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    client = DatasetClient(dry_run=True if args.dry_run else None)

    history: list[dict] = []
    for s in ("football", "basketball", "tennis", "cricket"):
        history += _mock_data.historical_results(s, 200)
    window = build_inference_window(FallbackProvider().fetch_tomorrow_matches(), history)

    day = datetime.now(timezone.utc).date().isoformat()
    path_in_repo = inference_partition(day, "inference_input.parquet")
    out = Path(client.local_dir) / path_in_repo
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(window).to_parquet(out, index=False)

    result = client.upload_file(out, path_in_repo)
    logger.info("Inference window: %d rows -> %s (%s)", len(window), path_in_repo, result["status"])
    print(json.dumps({"mode": client.mode, "rows": len(window), "path": path_in_repo}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
