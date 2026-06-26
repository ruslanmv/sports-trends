from sports_trends.features.feature_pipeline import generate_features


def test_feature_pipeline_placeholder_callable():
    assert generate_features() == []
