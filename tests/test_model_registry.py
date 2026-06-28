from sports_trends.models._train_core import train_sport
from sports_trends.models.registry import ModelRegistry


def test_train_and_dry_run_publish(tmp_path):
    reg = ModelRegistry(dry_run=True, local_dir=tmp_path)
    assert reg.mode == "dry-run"
    res = train_sport("football", publish=True, registry=reg, out_dir=tmp_path / "build")
    assert res["metrics"]["accuracy"] >= 0.0
    # Artifacts mirrored into <sport>/latest/ and registry updated.
    assert (tmp_path / "football" / "latest" / "model.pkl").exists()
    assert (tmp_path / "registry" / "latest_versions.json").exists()
