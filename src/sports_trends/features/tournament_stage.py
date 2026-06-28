"""Tournament-stage helpers for international / World Cup matches."""

from __future__ import annotations

from datetime import date
from typing import Any

# Canonical stage order (qualifiers -> final).
STAGE_ORDER = [
    "qualifying_group", "playoff", "group_stage",
    "round_of_32", "round_of_16", "quarterfinals", "semifinals", "third_place", "final",
]

# Importance score (0-100) used as a feature and for ranking.
STAGE_IMPORTANCE = {
    "qualifying_group": 55, "playoff": 70, "group_stage": 75,
    "round_of_32": 82, "round_of_16": 86, "quarterfinals": 90,
    "semifinals": 95, "third_place": 80, "final": 100,
}

KNOCKOUT_STAGES = {"round_of_32", "round_of_16", "quarterfinals", "semifinals", "third_place", "final"}

# Rough confederation strength multipliers (UEFA/CONMEBOL strongest).
CONFEDERATION_STRENGTH = {
    "UEFA": 1.0, "CONMEBOL": 0.97, "CONCACAF": 0.80,
    "CAF": 0.82, "AFC": 0.78, "OFC": 0.60, "INTERNATIONAL": 0.9,
}


def normalize_stage(raw_round: str | None) -> str:
    r = (raw_round or "").strip().lower()
    if "final" == r or r == "final":
        return "final"
    if "third" in r:
        return "third_place"
    if "semi" in r:
        return "semifinals"
    if "quarter" in r:
        return "quarterfinals"
    if "round of 16" in r or "1/8" in r:
        return "round_of_16"
    if "round of 32" in r:
        return "round_of_32"
    if "playoff" in r or "play-off" in r:
        return "playoff"
    if "qualif" in r:
        return "qualifying_group"
    return "group_stage"


def stage_importance(stage: str) -> int:
    return STAGE_IMPORTANCE.get(stage, 75)


def is_knockout(stage: str) -> bool:
    return stage in KNOCKOUT_STAGES


def confederation_strength(confed: str | None) -> float:
    return CONFEDERATION_STRENGTH.get((confed or "INTERNATIONAL").upper(), 0.85)


def current_stage_for_date(d: date | None = None) -> str:
    """Best-effort 2026 World Cup stage from a calendar date (group->final)."""
    d = d or date.today()
    md = (d.month, d.day)
    if md < (6, 11):
        return "qualifying_group"
    if md <= (6, 27):
        return "group_stage"
    if md <= (7, 3):
        return "round_of_32"
    if md <= (7, 7):
        return "round_of_16"
    if md <= (7, 11):
        return "quarterfinals"
    if md <= (7, 16):
        return "semifinals"
    return "final"  # Final: 19 July 2026
