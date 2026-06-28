#!/usr/bin/env python3
"""Generate SVG Open Graph cards for tomorrow's matches."""

from __future__ import annotations

import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.config import DATA_DIR
from sports_trends.social.generate_og_images import generate_og_images

if __name__ == "__main__":
    data = json.loads((DATA_DIR / "tomorrow.json").read_text())
    written = generate_og_images(data.get("matches", []), out_dir="assets/images/sports/og")
    print(json.dumps({"og_images": len(written)}, indent=2))
