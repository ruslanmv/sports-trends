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

## Model layout

```
<sport>/latest/{model.pkl, feature_schema.json, metrics.json, README.md}
registry/latest_versions.json
```

## Dual-mode upload

`hf/dataset_client.py::DatasetClient` and `models/registry.py::ModelRegistry`
both run **live** when `HF_TOKEN` is set and **dry-run** (local `.data_lake/`,
`.models/`) otherwise. The same scripts work in CI and on a laptop with no token.
