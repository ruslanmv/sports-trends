#!/usr/bin/env python3
"""Fetch raw data across sports and print a per-window count summary."""

from __future__ import annotations

import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.ingestion.fetch_raw_data import fetch_raw_data

if __name__ == "__main__":
    data = fetch_raw_data("all")
    print(json.dumps({k: len(v) for k, v in data.items()}, indent=2))
