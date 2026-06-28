"""Head-to-head record between two teams before a given date."""

from __future__ import annotations

from typing import Any


def head_to_head(history: list[dict[str, Any]], home: str, away: str, as_of: str | None = None) -> dict[str, int]:
    h2h_home = h2h_draw = h2h_away = 0
    for m in history:
        day = str(m.get("date") or m.get("match_date") or "")
        if as_of is not None and day >= as_of:
            continue
        mh = m.get("home_team") or m.get("home")
        ma = m.get("away_team") or m.get("away")
        if {mh, ma} != {home, away}:
            continue
        try:
            hs, as_ = float(m.get("home_score")), float(m.get("away_score"))
        except (TypeError, ValueError):
            continue
        winner = mh if hs > as_ else (ma if as_ > hs else None)
        if winner is None:
            h2h_draw += 1
        elif winner == home:
            h2h_home += 1
        else:
            h2h_away += 1
    return {"h2h_home_wins": h2h_home, "h2h_draws": h2h_draw, "h2h_away_wins": h2h_away}
