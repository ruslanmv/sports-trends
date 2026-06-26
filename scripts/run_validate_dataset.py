#!/usr/bin/env python3
"""CLI placeholder for run_validate_dataset.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.datasets.validate_dataset import validate_dataset

if __name__ == "__main__":
    print(validate_dataset())
