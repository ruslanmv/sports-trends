#!/usr/bin/env python3
"""CLI placeholder for run_train_models.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.models.train_football import train_football

if __name__ == "__main__":
    print(train_football())
