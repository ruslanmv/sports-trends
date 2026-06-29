"""Generate the small public JSON files the website consumes.

This is the single place that turns provider data + model predictions into the
``assets/data/sports/*.json`` files. Everything works offline with mock data and
matches the public reference dashboard.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..config import (
    DATA_DIR, HEADLINE, HF_DATASET_REPO, HF_MODEL_REPO, PRODUCT_NAME,
    SITE_BASE_URL, TAGLINE, TECHNICAL_NAME, UPDATE_CYCLE_MINUTES,
)
from ..features.sports_calendar import season_context
from ..providers import _mock_data, provider_health_report
from ..providers.fallback_provider import FallbackProvider
from ..ranking.rank_top_matches import rank_top_matches
from ..storage.write_json import write_json
from .build_window import build_inference_window
from .predict import predict_window


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _kickoff_label(iso: str | None) -> str:
    if not iso:
        return "TBD"
    try:
        dt = datetime.fromisoformat(iso)
        return dt.strftime("%H:%M")
    except ValueError:
        return "TBD"


def _pick_from_probs(probs: dict[str, float], home: str, away: str) -> tuple[str, float]:
    """Derive the AI pick label and confidence from the displayed probabilities."""
    top = max(probs, key=probs.get)
    confidence = round(float(probs[top]), 3)
    if top == "draw":
        return "AI: draw likely", confidence
    team = home if top in ("home_win", "player_1_win") else away
    return f"AI: {team} favoured", confidence


def _history() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for sport in ("football", "basketball", "tennis", "cricket"):
        rows.extend(_mock_data.historical_results(sport, n_matches=200))
    return rows


def build_season() -> dict[str, Any]:
    """What's in season right now — drives the season-aware UI + README."""
    return {"product": PRODUCT_NAME, "last_updated": _now(), **season_context()}


def build_football_config() -> dict[str, Any]:
    """Seasonal mode for the football page — flips to Mundial 2026 automatically."""
    ctx = season_context()
    wc = bool(ctx.get("worldcup_active"))
    ff = ctx.get("featured_football") or {}
    ff_name = ff.get("name", "Football")
    ff_active = ff.get("status") == "active"
    # Off the World Cup, the soccer surface rolls over to the top football event
    # (UCL, a top league, …) — named so the page always leads with a real
    # marquee competition instead of a generic label.
    club_eyebrow = f"{ff_name} Intelligence" if ff_name != "Football" else "Football Intelligence"
    if ff_active:
        club_headline = f"{ff.get('emoji', '⚽')} {ff_name} — Tomorrow’s Biggest Matches"
    else:
        days = ff.get("starts_in_days")
        club_headline = (f"{ff_name} starts in {days}d — Tomorrow’s Biggest Football Matches"
                         if days is not None else "Tomorrow’s Biggest Football Matches")
    return {
        "last_updated": _now(),
        "page_mode": "world_cup_2026" if wc else "club_season",
        "default_tab": "Mundial 2026" if wc else "All",
        "eyebrow": "Mundial 2026 Intelligence" if wc else club_eyebrow,
        "headline": "Who Advances Tomorrow?" if wc else club_headline,
        "subtitle": (
            "AI predictions, to-advance probabilities, and match insights for the World Cup."
            if wc else "AI predictions for the most important upcoming matches."
        ),
        "show_world_cup_strip": wc,
        "featured_football": ff,
        "primary_prediction_type": "to_advance" if wc else "match_result",
    }


def build_status() -> dict[str, Any]:
    return {
        "product": PRODUCT_NAME,
        "technical_name": TECHNICAL_NAME,
        "status": "live",
        "last_updated": _now(),
        "update_cycle_minutes": UPDATE_CYCLE_MINUTES,
        "dataset_repo": HF_DATASET_REPO,
        "model_repo": HF_MODEL_REPO,
        "website_url": SITE_BASE_URL,
        "stats": _mock_data.DASHBOARD_STATS,
        "providers": provider_health_report(),
    }


