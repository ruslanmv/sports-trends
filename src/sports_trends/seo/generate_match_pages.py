"""Generate per-match Jekyll pages (front matter + JSON-LD) from tomorrow.json."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .generate_json_ld import sport_event_jsonld
from .generate_meta_descriptions import meta_for_match


def _yaml_escape(value: str) -> str:
    return str(value).replace('"', "'")


def render_match_page(match: dict[str, Any]) -> str:
    meta = meta_for_match(match)
    slug = match.get("match_id", "")
    jsonld = sport_event_jsonld(match)
    import json
    fm = [
        "---",
        "layout: sports-match",
        f'title: "{_yaml_escape(meta["title"])}"',
        f"permalink: /sports/match/{slug}/",
        f'description: "{_yaml_escape(meta["description"])}"',
        f'sport: "{match.get("sport", "")}"',
        f'league: "{_yaml_escape(match.get("league", ""))}"',
        f'home_team: "{_yaml_escape(match.get("home_team", ""))}"',
        f'away_team: "{_yaml_escape(match.get("away_team", ""))}"',
        f'kickoff: "{match.get("kickoff", "")}"',
        f"jsonld: {json.dumps(jsonld)}",
        "---",
        "",
        f"# {match.get('home_team','')} vs {match.get('away_team','')}",
        "",
        meta["description"],
    ]
    return "\n".join(fm) + "\n"


def generate_match_pages(matches: list[dict[str, Any]] | None = None,
                         out_dir: str | Path = "sports/match") -> list[str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for match in (matches or []):
        slug = match.get("match_id")
        if not slug:
            continue
        path = out_dir / f"{slug}.md"
        path.write_text(render_match_page(match), encoding="utf-8")
        written.append(str(path))
    return written
