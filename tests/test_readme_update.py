import importlib.util
from pathlib import Path

SPEC = Path("scripts/update_readme.py")


def _load_module():
    spec = importlib.util.spec_from_file_location("update_readme", SPEC)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_top5_and_models_blocks_render():
    mod = _load_module()
    top5 = mod.top5_block()
    models = mod.models_block()
    assert "Match" in top5 and "Confidence" in top5
    assert "Algorithm" in models
    assert "football-hgb" in models


def test_replace_respects_markers():
    mod = _load_module()
    text = "a <!-- X:START -->old<!-- X:END --> b"
    out = mod._replace(text, "X", "NEW")
    assert "NEW" in out and "old" not in out
