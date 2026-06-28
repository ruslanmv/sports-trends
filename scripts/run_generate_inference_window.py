#!/usr/bin/env python3
"""Build tomorrow's inference window and save it as Parquet (Batch 8)."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from sports_trends.config import LOCAL_LAKE_DIR
from sports_trends.inference.build_window import build_inference_window
from sports_trends.providers import _mock_data
from sports_trends.providers.fallback_provider import FallbackProvider

if __name__ == "__main__":
    history = []
    for s in ("football", "basketball", "tennis", "cricket"):
        history += _mock_data.historical_results(s, 200)
    window = build_inference_window(FallbackProvider().fetch_tomorrow_matches(), history)
    day = datetime.now(timezone.utc).date().isoformat()
    out = LOCAL_LAKE_DIR / "gold" / "inference" / "tomorrow" / f"date={day}" / "inference_input.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(window).to_parquet(out, index=False)
    print(json.dumps({"rows": len(window), "out": str(out)}, indent=2))
