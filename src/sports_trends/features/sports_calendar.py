"""Year-round sports/tournament calendar.

Knows which major competitions are *in season* on any given date so the portal
stays relevant all year — World Cup in summer of a WC year, club leagues
Aug–May, the four tennis Slams across the year, NBA Oct–Jun, IPL in spring, and
so on. When one tournament ends, ``featured_competition`` automatically rolls
over to the next most important active competition.

Windows use (month, day) tuples and support wrap-around (e.g. Aug 1 → May 31).
One-off events (World Cup, Euros, Copa América, AFCON, T20 WC) are pinned to the
years they occur; everything else recurs annually.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Optional

MD = tuple[int, int]


@dataclass(frozen=True)
class Tournament:
    key: str
    name: str
    sport: str
    scope: str            # "club" | "international" | "grand_slam" | "franchise"
    importance: int       # 0-100
    start: MD
    end: MD
    years: Optional[frozenset[int]] = None  # None = recurs every year
    emoji: str = "🏆"

    def _in_window(self, d: date) -> bool:
        md = (d.month, d.day)
        if self.start <= self.end:
            return self.start <= md <= self.end
        # wrap-around window (season spans New Year)
        return md >= self.start or md <= self.end

    def is_active(self, d: date) -> bool:
        if self.years is not None and d.year not in self.years:
            return False
        return self._in_window(d)

    def next_start(self, d: date) -> Optional[date]:
        """Next calendar date this tournament begins, on/after ``d``."""
        years = sorted(self.years) if self.years is not None else [d.year, d.year + 1]
        for y in years:
            try:
                start = date(y, self.start[0], self.start[1])
            except ValueError:
                continue
            if start >= d:
                return start
        return None


# --- The calendar -----------------------------------------------------------
CALENDAR: list[Tournament] = [
    # Soccer — club
    Tournament("epl", "Premier League", "football", "club", 90, (8, 10), (5, 25), emoji="🏴"),
    Tournament("laliga", "La Liga", "football", "club", 88, (8, 15), (5, 25), emoji="🇪🇸"),
    Tournament("seriea", "Serie A", "football", "club", 87, (8, 18), (5, 26), emoji="🇮🇹"),
    Tournament("bundesliga", "Bundesliga", "football", "club", 86, (8, 22), (5, 18), emoji="🇩🇪"),
    Tournament("ligue1", "Ligue 1", "football", "club", 84, (8, 15), (5, 18), emoji="🇫🇷"),
    Tournament("ucl", "UEFA Champions League", "football", "club", 96, (9, 15), (5, 31), emoji="⭐"),
    # Soccer — international (one-off / cyclical)
    Tournament("worldcup", "FIFA World Cup", "football", "international", 100, (6, 11), (7, 19),
               years=frozenset({2026}), emoji="🏆"),
    Tournament("worldcup_q", "World Cup Qualifiers", "football", "international", 80, (3, 1), (11, 30),
               years=frozenset({2024, 2025, 2027, 2028, 2029}), emoji="🌍"),
    Tournament("euro", "UEFA Euro", "football", "international", 97, (6, 12), (7, 14),
               years=frozenset({2028, 2032}), emoji="🇪🇺"),
    Tournament("copa", "Copa América", "football", "international", 90, (6, 10), (7, 14),
               years=frozenset({2028}), emoji="🌎"),
    Tournament("afcon", "Africa Cup of Nations", "football", "international", 84, (12, 21), (1, 18),
               years=frozenset({2025, 2027}), emoji="🌍"),
    # Basketball
    Tournament("nba", "NBA", "basketball", "franchise", 90, (10, 21), (6, 22), emoji="🏀"),
    Tournament("euroleague", "EuroLeague", "basketball", "franchise", 80, (10, 1), (5, 26), emoji="🏀"),
    # Tennis — Grand Slams
    Tournament("ausopen", "Australian Open", "tennis", "grand_slam", 92, (1, 8), (1, 28), emoji="🎾"),
    Tournament("rolandgarros", "Roland Garros", "tennis", "grand_slam", 93, (5, 19), (6, 9), emoji="🎾"),
    Tournament("wimbledon", "Wimbledon", "tennis", "grand_slam", 95, (6, 24), (7, 14), emoji="🎾"),
    Tournament("usopen", "US Open", "tennis", "grand_slam", 92, (8, 25), (9, 8), emoji="🎾"),
    # Cricket
    Tournament("ipl", "Indian Premier League", "cricket", "franchise", 86, (3, 22), (5, 28), emoji="🏏"),
    Tournament("t20wc", "ICC T20 World Cup", "cricket", "international", 88, (6, 1), (6, 30),
               years=frozenset({2026, 2028}), emoji="🏏"),
    # Baseball
    Tournament("mlb", "MLB", "baseball", "franchise", 78, (3, 28), (10, 5), emoji="⚾"),
    # Esports (year-round majors)
    Tournament("esports", "Esports Majors", "esports", "franchise", 62, (1, 1), (12, 31), emoji="🎮"),
]

_BY_KEY = {t.key: t for t in CALENDAR}


def _row(t: Tournament) -> dict[str, Any]:
    return {"key": t.key, "name": t.name, "sport": t.sport, "scope": t.scope,
            "importance": t.importance, "emoji": t.emoji}


def active_tournaments(d: Optional[date] = None) -> list[dict[str, Any]]:
    d = d or date.today()
    rows = [_row(t) for t in CALENDAR if t.is_active(d)]
    return sorted(rows, key=lambda r: r["importance"], reverse=True)


def featured_competition(d: Optional[date] = None) -> dict[str, Any]:
    act = active_tournaments(d)
    return act[0] if act else _row(_BY_KEY["epl"])


def worldcup_active(d: Optional[date] = None) -> bool:
    d = d or date.today()
    return _BY_KEY["worldcup"].is_active(d) or _BY_KEY["worldcup_q"].is_active(d)


def upcoming_tournaments(d: Optional[date] = None, within_days: int = 60) -> list[dict[str, Any]]:
    d = d or date.today()
    out = []
    for t in CALENDAR:
        if t.is_active(d):
            continue
        nxt = t.next_start(d)
        if nxt and 0 <= (nxt - d).days <= within_days:
            out.append({**_row(t), "start": nxt.isoformat(), "starts_in_days": (nxt - d).days})
    return sorted(out, key=lambda r: r["starts_in_days"])


def season_context(d: Optional[date] = None) -> dict[str, Any]:
    d = d or date.today()
    return {
        "today": d.isoformat(),
        "featured": featured_competition(d),
        "worldcup_active": worldcup_active(d),
        "active": active_tournaments(d),
        "upcoming": upcoming_tournaments(d),
    }
