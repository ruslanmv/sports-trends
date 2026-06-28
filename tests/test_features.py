from sports_trends.features.feature_pipeline import FEATURE_COLUMNS, generate_features
from sports_trends.ingestion.normalize_matches import normalize_matches
from sports_trends.providers import _mock_data
from sports_trends.providers.fallback_provider import FallbackProvider
from sports_trends.providers.football_provider import FootballProvider


def _history():
    rows = []
    for sport in ("football", "basketball", "tennis", "cricket"):
        rows.extend(_mock_data.historical_results(sport))
    return rows


def test_generate_features_empty():
    assert generate_features() == []


def test_feature_rows_have_all_columns():
    fixtures = normalize_matches(FallbackProvider().fetch_tomorrow_matches(), "fallback")
    rows = generate_features(fixtures, _history())
    assert len(rows) == len(fixtures)
    for col in FEATURE_COLUMNS:
        assert col in rows[0], f"missing feature column {col}"


def test_features_have_no_future_leakage():
    # No history at/after the fixture date should ever be consumed: Elo must
    # equal the base rating delta only from strictly-earlier matches. We assert
    # the pipeline ignores a planted "future blowout" for the same teams.
    fixtures = normalize_matches(FootballProvider().fetch_tomorrow_matches(), "fallback")
    fx = fixtures[0]
    poisoned = _history() + [{
        "sport": "football", "home": fx["home_team"], "away": fx["away_team"],
        "home_score": 99, "away_score": 0, "date": "2999-01-01",
    }]
    base = generate_features([fx], _history())[0]
    with_future = generate_features([fx], poisoned)[0]
    assert base["home_elo"] == with_future["home_elo"]
