#!/usr/bin/env python3
"""Generate SEO assets from tomorrow.json: match pages, league pages, sitemap."""

from __future__ import annotations

import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.config import DATA_DIR
from sports_trends.seo.generate_league_pages import generate_league_pages
from sports_trends.seo.generate_match_pages import generate_match_pages
from sports_trends.seo.generate_sitemap import generate_sitemap

if __name__ == "__main__":
    data = json.loads((DATA_DIR / "tomorrow.json").read_text())
    matches = data.get("matches", [])
    match_pages = generate_match_pages(matches, out_dir="sports/match")
    league_pages = generate_league_pages(matches, out_dir="sports/league")
    Path("sports/sitemap-sports.xml").write_text(generate_sitemap(matches), encoding="utf-8")
    print(json.dumps({"match_pages": len(match_pages), "league_pages": len(league_pages),
                      "sitemap": "sports/sitemap-sports.xml"}, indent=2))
