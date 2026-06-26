#!/usr/bin/env python3
"""CLI placeholder for run_generate_inference_window.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.inference.build_window import build_inference_window

if __name__ == "__main__":
    print(build_inference_window())
