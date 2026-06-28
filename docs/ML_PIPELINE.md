# ML Pipeline

Three cadences, no model retraining on the hot path:

| Cadence | Workflow(s) | Does |
| --- | --- | --- |
| Every 30 min | `sports-live-refresh`, `hf-refresh-dataset` | Fetch live/today, normalize, publish `live/today/status.json`, upload raw partitions |
| Daily | `hf-generate-inference-window`, `sports-predict-tomorrow`, `hf-feature-generation`, `sports-generate-seo-pages` | Build inference window, predict tomorrow, regenerate features + SEO pages |
| Weekly | `hf-build-training-dataset`, `train-models` | Rebuild training data, retrain + publish models |

## Stages

1. **Ingest** (`providers/*`, `ingestion/fetch_raw_data.py`) — live API or mock fallback.
2. **Normalize** (`ingestion/normalize_matches.py`) — canonical schema, stable id, dedup.
3. **Features** (`features/*`) — Elo, form, H2H, rest, league/social. Leakage-safe.
4. **Training data** (`datasets/build_training_dataset.py`) — labels + features, chronological split, leakage checks.
5. **Train** (`models/*`) — **sport-optimized** models from `models/model_zoo.py`
   (football → HistGradientBoosting, basketball → LogisticRegression,
   tennis → GradientBoosting, cricket → RandomForest), probability-calibrated,
   retrained **daily** by `sports-daily-pipeline.yml` and published to HF.
6. **Inference** (`inference/*`) — window → model (or Elo heuristic) → probabilities + explanations.
7. **Publish** (`inference/publish_json.py`) — the seven public JSON files.

## Leakage prevention

Features for a fixture use only matches with `date < fixture.match_date`.
`datasets/leakage_checks.py` asserts feature/label disjointness and chronological
ordering; a test plants a future blowout and verifies Elo is unchanged.
