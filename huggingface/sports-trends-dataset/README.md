---
license: mit
language:
  - en
pretty_name: "Sports-Trends — Multi-Sport Match Dataset (medallion lake)"
task_categories:
  - tabular-classification
tags:
  - sports
  - sports-analytics
  - football
  - soccer
  - basketball
  - tennis
  - cricket
  - elo
  - feature-store
  - parquet
  - medallion-architecture
size_categories:
  - 10K<n<100K
---

<div align="center">

# ⚽🏀🎾🏏 Sports-Trends Dataset
### A leakage-safe, multi-sport match data lake — raw fixtures → engineered features → training splits.

**The data backbone of [Ruslan Magana Sports Intelligence](https://ruslanmv.com/sports-trends/) — refreshed automatically every day.**

[![🌐 Live dashboard](https://img.shields.io/badge/live-ruslanmv.com%2Fsports--trends-0aa06e)](https://ruslanmv.com/sports-trends/)
[![🤗 Models](https://img.shields.io/badge/🤗%20models-sports--trends--models-ffce00)](https://huggingface.co/ruslanmv/sports-trends-models)
[![GitHub](https://img.shields.io/badge/GitHub-sports--trends-181717?logo=github)](https://github.com/ruslanmv/sports-trends)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f)](https://github.com/ruslanmv/sports-trends/blob/main/LICENSE)

</div>

> **TL;DR** — A continuously-updated, **medallion-architecture** data lake for football,
> basketball, tennis and cricket: immutable raw ingests, cleaned/standardized layers, an
> engineered feature store, and ready-to-train **chronological** splits in partitioned
> Parquet. Built to be **leakage-safe** and reproducible.
>
> 🤝 Pairs with the [sports-trends-models](https://huggingface.co/ruslanmv/sports-trends-models) repo.

---

## 🗂️ What's inside (medallion layout)

Large data never lives in GitHub — it lives here, partitioned by sport / date / layer.

```
raw/<sport>/provider=<p>/date=YYYY-MM-DD/fixtures.json   # immutable ingest (source of truth)
bronze/  silver/                                          # cleaned + standardized records
gold/
  features/<feature>/sport=<sport>/date=.../part.parquet  # engineered feature store
  training/<sport>/{train,validation,test}.parquet        # chronological, leakage-safe splits
  inference/tomorrow/date=YYYY-MM-DD/inference_input.parquet
quality/{leakage_report,schema_validation,...}.json       # automated data-quality reports
registry/{dataset_manifest,latest_versions}.json          # versioning + production pointers
```

- **Raw** is append-only and immutable — full provenance back to the source API.
- **Bronze/Silver** normalize to one **canonical schema** with stable IDs and de-duplication.
- **Gold** is analytics/ML-ready: a feature store plus train/validation/test splits.
- ML data is **partitioned Parquet** (by sport/date/layer) — never one giant CSV.

---

## 🧮 Engineered features (gold)

Every feature is computed **leakage-safely** — for a given fixture, only matches with
`date < fixture.match_date` are used:

| Feature | Description |
|---------|-------------|
| **Elo rating** | Self-correcting team/player strength, updated after each result. |
| **Recent form** | Rolling performance over the last N matches. |
| **Head-to-head** | Historical record between the two sides. |
| **Rest days** | Fatigue / fixture congestion. |
| **Home advantage** | Venue effect (+ host-nation & neutral-venue handling for the World Cup). |
| **League / tournament strength** | Competition-level context weighting. |
| **Stage importance** | Group → knockout → final weighting for tournaments. |
| **Social interest** | Popularity signal (used for ranking, not core outcome). |

The prediction **label** is the realized match outcome (home/draw/away or 2-way per sport).

---

## ✅ Data quality & leakage prevention

- **Chronological splits.** Training data is ordered by time — train precedes validation
  precedes test. No random shuffling across the time boundary.
- **Leakage assertions.** Automated checks (`quality/leakage_report.json`) verify
  feature/label disjointness and chronological ordering; a regression test plants a future
  blowout and confirms pre-match features are unchanged.
- **Schema validation.** Records are validated against the canonical schema
  (`quality/schema_validation.json`).
- **Versioned manifests.** `registry/dataset_manifest.json` records version, timestamp,
  sports covered, layers present, and quality counts.

---

## 🚀 Load the data

```python
import pandas as pd
from huggingface_hub import hf_hub_download

REPO = "ruslanmv/sports-trends-dataset"

# Ready-to-train football split (chronological, leakage-safe)
train = pd.read_parquet(hf_hub_download(REPO, "gold/training/football/train.parquet", repo_type="dataset"))
print(train.shape)
print(train.head())
```

Or stream everything for a sport with the 🤗 `datasets` library:

```python
from datasets import load_dataset
ds = load_dataset("ruslanmv/sports-trends-dataset", data_files="gold/training/football/*.parquet")
```

---

## 🔄 Update cadence

| Cadence | What refreshes |
|---------|----------------|
| **Every 30 min** | Live/today fixtures + raw partitions. |
| **Daily** | Inference window, regenerated features, tomorrow's predictions. |
| **Weekly** | Rebuilt training datasets feeding model retraining. |

All updates run automatically via GitHub Actions.

---

## ⚖️ Sources, license & intended use

- **Sources.** Aggregated from free sports APIs and public-domain feeds (e.g. OpenFootball
  for World Cup data), normalized into a common schema. Raw partitions retain provider provenance.
- **License.** MIT for this dataset's structure, schema, and engineered features. Please
  respect the terms of the underlying upstream providers for the raw factual data.
- **Intended use.** Sports analytics, ML research, education, and powering the
  [ruslanmv.com/sports-trends](https://ruslanmv.com/sports-trends/) dashboard.
- 🚫 **Not betting advice.** Provided for information and entertainment only.

---

## 🧾 Citation

```bibtex
@dataset{magana_sports_trends_dataset_2026,
  author  = {Ruslan Magana Vsevolodovna},
  title   = {Sports-Trends: A leakage-safe multi-sport match data lake},
  year    = {2026},
  url      = {https://huggingface.co/datasets/ruslanmv/sports-trends-dataset},
  note     = {Live dashboard: https://ruslanmv.com/sports-trends/}
}
```

---

<div align="center">

Built and maintained by **[Ruslan Magana Vsevolodovna](https://ruslanmv.com)** — AI / ML engineer.

🌐 **[ruslanmv.com](https://ruslanmv.com)** · 📊 **[Live dashboard](https://ruslanmv.com/sports-trends/)** · 🤗 **[Models](https://huggingface.co/ruslanmv/sports-trends-models)** · 💻 **[GitHub](https://github.com/ruslanmv/sports-trends)**

<sub>Powered by Hugging Face 🤗 + GitHub Actions ⚙️ · Licensed MIT · Not betting advice.</sub>

</div>
