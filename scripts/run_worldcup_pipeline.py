#!/usr/bin/env python3
"""Fetch World Cup fixtures, predict (90-min + to-advance + qualifiers), publish JSON.

Free + offline-safe: uses OpenFootball (no key) when online, else bundled mock
data. Add SPORTS_API_FOOTBALL_KEY or FOOTBALL_DATA_TOKEN for richer live data.

Usage: python scripts/run_worldcup_pipeline.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.inference.worldcup_publish import publish_worldcup_json
from sports_trends.providers.worldcup_provider import WorldCupProvider

if __name__ == "__main__":
    provider = WorldCupProvider()
    summary = publish_worldcup_json(provider=provider)
    summary["source"] = provider.source
    print(json.dumps(summary, indent=2))
