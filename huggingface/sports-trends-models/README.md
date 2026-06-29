---
license: mit
library_name: scikit-learn
pipeline_tag: tabular-classification
tags:
  - sports-analytics
  - sports-prediction
  - football
  - soccer
  - basketball
  - tennis
  - cricket
  - tabular-classification
  - probability-calibration
  - elo
  - gradient-boosting
language:
  - en
model-index:
  - name: sports-trends-models
    results:
      - task:
          type: tabular-classification
          name: Match outcome prediction
        dataset:
          name: ruslanmv/sports-trends-dataset
          type: ruslanmv/sports-trends-dataset
        metrics:
          - type: accuracy
            name: Accuracy (holdout, sport-dependent)
            value: 0.55
          - type: log_loss
            name: Log loss (calibrated)
            value: 0.98
---

<div align="center">

# ⚽🏀🎾🏏 Sports-Trends Models
### Calibrated, leakage-safe match-outcome models — a model picked for each sport.

**Part of [Ruslan Magana Sports Intelligence](https://ruslanmv.com/sports-trends/) — AI match predictions, live results and trending games, refreshed every day.**

[![🌐 Live dashboard](https://img.shields.io/badge/live-ruslanmv.com%2Fsports--trends-0aa06e)](https://ruslanmv.com/sports-trends/)
[![🤗 Dataset](https://img.shields.io/badge/🤗%20dataset-sports--trends--dataset-ffce00)](https://huggingface.co/datasets/ruslanmv/sports-trends-dataset)
[![GitHub](https://img.shields.io/badge/GitHub-sports--trends-181717?logo=github)](https://github.com/ruslanmv/sports-trends)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f)](https://github.com/ruslanmv/sports-trends/blob/main/LICENSE)

</div>

> **TL;DR** — This repository hosts the production models behind
> [ruslanmv.com/sports-trends](https://ruslanmv.com/sports-trends/). Each sport gets
> the algorithm best suited to its dynamics, every model outputs **probability-calibrated**
> win/draw/loss odds, and the whole training pipeline is **leakage-safe by construction**.
> Models are retrained automatically and published under `<sport>/latest/`.
>
> 📊 **For information & entertainment only — not betting advice.**

---

## 🎯 What these models do

Given an upcoming fixture, the models estimate the **probability of each outcome**:

| Sport | Outcome space | Model | Why this model |
|-------|---------------|-------|----------------|
| ⚽ **Football** | home / draw / away (3-way) | `HistGradientBoostingClassifier` | Draws + non-linear Elo×form interactions; gradient boosting handles the 3-way target and feature interactions best. |
| 🏀 **Basketball** | home / away (2-way) | `LogisticRegression` | No draws and a strong linear Elo signal — calibrated logistic regression gives clean, well-behaved probabilities. |
| 🎾 **Tennis** | player 1 / player 2 (2-way) | `GradientBoostingClassifier` | Head-to-head, surface and form interactions are non-linear; GBDT captures them on short player histories. |
| 🏏 **Cricket** | home / away (2-way) | `RandomForestClassifier` | Format-dependent, noisy results; bagged trees are robust to variance and outliers. |
| 🏆 **World Cup / international** | 90-min result **+ to-advance** | Elo + tournament model | Adds host advantage, neutral venue, confederation strength and stage importance, plus an extra-time/penalties "who advances" layer. |

Every estimator is wrapped in **probability calibration** (isotonic for tree models,
sigmoid for logistic) so a published "62%" really behaves like 62% over many games —
with a safe fallback to the raw estimator when a dataset is too small to calibrate.

---

## 🧠 How the predictions work

Predictions are **not** a black box and **not** scraped odds. They are produced by a
transparent, reproducible pipeline. Every published prediction ships with a short
plain-language **explanation** of the drivers behind it.

```
   Free sports APIs                 Feature engineering            Per-sport model
 ┌──────────────────┐   normalize  ┌────────────────────┐  infer  ┌────────────────┐
 │ fixtures, results│ ───────────▶ │ Elo · form · H2H · │ ──────▶ │ calibrated     │
 │ (multi-source)   │   canonical  │ rest · home adv ·  │         │ probabilities  │
 │  + offline mock  │   schema     │ league/social      │         │ + explanation  │
 └──────────────────┘              └────────────────────┘         └───────┬────────┘
        │                                   ▲                              │
        │            leakage guard: only matches with date < fixture date  │
        └──────────────────────────────────────────────────────────── publish JSON
```

**1. Ingest.** Fixtures and results are pulled from free sports APIs (with a public-domain
World Cup feed and a deterministic offline mock as fallbacks), then normalized to one
canonical schema with stable IDs and de-duplication.

**2. Features (leakage-safe).** For each fixture we compute only information available
*before* kickoff:

- **Elo ratings** — a self-correcting team/player strength rating updated after each result.
- **Recent form** — rolling performance over the last N matches.
- **Head-to-head** — historical record between the two sides.
- **Rest days & congestion** — fatigue from fixture density.
- **Home advantage** — venue effect (and, for the World Cup, host-nation + neutral-venue handling).
- **League / tournament strength** & **stage importance** — context weighting.
- **Social interest** — popularity signal used for ranking, not for the core outcome.

**3. Train.** Labels and features are joined, split **chronologically** (train → validation →
test, never random), and checked by automated **leakage assertions** before any model sees them.
Each sport trains its zoo model (table above) and the probabilities are calibrated.

**4. Infer.** The inference window passes through the model to produce per-outcome
probabilities. When a trained model isn't available for a fixture, the system degrades
gracefully to a transparent **Elo heuristic** — so the product never shows a blank.

**5. Publish.** Outputs are written as static JSON and rendered on
[the live dashboard](https://ruslanmv.com/sports-trends/), each card carrying its
probabilities, a confidence value, and the human-readable reasoning.

### 🛡️ Why you can trust the numbers

- **Leakage-safe by construction.** Features for a fixture use *only* matches with
  `date < fixture.match_date`. A regression test plants a future blowout and asserts the
  pre-match Elo is unchanged — guaranteeing no peeking at the result.
- **Calibrated probabilities.** Outputs are calibrated, so they are meaningful as odds,
  not just rankings. We report **log loss** (calibration quality), not only accuracy.
- **Honest baselines.** These are well-understood, auditable scikit-learn models — chosen
  for reliability and explainability over hype.
- **Reproducible & open.** The full pipeline is open source on
  [GitHub](https://github.com/ruslanmv/sports-trends) and runs automatically in CI.

---

## 📦 Repository layout

```
<sport>/latest/
    model.pkl              # calibrated scikit-learn estimator (joblib)
    feature_schema.json    # ordered feature names + dtypes expected at inference
    metrics.json           # holdout accuracy + log loss for this version
    README.md              # per-sport card
registry/
    latest_versions.json   # production pointer: sport -> {version, path, metrics}
```

`registry/latest_versions.json` is the source of truth for which version is live.

---

## 🚀 Use a model

```python
import json
import joblib
import pandas as pd
from huggingface_hub import hf_hub_download

REPO = "ruslanmv/sports-trends-models"
SPORT = "football"

model = joblib.load(hf_hub_download(REPO, f"{SPORT}/latest/model.pkl"))
schema = json.load(open(hf_hub_download(REPO, f"{SPORT}/latest/feature_schema.json")))

# Build one row with the features named in feature_schema.json (same order).
features = {name: 0.0 for name in schema["features"]}
X = pd.DataFrame([features])[schema["features"]]

proba = model.predict_proba(X)[0]
print(dict(zip(model.classes_, proba.round(3))))
# e.g. {'home': 0.58, 'draw': 0.18, 'away': 0.24}
```

Check the live production versions and metrics:

```python
import json
from huggingface_hub import hf_hub_download
reg = json.load(open(hf_hub_download("ruslanmv/sports-trends-models",
                                     "registry/latest_versions.json")))
print(reg["football"])  # -> {'version': ..., 'path': 'football/latest/', 'metrics': {...}}
```

---

## 📈 Evaluation

Each version stores its own `metrics.json` (holdout **accuracy** and calibrated
**log loss**) produced on a chronological hold-out split. Sports outcomes are
high-variance, so treat metrics as *relative* model-quality signals rather than
guarantees: a well-calibrated football model typically lands meaningfully above the
3-way random/majority baseline, and log loss is the metric we optimise for because
**calibration matters more than raw accuracy** for probabilistic predictions.

> Numbers in the `model-index` above are indicative placeholders; the authoritative,
> per-version metrics always live in each `<sport>/latest/metrics.json`.

---

## ⚠️ Intended use & limitations

**Intended use** — research, education, sports analytics, and powering the
[ruslanmv.com/sports-trends](https://ruslanmv.com/sports-trends/) dashboard.

**Out of scope / limitations**

- 🚫 **Not betting advice.** Predictions are informational and for entertainment only.
  No outcome is guaranteed. Please gamble responsibly, if at all.
- Models reflect their training data: lower-tier competitions and rare matchups carry
  more uncertainty than top leagues.
- Free data sources can be delayed or incomplete; the system favours graceful degradation
  (Elo heuristic / mock) over fabricated precision.
- They estimate *probabilities*, not certainties — variance and upsets are expected.

---

## 🧾 Citation

```bibtex
@software{magana_sports_trends_2026,
  author  = {Ruslan Magana Vsevolodovna},
  title   = {Sports-Trends: Calibrated, leakage-safe sports outcome models},
  year    = {2026},
  url      = {https://huggingface.co/ruslanmv/sports-trends-models},
  note     = {Live dashboard: https://ruslanmv.com/sports-trends/}
}
```

---

<div align="center">

### 👤 About the author

Built and maintained by **[Ruslan Magana Vsevolodovna](https://ruslanmv.com)** —
AI / ML engineer working on data platforms, MLOps and applied machine learning.

🌐 **[ruslanmv.com](https://ruslanmv.com)** · 📊 **[Live dashboard](https://ruslanmv.com/sports-trends/)** · 🤗 **[Dataset](https://huggingface.co/datasets/ruslanmv/sports-trends-dataset)** · 💻 **[GitHub](https://github.com/ruslanmv/sports-trends)**

<sub>Powered by Hugging Face 🤗 + GitHub Actions ⚙️ · Licensed MIT · Not betting advice.</sub>

</div>
