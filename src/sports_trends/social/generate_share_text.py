"""Share text for social posts about a match."""

from __future__ import annotations

from typing import Any

from ..config import SITE_BASE_URL


def share_text(match: dict[str, Any]) -> dict[str, str]:
    home, away = match.get("home_team", ""), match.get("away_team", "")
    label = match.get("prediction_label", "AI prediction inside")
    url = f"{SITE_BASE_URL.rstrip('/')}/match/{match.get('match_id','')}/"
    text = f"{home} vs {away} — {label}. Live odds & results every 30 min ⚽📊"
    return {
        "match_id": match.get("match_id", ""),
        "text": text,
        "url": url,
        "x": f"https://twitter.com/intent/tweet?text={text}&url={url}",
        "whatsapp": f"https://wa.me/?text={text} {url}",
    }


def generate_share_text(matches: list[dict[str, Any]] | None = None) -> list[dict[str, str]]:
    return [share_text(m) for m in (matches or [])]
