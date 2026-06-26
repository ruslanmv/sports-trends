from sports_trends.inference.predict import predict_window
from sports_trends.models.predict import predict_matches


def test_prediction_placeholders_callable():
    assert predict_window() == []
    assert predict_matches() == []
