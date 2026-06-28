"""SEO meta titles/descriptions for match and league pages."""

from __future__ import annotations

from typing import Any


def meta_for_match(match: dict[str, Any]) -> dict[str, str]:
    home, away = match.get("home_team", ""), match.get("away_team", "")
    league = match.get("league", "")
    probs = match.get("probabilities", {}) or {}
    top = max(probs, key=probs.get) if probs else None
    pick = {"home_win": home, "away_win": away, "draw": "Draw",
            "player_1_win": home, "player_2_win": away}.get(top, "")
    title = f"{home} vs {away} prediction & live odds — {league}"
    desc = (f"AI prediction for {home} vs {away} ({league}): "
            f"{'likely ' + pick if pick else 'a balanced contest'}. "
            "Win probabilities, confidence, and live results updated every 30 minutes.")
    return {"match_id": match.get("match_id", ""), "title": title[:70], "description": desc[:160]}


def generate_meta_descriptions(matches: list[dict[str, Any]] | None = None) -> list[dict[str, str]]:
    return [meta_for_match(m) for m in (matches or [])]
