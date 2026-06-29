from datetime import date

from sports_trends.features.sports_calendar import (
    active_tournaments, featured_competition, featured_football_competition,
    season_context, upcoming_tournaments, worldcup_active,
)

FOOTBALL_KEYS = {"worldcup", "worldcup_q", "ucl", "epl", "laliga", "seriea",
                 "bundesliga", "ligue1", "euro", "copa", "afcon"}


def test_worldcup_featured_in_summer_2026():
    d = date(2026, 6, 28)
    assert worldcup_active(d)
    assert featured_competition(d)["key"] == "worldcup"


def test_rolls_over_to_club_season_after_world_cup():
    d = date(2026, 9, 15)
    assert not worldcup_active(d)
    feat = featured_competition(d)
    assert feat["key"] in {"ucl", "epl"}  # club football takes over
    names = {t["name"] for t in active_tournaments(d)}
    assert "Premier League" in names


def test_january_has_australian_open_and_nba():
    names = {t["name"] for t in active_tournaments(date(2027, 1, 20))}
    assert "Australian Open" in names and "NBA" in names


def test_season_context_shape_and_upcoming():
    s = season_context(date(2026, 6, 28))
    assert s["featured"] and "active" in s and "upcoming" in s
    up = upcoming_tournaments(date(2026, 7, 5), within_days=60)
    assert any("Premier League" == u["name"] for u in up)


def test_season_is_never_empty_any_month():
    # Year-round coverage: every month has at least one active competition.
    for month in range(1, 13):
        assert active_tournaments(date(2026, month, 15)), f"no tournament active in month {month}"


def test_world_cup_is_featured_football_during_tournament():
    ff = featured_football_competition(date(2026, 6, 28))
    assert ff["key"] == "worldcup" and ff["status"] == "active"


def test_featured_football_rolls_to_soccer_in_post_world_cup_gap():
    # Day after the final there is NO football active (club leagues start later),
    # yet the soccer surface must still headline a football event (not MLB).
    gap = date(2026, 7, 22)
    assert not worldcup_active(gap)
    # Cross-sport featured can be a non-football event in the gap...
    assert featured_competition(gap)["sport"] != "football"
    # ...but the football surface always stays on football.
    ff = featured_football_competition(gap)
    assert ff["sport"] == "football"
    assert ff["key"] in FOOTBALL_KEYS
    assert ff["status"] == "upcoming" and ff["starts_in_days"] >= 0


def test_featured_football_is_football_every_month():
    for month in range(1, 13):
        ff = featured_football_competition(date(2026, month, 15))
        assert ff["sport"] == "football", f"month {month} -> {ff}"


def test_season_context_includes_featured_football():
    s = season_context(date(2026, 8, 1))
    assert s["featured_football"]["sport"] == "football"
