#!/usr/bin/env python3
"""Normalize raw fixtures into canonical matches and report duplicates."""

from __future__ import annotations

import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.ingestion.fetch_raw_data import fetch_raw_data
from sports_trends.ingestion.normalize_matches import find_duplicate_ids, normalize_matches

if __name__ == "__main__":
    raw = fetch_raw_data("all")
    rows = raw["tomorrow"] + raw["today"]
    matches = normalize_matches(rows, provider="fallback")
    print(json.dumps({"normalized": len(matches), "duplicates": len(find_duplicate_ids(matches))}, indent=2))
