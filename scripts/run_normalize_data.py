#!/usr/bin/env python3
"""CLI placeholder for run_normalize_data.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.ingestion.normalize_matches import normalize_matches

if __name__ == "__main__":
    print(normalize_matches())
