from datetime import date

from sports_trends.features.tournament_stage import (
    current_stage_for_date, is_knockout, normalize_stage, stage_importance,
)
from sports_trends.inference.worldcup_predict import predict_worldcup_match
from sports_trends.inference.worldcup_publish import build_worldcup_json
from sports_trends.providers.worldcup_provider import WorldCupProvider


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
                 "worldcup-qualifiers.json", "worldcup-standings.json", "worldcup-trending.json"):
        assert name in files
    assert files["worldcup.json"]["matches"]
