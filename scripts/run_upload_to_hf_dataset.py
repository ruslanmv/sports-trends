#!/usr/bin/env python3
"""CLI placeholder for run_upload_to_hf_dataset.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.hf.upload import upload_placeholder

if __name__ == "__main__":
    print(upload_placeholder())
