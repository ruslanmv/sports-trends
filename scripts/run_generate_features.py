#!/usr/bin/env python3
"""CLI placeholder for run_generate_features.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.features.feature_pipeline import generate_features

if __name__ == "__main__":
    print(generate_features())
