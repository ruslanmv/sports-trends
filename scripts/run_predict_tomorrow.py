#!/usr/bin/env python3
"""CLI placeholder for run_predict_tomorrow.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.inference.predict import predict_window

if __name__ == "__main__":
    print(predict_window())
