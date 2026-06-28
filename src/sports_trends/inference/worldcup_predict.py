"""World Cup / international prediction: 90-minute result + to-advance layer."""

from __future__ import annotations

import math
from typing import Any

from ..features.international_features import international_features, national_elo
from ..features.tournament_stage import is_knockout, stage_importance

ELO_90_SCALE = 280.0       # 90-minute result spread
ADVANCE_SCALE = 220.0      # includes extra time / penalties
QUALIFY_SCALE = 240.0


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-40.0, min(40.0, x))))


def _result_90(elo_diff: float) -> dict[str, float]:
    p_home_raw = _logistic(elo_diff / ELO_90_SCALE)
    draw = 0.28 * (1.0 - abs(2 * p_home_raw - 1.0))
    home = p_home_raw * (1 - draw)
    away = (1 - p_home_raw) * (1 - draw)
    total = home + draw + away
    return {"team1": round(home / total, 3), "draw": round(draw / total, 3), "team2": round(away / total, 3)}


def _viral_score(home: str, away: str, stage: str) -> int:
    fame = (national_elo(home) + national_elo(away) - 3400) / 8.0   # ~0-100 from strength
    return int(max(40, min(100, 0.6 * fame + 0.4 * stage_importance(stage))))


def predict_worldcup_match(match: dict[str, Any]) -> dict[str, Any]:
    feats = international_features(match)
    home = match.get("home", match.get("home_team", ""))
    away = match.get("away", match.get("away_team", ""))
    stage = feats["stage"]
    diff = feats["elo_diff"]

    result = _result_90(diff)
    top = max(result, key=result.get)
    pick_team = home if top == "team1" else (away if top == "team2" else "Draw")
    label = f"{pick_team} favoured" if top != "draw" else "Even — draw likely in 90'"

    out: dict[str, Any] = {
        "match_id": match.get("id", match.get("match_id")),
        "competition_type": match.get("competition_type", "world_cup"),
        "stage": stage,
        "group": match.get("group", ""),
        "home_team": home, "away_team": away,
        "kickoff": match.get("kickoff"),
        "neutral_venue": feats["neutral_venue"],
        "host_advantage": feats["host_advantage"],
        "result_90": result,
        "prediction_label": label,
        "confidence": round(max(result.values()), 3),
        "interest_score": _viral_score(home, away, stage),
        "explanation": [
            f"Elo: {home} {feats['home_elo']:.0f} vs {away} {feats['away_elo']:.0f} "
            f"(Δ {diff:+.0f}{', host advantage' if feats['host_advantage'] and not feats['neutral_venue'] else ''}).",
            f"Stage importance {feats['stage_importance']}/100 ({stage.replace('_',' ')}).",
        ],
    }

    if is_knockout(stage):
        adv = _logistic(diff / ADVANCE_SCALE)
        out["to_advance"] = {home: round(adv, 3), away: round(1 - adv, 3)}
        out["explanation"].append(
            f"To advance (incl. extra time / penalties): {home} {adv*100:.0f}% · {away} {(1-adv)*100:.0f}%."
        )
    elif match.get("competition_type") == "world_cup_qualifier" or stage in ("qualifying_group", "playoff"):
        q_home = max(0.05, min(0.95, _logistic(diff / QUALIFY_SCALE)))
        out["qualification"] = {
            "win_draw_loss": result,
            "group_qualification_probability": {home: round(q_home, 3), away: round(1 - q_home, 3)},
            "elimination_risk": {home: round(1 - q_home, 3), away: round(q_home, 3)},
        }
        out["explanation"].append(
            f"Group qualification odds: {home} {q_home*100:.0f}% · {away} {(1-q_home)*100:.0f}%."
        )
    return out


def predict_many(matches: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    return [predict_worldcup_match(m) for m in (matches or [])]
