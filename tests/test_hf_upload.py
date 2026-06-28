from sports_trends.hf.dataset_client import DatasetClient
from sports_trends.hf.manifest import build_manifest
from sports_trends.hf.upload import upload_partition


def test_manifest_has_required_keys():
    m = build_manifest(duplicates=0, schema_errors=0, leakage_errors=0)
    assert m["dataset_name"] == "ruslanmv/sports-trends-dataset"
    assert m["quality"] == {"duplicates": 0, "schema_errors": 0, "leakage_errors": 0}
    assert set(m["layers"]) == {"raw", "bronze", "silver", "gold"}


def test_upload_partition_dry_run(tmp_path):
    client = DatasetClient(dry_run=True, local_dir=tmp_path)
    assert client.mode == "dry-run"
    res = upload_partition([{"match_id": "x"}], "raw/football/provider=fallback/date=2026-06-27/fixtures.json", client=client)
    assert res["status"] == "dry-run"
    assert (tmp_path / "raw/football/provider=fallback/date=2026-06-27/fixtures.json").exists()
