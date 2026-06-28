from sports_trends.ingestion.canonical import validate_match
from sports_trends.ingestion.normalize_matches import (
    CANONICAL_FIELDS,
    find_duplicate_ids,
    make_match_id,
    normalize_match,
    normalize_matches,
)
from sports_trends.providers.fallback_provider import FallbackProvider


def test_normalize_match_minimum_fields():
    out = normalize_match({"id": "1", "home": "A", "away": "B"}, "demo")
    assert out["provider"] == "demo"
    assert out["home_team"] == "A"
    assert out["away_team"] == "B"
    assert set(CANONICAL_FIELDS).issubset(out.keys())


def test_match_id_is_stable_and_deterministic():
    a = make_match_id("football", "EPL", "Arsenal", "Spurs", "2026-06-27")
    b = make_match_id("football", "EPL", "Arsenal", "Spurs", "2026-06-27")
    assert a == b == "football-epl-arsenal-spurs-2026-06-27"


def test_dedup_detects_duplicate_ids():
    rows = [{"id": "x", "home": "A", "away": "B"}, {"id": "x", "home": "A", "away": "B"}]
    normalized = [normalize_match(r, "demo") for r in rows]
    assert find_duplicate_ids(normalized) == ["x"]
    assert len(normalize_matches(rows, "demo")) == 1


def test_fallback_data_validates_against_canonical_model():
    for raw in FallbackProvider().fetch_tomorrow_matches():
        validate_match(normalize_match(raw, "fallback"))
