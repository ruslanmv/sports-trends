from ruslan_sports.predictions.generate_predictions import generate_predictions


def test_generate_predictions_preserves_matches():
    rows = generate_predictions([{"id": "m1"}])
    assert rows[0]["id"] == "m1"
    assert "prediction" in rows[0]
