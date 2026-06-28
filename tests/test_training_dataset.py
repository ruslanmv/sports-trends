from sports_trends.datasets.build_training_dataset import build_training_dataset, time_split
from sports_trends.datasets.leakage_checks import leakage_report
from sports_trends.features.feature_pipeline import FEATURE_COLUMNS
from sports_trends.providers import _mock_data


def test_training_dataset_builds_with_labels():
    history = _mock_data.historical_results("football", 120)
    rows = build_training_dataset(history, "football")
    assert rows
    r = rows[0]
    assert "target" in r and "home_win" in r
    for col in FEATURE_COLUMNS:
        assert col in r


def test_leakage_report_passes_and_is_chronological():
    history = _mock_data.historical_results("basketball", 120)
    rows = build_training_dataset(history, "basketball")
    report = leakage_report(rows, "basketball")
    assert report["passed"]
    assert report["leakage_errors"] == 0
    assert report["chronological"]


def test_time_split_is_disjoint_and_ordered():
    history = _mock_data.historical_results("tennis", 100)
    rows = build_training_dataset(history, "tennis")
    splits = time_split(rows)
    assert len(splits["train"]) + len(splits["validation"]) + len(splits["test"]) == len(rows)
    if splits["train"] and splits["test"]:
        assert splits["train"][-1]["match_date"] <= splits["test"][0]["match_date"]
