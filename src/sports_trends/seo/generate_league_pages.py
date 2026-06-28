"""Generate per-league index pages from the day's matches."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..ingestion.normalize_matches import slugify


def generate_league_pages(matches: list[dict[str, Any]] | None = None,
                          out_dir: str | Path = "sports/league") -> list[str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    leagues: dict[str, dict[str, Any]] = {}
    for m in (matches or []):
        name = m.get("league", "")
        if not name:
            continue
        leagues.setdefault(slugify(name), {"name": name, "sport": m.get("sport", ""), "count": 0})
        leagues[slugify(name)]["count"] += 1

    written = []
    for slug, info in leagues.items():
        page = (
            "---\n"
            "layout: sports-league\n"
            f'title: "{info["name"]} predictions & results"\n'
            f"permalink: /sports/league/{slug}/\n"
            f'sport: "{info["sport"]}"\n'
            f'league: "{info["name"]}"\n'
            "---\n\n"
            f"# {info['name']}\n\n"
            f"AI predictions and live results for {info['name']}.\n"
        )
        path = out_dir / f"{slug}.md"
        path.write_text(page, encoding="utf-8")
        written.append(str(path))
    return written
