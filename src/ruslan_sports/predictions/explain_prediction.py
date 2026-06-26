from typing import Any


def explain_prediction(match: dict[str, Any]) -> str:
    """TODO: Generate human-readable prediction explanation."""
    prediction = match.get("prediction", {})
    return prediction.get("label", "Prediction explanation pending.")
