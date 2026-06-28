from sports_trends.ingestion.fetch_raw_data import fetch_raw_data


def test_fetch_raw_data_all_windows():
    data = fetch_raw_data("all")
    assert set(data) == {"today", "tomorrow", "live", "finished"}
    assert len(data["tomorrow"]) >= 4
    assert all(isinstance(r, dict) for r in data["tomorrow"])


def test_fetch_raw_data_live_window():
    data = fetch_raw_data("live")
    assert data["live"] and not data["tomorrow"]
