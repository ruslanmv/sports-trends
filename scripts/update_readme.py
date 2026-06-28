#!/usr/bin/env python3
"""Refresh the dynamic blocks of README.md from the generated JSON.

Injects, between HTML-comment markers, (1) tomorrow's Top-5 AI predictions and
(2) the live model registry. Runs daily in CI so the README always shows the
latest games and freshly trained models. Safe to run locally; a no-op if the
markers are missing.

Usage: python scripts/update_readme.py
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sports_trends.config import DATA_DIR, REPO_ROOT
from sports_trends.models.model_zoo import registry_table

README = REPO_ROOT / "README.md"
SPORT_EMOJI = {"football": "⚽", "basketball": "🏀", "tennis": "🎾",
               "cricket": "🏏", "baseball": "⚾", "esports": "🎮"}


def _load(name: str, default):
    path = DATA_DIR / name
    return json.loads(path.read_text()) if path.exists() else default


def _bar(p: float, width: int = 10) -> str:
    filled = round((p or 0) * width)
    return "█" * filled + "░" * (width - filled)


def top5_block() -> str:
    data = _load("tomorrow.json", {"matches": []})
    matches = data.get("matches", [])[:5]
    if not matches:
        return "_No fixtures available right now — check back after the next daily run._"
    lines = [
        "| # | Match | League | Kickoff | AI Pick | Confidence |",
        "|:-:|:------|:-------|:-------:|:--------|:-----------|",
    ]
    for i, m in enumerate(matches, 1):
        emoji = SPORT_EMOJI.get(m.get("sport"), "🏆")
        probs = m.get("probabilities", {})
        conf = m.get("confidence", max(probs.values()) if probs else 0)
        pick = (m.get("prediction_label", "") or "").replace("AI:", "").strip() or "—"
        lines.append(
            f"| {i} | {emoji} **{m.get('home_team','')}** vs **{m.get('away_team','')}** "
            f"| {m.get('league','')} | {m.get('kickoff_label','TBD')} "
            f"| {pick} | `{_bar(conf)}` {round(conf*100)}% |"
        )
    return "\n".join(lines)


def models_block() -> str:
    summary = _load("models.json", None)
    rows = registry_table()
    trained = (summary or {}).get("models", {})
    lines = [
        "| Sport | Model | Algorithm | Task | Latest accuracy |",
        "|:------|:------|:----------|:-----|:---------------:|",
    ]
    for r in rows:
        sport = r["sport"]
        emoji = SPORT_EMOJI.get(sport, "🏆")
        acc = trained.get(sport, {}).get("metrics", {}).get("accuracy")
        acc_s = f"{acc:.3f}" if isinstance(acc, (int, float)) else "—"
        lines.append(f"| {emoji} {sport.title()} | `{r['model_name']}` | {r['algo']} | {r['task']} | {acc_s} |")
    return "\n".join(lines)


def season_block() -> str:
    s = _load("season.json", None)
    if not s:
        from sports_trends.features.sports_calendar import season_context
        s = season_context()
    feat = s.get("featured", {})
    active = s.get("active", [])[:8]
    upcoming = s.get("upcoming", [])[:4]
    lines = [f"**🔥 Featured right now:** {feat.get('emoji','🏆')} **{feat.get('name','')}** "
             f"({feat.get('sport','')})", "", "**In season today:**", ""]
    lines.append(" · ".join(f"{a.get('emoji','')} {a['name']}" for a in active) or "_off-season_")
    if upcoming:
        lines += ["", "**Starting soon:**", ""]
        lines.append(" · ".join(f"{u['name']} (in {u['starts_in_days']}d)" for u in upcoming))
    return "\n".join(lines)


def worldcup_block() -> str:
    data = _load("worldcup-predictions.json", {"matches": []})
    matches = [m for m in data.get("matches", []) if m.get("to_advance")][:3]
    if not matches:
        return "_World Cup predictions appear here during the tournament._"
    lines = [
        "| Tie | Stage | 90' result | To advance |",
        "|:----|:-----:|:-----------|:-----------|",
    ]
    for m in matches:
        r = m.get("result_90", {})
        adv = m.get("to_advance", {})
        adv_s = " · ".join(f"**{k}** {round(v*100)}%" for k, v in sorted(adv.items(), key=lambda kv: -kv[1]))
        stage = (m.get("stage", "") or "").replace("_", " ").title()
        lines.append(
            f"| ⚽ {m.get('home_team','')} vs {m.get('away_team','')} | {stage} "
            f"| {m.get('home_team','')} {round(r.get('team1',0)*100)}% · "
            f"draw {round(r.get('draw',0)*100)}% · {m.get('away_team','')} {round(r.get('team2',0)*100)}% "
            f"| {adv_s} |"
        )
    return "\n".join(lines)


def _replace(text: str, tag: str, block: str) -> str:
    pat = re.compile(rf"(<!-- {tag}:START -->)(.*?)(<!-- {tag}:END -->)", re.DOTALL)
    if not pat.search(text):
        print(f"warning: markers for {tag} not found", file=sys.stderr)
        return text
    return pat.sub(lambda m: f"{m.group(1)}\n{block}\n{m.group(3)}", text)


def main() -> int:
    if not README.exists():
        print("README.md not found", file=sys.stderr)
        return 1
    text = README.read_text(encoding="utf-8")
    text = _replace(text, "SEASON", season_block())
    text = _replace(text, "TOP5", top5_block())
    text = _replace(text, "WORLDCUP", worldcup_block())
    text = _replace(text, "MODELS", models_block())
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    text = _replace(text, "UPDATED", f"_Last updated: **{stamp}** — refreshed automatically every day._")
    README.write_text(text, encoding="utf-8")
    print("README.md dynamic blocks updated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
