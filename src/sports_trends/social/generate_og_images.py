"""Generate lightweight SVG Open Graph cards for matches (no binary deps)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#08140e"/><stop offset="0.6" stop-color="#0c3a27"/><stop offset="1" stop-color="#06160f"/>
  </linearGradient></defs>
  <rect width="1200" height="630" fill="url(#g)"/>
  <text x="80" y="120" fill="#18d08f" font-family="Inter,Arial" font-size="30" font-weight="800" letter-spacing="4">{league}</text>
  <text x="80" y="300" fill="#ffffff" font-family="Inter,Arial" font-size="84" font-weight="800">{home}</text>
  <text x="80" y="360" fill="#9aa6b0" font-family="Inter,Arial" font-size="40">vs</text>
  <text x="80" y="450" fill="#ffffff" font-family="Inter,Arial" font-size="84" font-weight="800">{away}</text>
  <text x="80" y="560" fill="#18d08f" font-family="Inter,Arial" font-size="34" font-weight="700">{label}</text>
</svg>
"""


def _esc(s: Any) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_og_svg(match: dict[str, Any]) -> str:
    return _SVG.format(
        league=_esc(match.get("league", "")),
        home=_esc(match.get("home_team", "")),
        away=_esc(match.get("away_team", "")),
        label=_esc(match.get("prediction_label", "AI prediction")),
    )


def generate_og_images(matches: list[dict[str, Any]] | None = None,
                       out_dir: str | Path = "assets/images/sports/og") -> list[str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for m in (matches or []):
        slug = m.get("match_id")
        if not slug:
            continue
        path = out_dir / f"{slug}.svg"
        path.write_text(render_og_svg(m), encoding="utf-8")
        written.append(str(path))
    return written
