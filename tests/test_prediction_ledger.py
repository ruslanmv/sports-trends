"""Tests for the prediction-ledger feedback loop (log → reconcile → learn)."""

import math

from sports_trends.datasets.build_prediction_dataset import (
    build_prediction_dataset, merge_training_rows,
)
from sports_trends.datasets.build_training_dataset import build_training_dataset
from sports_trends.datasets.leakage_checks import leakage_report
from sports_trends.datasets.prediction_ledger import (
    build_ledger_records, performance_report, reconcile,
)
from sports_trends.features.feature_pipeline import FEATURE_COLUMNS


def _prediction(match_id, home, away, probs, model_used=True, sport="football"):
    row = {c: 0 for c in FEATURE_COLUMNS}
    row.update({
        "match_id": match_id, "sport": sport, "league": "Test League",
        "home_team": home, "away_team": away, "match_date": "2026-03-01",
        "kickoff": "2026-03-01T18:00:00+00:00",
        "probabilities": probs, "model_used": model_used,
        "prediction_label": "AI: test",
    })
    return row


def test_build_ledger_records_snapshots_features_and_pick():
    preds = [_prediction("m1", "A", "B", {"home_win": 0.6, "draw": 0.25, "away_win": 0.15})]
    rows = build_ledger_records(preds, model_versions={"football": "2026.03.01"})
    r = rows[0]
    assert r["status"] == "open"
    assert r["predicted_class"] == "home_win" and r["predicted_pick"] == "home"
    assert r["model_version"] == "2026.03.01"
    assert r["confidence"] == 0.6
    assert r["prob_home_win"] == 0.6  # flattened probability columns
    # Feature snapshot is present for every feature column.
    assert all(c in r for c in FEATURE_COLUMNS)


def test_reconcile_scores_correct_prediction():
    preds = [_prediction("m1", "A", "B", {"home_win": 0.6, "draw": 0.25, "away_win": 0.15})]
    ledger = build_ledger_records(preds)
    results = [{"match_id": "m1", "sport": "football", "status": "finished",
                "home_score": 2, "away_score": 0}]
    out = reconcile(ledger, results)
    assert len(out["settled"]) == 1 and not out["still_open"]
    s = out["settled"][0]
    assert s["status"] == "settled"
    assert s["actual_class"] == "home_win"
    assert s["correct"] == 1
    assert s["prob_actual"] == 0.6
    assert math.isclose(s["log_loss"], -math.log(0.6), rel_tol=1e-6)
    # Brier = sum (p - y)^2 over classes
    expected_brier = (0.6 - 1) ** 2 + 0.25 ** 2 + 0.15 ** 2
    assert math.isclose(s["brier"], round(expected_brier, 6), rel_tol=1e-6)
    # Label columns are attached for the training pipeline.
    assert s["label_target"] == 0 and s["label_home_win"] == 1


def test_reconcile_marks_wrong_prediction_and_keeps_unfinished_open():
    preds = [
        _prediction("won", "A", "B", {"home_win": 0.2, "draw": 0.2, "away_win": 0.6}),
        _prediction("future", "C", "D", {"home_win": 0.5, "draw": 0.3, "away_win": 0.2}),
    ]
    ledger = build_ledger_records(preds)
    results = [{"match_id": "won", "sport": "football", "status": "finished",
                "home_score": 3, "away_score": 1}]  # home actually won -> pick away was wrong
    out = reconcile(ledger, results)
    assert len(out["settled"]) == 1 and len(out["still_open"]) == 1
    assert out["settled"][0]["correct"] == 0
    assert out["still_open"][0]["match_id"] == "future"
    assert out["still_open"][0]["status"] == "open"


def test_performance_report_splits_model_vs_heuristic():
    preds = [
        _prediction("a", "A", "B", {"home_win": 0.7, "draw": 0.2, "away_win": 0.1}, model_used=True),
        _prediction("b", "C", "D", {"home_win": 0.3, "draw": 0.3, "away_win": 0.4}, model_used=False),
    ]
    ledger = build_ledger_records(preds)
    results = [
        {"match_id": "a", "sport": "football", "status": "finished", "home_score": 2, "away_score": 0},
        {"match_id": "b", "sport": "football", "status": "finished", "home_score": 0, "away_score": 1},
    ]
    settled = reconcile(ledger, results)["settled"]
    rep = performance_report(settled)
    assert rep["overall"]["n"] == 2
    assert rep["overall"]["accuracy"] == 1.0  # both picks correct
    fb = rep["sports"]["football"]
    assert fb["model"]["n"] == 1 and fb["heuristic"]["n"] == 1
    assert fb["log_loss"] is not None
    assert isinstance(fb["calibration"], list)


def test_settled_rows_feed_leakage_safe_training_rows():
    preds = [_prediction("m1", "A", "B", {"home_win": 0.6, "draw": 0.25, "away_win": 0.15})]
    settled = reconcile(build_ledger_records(preds),
                        [{"match_id": "m1", "sport": "football", "status": "finished",
                          "home_score": 2, "away_score": 0}])["settled"]
    train_rows = build_prediction_dataset(settled, sport="football")
    assert len(train_rows) == 1
    row = train_rows[0]
    assert row["target"] == 0 and row["sport"] == "football"
    assert all(c in row for c in FEATURE_COLUMNS)
    # No leakage: label columns must not be feature columns.
    rep = leakage_report(train_rows, "football")
    assert rep["passed"], rep["errors"]


def test_merge_training_rows_prefers_settled_outcomes():
    history = [{"match_id": "m1", "sport": "football", "match_date": "2026-01-01", "target": 1}]
    settled_rows = [{"match_id": "m1", "sport": "football", "match_date": "2026-01-01", "target": 0}]
    merged = merge_training_rows(history, settled_rows)
    assert len(merged) == 1 and merged[0]["target"] == 0  # settled wins
