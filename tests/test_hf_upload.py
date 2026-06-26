from sports_trends.hf.manifest import build_manifest


def test_manifest_placeholder_callable():
    assert build_manifest() == []