def _normalize_live(raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in raw:
        out.append({
            "match_id": r.get("id"),
            "sport": r["sport"],
            "league": r.get("league"),
            "home_team": r.get("home"),
            "away_team": r.get("away"),
            "home_score": r.get("home_score"),
            "away_score": r.get("away_score"),
            "status": r.get("status"),
            "status_detail": r.get("status_detail"),
            "is_live": r.get("status") == "live",
            "is_finished": r.get("status") == "finished",
        })
    return out


def build_live() -> dict[str, Any]:
    raw = FallbackProvider().fetch_live_results() + FallbackProvider().fetch_finished_results()
    matches = _normalize_live(raw)
    return {"last_updated": _now(), "count": len(matches), "matches": matches}


def build_today() -> dict[str, Any]:
    matches = _normalize_live(FallbackProvider().fetch_today_matches())
    return {"date": datetime.now(timezone.utc).date().isoformat(),
            "last_updated": _now(), "count": len(matches), "matches": matches}


def _predicted_matches() -> list[dict[str, Any]]:
    raw = FallbackProvider().fetch_tomorrow_matches()
    raw_by_id = {r["id"]: r for r in raw}
    window = build_inference_window(raw, _history())
    predictions = predict_window(window)

    cards = []
    for pred in predictions:
        raw_fx = raw_by_id.get(pred["match_id"], {})
        # Prefer curated win_prob from the fixture for display; else model probs.
        curated = raw_fx.get("win_prob")
        probs = (
            {"home_win": curated["home"], "draw": curated["draw"], "away_win": curated["away"]}
            if curated else pred["probabilities"]
        )
        # Pick + confidence must agree with the probabilities actually shown.
        label, confidence = _pick_from_probs(probs, pred["home_team"], pred["away_team"])
        cards.append({
            "match_id": pred["match_id"],
            "sport": pred["sport"],
            "league": pred["league"],
            "home_team": pred["home_team"],
            "away_team": pred["away_team"],
            "kickoff": pred.get("kickoff"),
            "kickoff_label": _kickoff_label(pred.get("kickoff")),
            "probabilities": {k: round(float(v), 3) for k, v in probs.items()},
            "prediction_label": label,
            "confidence": confidence,
            "interest_score": raw_fx.get("interest_score", 50),
            "trend_badge": raw_fx.get("trend_badge"),
            "audience": raw_fx.get("audience"),
            "model_used": pred.get("model_used", False),
            "explanation": pred["explanation"],
        })
    return rank_top_matches(cards)


def build_tomorrow(cards: list[dict[str, Any]]) -> dict[str, Any]:
    return {"date": (datetime.now(timezone.utc).date()).isoformat(),
            "headline": HEADLINE, "tagline": TAGLINE, "last_updated": _now(),
            "count": len(cards), "matches": cards}


def build_predictions(cards: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "product": PRODUCT_NAME, "technical_name": TECHNICAL_NAME,
        "last_updated": _now(), "source": HF_DATASET_REPO,
        "model_version": "baseline-v1", "headline": HEADLINE, "tagline": TAGLINE,
        "matches": cards,
    }


def _audience_num(value: Any) -> float:
    s = str(value or "0").upper().strip()
    mult = 1_000_000 if s.endswith("M") else (1_000 if s.endswith("K") else 1)
    try:
        return float(s.rstrip("MK")) * mult
    except ValueError:
        return 0.0


def build_trending(cards: list[dict[str, Any]]) -> dict[str, Any]:
    ranked = sorted(cards, key=lambda c: _audience_num(c.get("audience")), reverse=True)
    rows = [{
        "rank": i + 1,
        "label": f"{c['home_team']} vs {c['away_team']}",
        "sport": c["sport"],
        "audience": c.get("audience"),
        "hot": i == 0,
    } for i, c in enumerate(ranked)]
    return {"region": "Worldwide", "last_updated": _now(), "count": len(rows), "matches": rows}


def build_rankings(cards: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "last_updated": _now(),
        "explore_sports": _mock_data.EXPLORE_SPORTS,
        "top_matches": [
            {"rank": i + 1, "match_id": c["match_id"],
             "label": f"{c['home_team']} vs {c['away_team']}",
             "interest_score": c["interest_score"]}
            for i, c in enumerate(cards)
        ],
    }


def publish_frontend_json(data_dir: str | Path = DATA_DIR) -> dict[str, Any]:
    """Write all seven public JSON files and return a summary."""
    data_dir = Path(data_dir)
    cards = _predicted_matches()

    files = {
        "season.json": build_season(),
        "football-config.json": build_football_config(),
        "status.json": build_status(),
        "live.json": build_live(),
        "today.json": build_today(),
        "tomorrow.json": build_tomorrow(cards),
        "predictions.json": build_predictions(cards),
        "trending.json": build_trending(cards),
        "rankings.json": build_rankings(cards),
    }
    for name, payload in files.items():
        write_json(data_dir / name, payload)
    return {"data_dir": str(data_dir), "files": list(files), "tomorrow_matches": len(cards)}
