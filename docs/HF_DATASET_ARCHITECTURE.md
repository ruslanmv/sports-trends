# Hugging Face Data Lake Architecture

Large data never lives in GitHub. It lives in two HF repos:

- **Dataset:** `ruslanmv/sports-trends-dataset` (`repo_type="dataset"`)
- **Models:** `ruslanmv/sports-trends-models` (`repo_type="model"`)

## Dataset layout

```
raw/<sport>/provider=<p>/date=YYYY-MM-DD/fixtures.json   # immutable ingest
bronze/  silver/                                          # cleaned/standardized
gold/
  features/<feature>/sport=<sport>/date=.../part.parquet
  training/<sport>/{train,validation,test}.parquet
  inference/tomorrow/date=YYYY-MM-DD/inference_input.parquet
quality/{leakage_report,schema_validation,...}.json
registry/{dataset_manifest,latest_versions}.json
```

ML datasets are **partitioned Parquet** (by sport/date/layer) — never one giant CSV.
Frontend files are JSON only.

### Feedback-loop partitions

```
predictions/<sport>/date=YYYY-MM-DD/predictions.parquet   # prediction ledger (open)
gold/outcomes/<sport>/date=YYYY-MM-DD/settled.parquet      # prediction ⨝ real result (labelled)
quality/model_performance.json                             # rolling accuracy/log-loss/Brier/calibration
```

Predictions are logged at inference time (with their feature snapshot + model
version), reconciled against real results after each match, and folded back into
`gold/training` so retraining uses fresh, real outcomes. See
[FEEDBACK_LOOP.md](FEEDBACK_LOOP.md).

## Model layout

```
<sport>/latest/{model.pkl, feature_schema.json, metrics.json, README.md}
registry/latest_versions.json
```

## Dual-mode upload

`hf/dataset_client.py::DatasetClient` and `models/registry.py::ModelRegistry`
both run **live** when `HF_TOKEN` is set and **dry-run** (local `.data_lake/`,
`.models/`) otherwise. The same scripts work in CI and on a laptop with no token.

## Repo cards (READMEs)

The public "front page" of each HF repo is version-controlled in GitHub:

```
huggingface/sports-trends-models/README.md   -> HF model repo card
huggingface/sports-trends-dataset/README.md  -> HF dataset repo card
```

Publish them with `scripts/publish_hf_cards.py` (live when `HF_TOKEN` is set,
otherwise dry-run — it validates the YAML front-matter and logs what it would
upload). The cards explain how predictions work, the per-sport model zoo,
calibration and leakage prevention, and link back to
[ruslanmv.com/sports-trends](https://ruslanmv.com/sports-trends/).
