#!/usr/bin/env python3
"""Predict tomorrow's fixtures and publish tomorrow/predictions/trending JSON (Batch 8)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.inference.publish_json import publish_frontend_json

if __name__ == "__main__":
    print(json.dumps(publish_frontend_json(), indent=2))
