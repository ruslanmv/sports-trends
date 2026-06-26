#!/usr/bin/env python3
"""CLI placeholder for run_publish_frontend_json.py."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.inference.publish_json import publish_frontend_json

if __name__ == "__main__":
    print(publish_frontend_json())
