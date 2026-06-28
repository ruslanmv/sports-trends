#!/usr/bin/env python3
"""Generate leakage-safe feature rows for tomorrow's fixtures and save Parquet.

Uses mock history + fixtures when no API keys are configured.

Usage:
    python scripts/run_generate_features.py [--out gold/features/match_features/...]
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.config import LOCAL_LAKE_DIR
from sports_trends.features.feature_pipeline import generate_features, save_features_parquet
from sports_trends.ingestion.normalize_matches import normalize_matches
from sports_trends.logging_config import get_logger
from sports_trends.providers import _mock_data
from sports_trends.providers.fallback_provider import FallbackProvider

logger = get_logger("run_generate_features")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=None, help="Output Parquet path.")
    args = parser.parse_args()

    fixtures = normalize_matches(FallbackProvider().fetch_tomorrow_matches(), provider="fallback")
    history: list[dict] = []
    for sport in ("football", "basketball", "tennis", "cricket"):
        history.extend(_mock_data.historical_results(sport))

    rows = generate_features(fixtures, history)
    day = datetime.now(timezone.utc).date().isoformat()
    out = Path(args.out) if args.out else (
        LOCAL_LAKE_DIR / "gold" / "features" / "match_features" / f"date={day}" / "part.parquet"
    )
    save_features_parquet(rows, out)
    logger.info("Wrote %d feature rows -> %s", len(rows), out)
    print(json.dumps({"rows": len(rows), "out": str(out), "columns": list(rows[0].keys()) if rows else []}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
