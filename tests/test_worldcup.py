from datetime import date

from sports_trends.features.tournament_stage import (
    current_stage_for_date, is_knockout, normalize_stage, stage_importance,
)
from sports_trends.inference.worldcup_predict import predict_worldcup_match
from sports_trends.inference.worldcup_publish import build_worldcup_json
from sports_trends.providers.openfootball_worldcup_provider import _is_placeholder, _kickoff
from sports_trends.providers.worldcup_provider import WorldCupProvider, compute_standings


def test_stage_normalization_and_order():
    assert normalize_stage("Round of 16") == "round_of_16"
    assert normalize_stage("Quarter-finals") == "quarterfinals"
    assert normalize_stage("Matchday 1") == "group_stage"
    assert is_knockout("final") and not is_knockout("group_stage")
    assert stage_importance("final") > stage_importance("group_stage")


def test_current_stage_for_2026_calendar():
    assert current_stage_for_date(date(2026, 6, 20)) == "group_stage"
    assert current_stage_for_date(date(2026, 6, 28)) == "round_of_32"
    assert current_stage_for_date(date(2026, 7, 19)) == "final"


def test_offline_provider_falls_back_to_mock():
    p = WorldCupProvider(allow_network=False)
    up = p.fetch_upcoming()
    assert up and all(m["competition_type"] == "world_cup" for m in up)
    assert p.fetch_qualifiers() and p.fetch_standings()


def test_knockout_prediction_has_90min_and_to_advance():
    p = WorldCupProvider(allow_network=False)
    match = p.fetch_upcoming()[0]
    pred = predict_worldcup_match(match)
    probs = pred["result_90"]
    assert abs(sum(probs.values()) - 1.0) < 1e-6
    assert set(pred["to_advance"]) == {match["home"], match["away"]}
    assert abs(sum(pred["to_advance"].values()) - 1.0) < 1e-6
    assert pred["explanation"]


def test_qualifier_prediction_has_group_probability():
    p = WorldCupProvider(allow_network=False)
    q = predict_worldcup_match(p.fetch_qualifiers()[0])
    assert "qualification" in q
    gqp = q["qualification"]["group_qualification_probability"]
    assert abs(sum(gqp.values()) - 1.0) < 1e-6


def test_publish_builds_all_worldcup_files():
    files = build_worldcup_json(WorldCupProvider(allow_network=False))
    for name in ("worldcup.json", "worldcup-predictions.json", "worldcup-live.json",
                 "worldcup-qualifiers.json", "worldcup-fixtures.json",
                 "worldcup-standings.json", "worldcup-trending.json"):
        assert name in files
    assert files["worldcup.json"]["matches"]


def test_openfootball_kickoff_parses_local_utc_offset():
    # "17:00 UTC-4" is 21:00 UTC; bare "HH:MM" stays as given.
    assert _kickoff("2026-06-29", "17:00 UTC-4") == "2026-06-29T21:00:00+00:00"
    assert _kickoff("2026-06-11", "20:00 UTC-6") == "2026-06-12T02:00:00+00:00"
    assert _kickoff("2026-07-19", "15:00").endswith("T15:00:00+00:00")
    assert _kickoff("", "17:00 UTC-4") is None


def test_knockout_placeholder_detection():
    for code in ("W74", "L101", "RU2", "1A", "2B", "Winner Group A", "Runner-up B"):
        assert _is_placeholder(code), code
    for real in ("Argentina", "South Korea", "Côte d'Ivoire", "USA"):
        assert not _is_placeholder(real), real


def test_compute_standings_from_results():
    finished = [
        {"home": "Brazil", "away": "Serbia", "group": "G",
         "home_score": 2, "away_score": 0, "status": "finished"},
        {"home": "Brazil", "away": "Switzerland", "group": "G",
         "home_score": 1, "away_score": 1, "status": "finished"},
    ]
    table = compute_standings(finished)
    assert "G" in table
    brazil = next(r for r in table["G"] if r["team"] == "Brazil")
    assert brazil["points"] == 4 and brazil["played"] == 2 and brazil["gd"] == 2
    # Leader sorts first.
    assert table["G"][0]["team"] == "Brazil"


def test_fetch_fixtures_offline_returns_schedule():
    p = WorldCupProvider(allow_network=False)
    fixtures = p.fetch_fixtures()
    assert fixtures and all("home" in m for m in fixtures)
