from sports_trends.inference.build_window import build_inference_window
from sports_trends.inference.predict import predict_window
from sports_trends.inference.publish_json import publish_frontend_json
from sports_trends.providers import _mock_data
from sports_trends.providers.fallback_provider import FallbackProvider


def _history():
    rows = []
    for s in ("football", "basketball", "tennis", "cricket"):
        rows += _mock_data.historical_results(s, 200)
    return rows


def test_prediction_placeholders_callable():
    assert predict_window() == []
    assert build_inference_window() == []


def test_inference_window_has_model_input_columns():
    window = build_inference_window(FallbackProvider().fetch_tomorrow_matches(), _history())
    assert window
    row = window[0]
    for col in ("match_id", "elo_diff", "home_form_last_5", "model_input_version"):
        assert col in row


def test_predict_window_outputs_probabilities_and_explanation():
    window = build_inference_window(FallbackProvider().fetch_tomorrow_matches(), _history())
    preds = predict_window(window)
    assert len(preds) == len(window)
    for p in preds:
        assert abs(sum(p["probabilities"].values()) - 1.0) < 1e-6
        assert 0.0 <= p["confidence"] <= 1.0
        assert p["explanation"] and p["prediction_label"]


def test_publish_frontend_json_writes_all_files(tmp_path):
    summary = publish_frontend_json(tmp_path)
    assert summary["tomorrow_matches"] >= 4
    for name in ("status.json", "live.json", "today.json", "tomorrow.json",
                 "predictions.json", "trending.json", "rankings.json"):
        assert (tmp_path / name).exists()
