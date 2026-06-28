#!/usr/bin/env python3
"""Generate leakage-safe feature rows for tomorrow's fixtures, save Parquet, and
upload to the Hugging Face dataset (gold/features). Dry-run without HF_TOKEN.

Uses mock history + fixtures when no API keys are configured.

Usage:
    python scripts/run_generate_features.py [--dry-run] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.features.feature_pipeline import generate_features, save_features_parquet
from sports_trends.hf.dataset_client import DatasetClient
from sports_trends.hf.partitions import feature_partition
from sports_trends.ingestion.normalize_matches import normalize_matches
from sports_trends.logging_config import get_logger
from sports_trends.providers import _mock_data
from sports_trends.providers.fallback_provider import FallbackProvider

logger = get_logger("run_generate_features")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--out", default=None, help="Output Parquet path.")
    args = parser.parse_args()

    client = DatasetClient(dry_run=True if args.dry_run else None)

    fixtures = normalize_matches(FallbackProvider().fetch_tomorrow_matches(), provider="fallback")
    history: list[dict] = []
    for sport in ("football", "basketball", "tennis", "cricket"):
        history.extend(_mock_data.historical_results(sport))

    rows = generate_features(fixtures, history)
    day = datetime.now(timezone.utc).date().isoformat()
    path_in_repo = feature_partition("match_features", "all", day)
    out = Path(args.out) if args.out else (Path(client.local_dir) / path_in_repo)
    save_features_parquet(rows, out)

    result = client.upload_file(out, path_in_repo)
    logger.info("Features: %d rows -> %s (%s)", len(rows), path_in_repo, result["status"])
    print(json.dumps({"mode": client.mode, "rows": len(rows), "path": path_in_repo}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
