from sports_trends.inference.publish_json import build_season, publish_frontend_json


def test_build_season_has_featured_and_active():
    s = build_season()
    assert "featured" in s and "active" in s and "worldcup_active" in s


def test_publish_writes_season_json(tmp_path):
    summary = publish_frontend_json(tmp_path)
    assert "season.json" in summary["files"]
    assert (tmp_path / "season.json").exists()
