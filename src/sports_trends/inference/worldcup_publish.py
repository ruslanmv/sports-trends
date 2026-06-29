"""Publish the public World Cup JSON files consumed by the site + README."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import DATA_DIR, PRODUCT_NAME
from ..providers.worldcup_provider import WorldCupProvider
from ..ranking.rank_top_matches import rank_top_matches
from ..storage.write_json import write_json
from .worldcup_predict import predict_many


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _kickoff_label(iso: str | None) -> str:
    if not iso:
        return "TBD"
    try:
        return datetime.fromisoformat(iso).strftime("%d %b %H:%M")
    except ValueError:
        return "TBD"


_STAGE_LABEL = {
    "group_stage": "Group Stage", "round_of_32": "Round of 32",
    "round_of_16": "Round of 16", "quarterfinals": "Quarter-finals",
    "semifinals": "Semi-finals", "third_place": "Third-place Play-off",
    "final": "Final",
}


def _fixtures_payload(provider: WorldCupProvider) -> dict[str, Any]:
    """Full schedule grouped by round (group → final) for the page's schedule tab."""
    rows = provider.fetch_fixtures()
    by_stage: dict[str, list[dict[str, Any]]] = {}
    for r in rows:
        item = {
            "match_id": r.get("id"),
            "home_team": r.get("home"), "away_team": r.get("away"),
            "home_confederation": r.get("home_confederation"),
            "away_confederation": r.get("away_confederation"),
            "stage": r.get("stage"), "group": r.get("group", ""),
            "date": r.get("date"), "kickoff": r.get("kickoff"),
            "kickoff_label": _kickoff_label(r.get("kickoff")),
            "venue": r.get("venue", ""), "host_city": r.get("host_city", ""),
            "status": r.get("status"),
            "home_score": r.get("home_score"), "away_score": r.get("away_score"),
        }
        by_stage.setdefault(r.get("stage", "group_stage"), []).append(item)

    order = ["group_stage", "round_of_32", "round_of_16", "quarterfinals",
             "semifinals", "third_place", "final"]
    sections = [{
        "stage": s, "label": _STAGE_LABEL.get(s, s.replace("_", " ").title()),
        "matches": by_stage[s],
    } for s in order if s in by_stage]
    upcoming_count = sum(1 for r in rows if r.get("status") != "finished")
    return {"sections": sections, "total": len(rows), "upcoming": upcoming_count}


def build_worldcup_json(provider: WorldCupProvider | None = None) -> dict[str, dict[str, Any]]:
    provider = provider or WorldCupProvider()
    upcoming = provider.fetch_upcoming()
    qualifiers = provider.fetch_qualifiers()

    preds = predict_many(upcoming)
    for p in preds:
        p["kickoff_label"] = _kickoff_label(p.get("kickoff"))
    preds = rank_top_matches(preds)
    qual_preds = predict_many(qualifiers)

    meta = {"product": PRODUCT_NAME, "competition": "FIFA World Cup 2026",
            "source": provider.source, "last_updated": _now()}

    # Compact, prediction-first shape for the football page (table + featured).
    wc2026 = {
        "last_updated": meta["last_updated"], "competition": "Mundial 2026",
        "stage": preds[0]["stage"] if preds else "round_of_32",
        "matches": [{
            "match_id": p["match_id"], "home_team": p["home_team"], "away_team": p["away_team"],
            "stage": p["stage"], "kickoff": p.get("kickoff"), "kickoff_label": p.get("kickoff_label"),
            "prediction": {
                "home_win": p["result_90"].get("team1"), "draw": p["result_90"].get("draw"),
                "away_win": p["result_90"].get("team2"),
                "home_to_advance": (p.get("to_advance") or {}).get(p["home_team"]),
                "away_to_advance": (p.get("to_advance") or {}).get(p["away_team"]),
                "ai_pick": p["prediction_label"], "confidence": int(round(p["confidence"] * 100)),
            },
            "interest_score": p["interest_score"],
        } for p in preds],
    }

    return {
        "worldcup.json": {**meta, "headline": "World Cup — Biggest Games",
                          "count": len(preds), "matches": preds},
        "world-cup-2026.json": wc2026,
        "worldcup-predictions.json": {**meta, "matches": preds},
        "worldcup-live.json": {**meta, "matches": provider.fetch_live()},
        "worldcup-qualifiers.json": {**meta, "matches": qual_preds},
        "worldcup-fixtures.json": {**meta, **_fixtures_payload(provider)},
        "worldcup-standings.json": {**meta, "groups": provider.fetch_standings()},
        "worldcup-trending.json": {**meta, "region": "Worldwide",
                                   "matches": [
                                       {"rank": i + 1,
                                        "label": f"{p['home_team']} vs {p['away_team']}",
                                        "stage": p["stage"], "interest_score": p["interest_score"],
                                        "hot": i == 0}
                                       for i, p in enumerate(preds[:5])]},
    }


def publish_worldcup_json(data_dir: str | Path = DATA_DIR,
                          provider: WorldCupProvider | None = None) -> dict[str, Any]:
    data_dir = Path(data_dir)
    files = build_worldcup_json(provider)
    for name, payload in files.items():
        write_json(data_dir / name, payload)
    return {"files": list(files), "matches": files["worldcup.json"]["count"]}
