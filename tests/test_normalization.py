from sports_trends.ingestion.normalize_matches import normalize_match


def test_normalize_match_minimum_fields():
    out = normalize_match({"id": "1", "home": "A", "away": "B"}, "demo")
    assert out["provider"] == "demo"
    assert out["home_team"] == "A"
    assert out["away_team"] == "B"
