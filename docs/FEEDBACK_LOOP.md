# Prediction Feedback Loop — how the models keep improving

> **Goal.** Every prediction we publish is remembered. When the match finishes,
> we compare what we predicted to what actually happened, score it, and feed that
> labelled outcome back into training — so the models retrain on fresh, real data
> and stay coherent with the latest results.

This closes the loop between *inference* and *training*: the more we predict, the
more labelled data we accumulate, and the better the next model becomes.

```
        ┌─────────────┐   log    ┌──────────────────────┐
 daily  │ predict     │ ───────▶ │ predictions/ (ledger) │  status=open
        │ tomorrow    │          │  feature snapshot +   │
        └─────────────┘          │  model version + probs│
                                 └───────────┬──────────┘
                                             │ match finishes
        ┌─────────────┐ results  ┌───────────▼──────────┐
 daily  │ fetch real  │ ───────▶ │ reconcile()          │  join by match_id
        │ results     │          │  label + score        │  (correct? prob? brier?)
        └─────────────┘          └───────────┬──────────┘
                                             │ status=settled
                    ┌────────────────────────┼────────────────────────┐
                    ▼                         ▼                        ▼
        gold/outcomes/ (labelled)   quality/model_performance.json   (drift signal)
                    │                  rolling acc / log loss /
                    │                  Brier / calibration /
                    │                  model-vs-heuristic
                    ▼
 weekly  build_training_dataset  ──merge──▶  gold/training/  ──▶  train-models
         (history + settled outcomes, leakage-checked, chronological split)
```

## The three moves

### 1. Log (at prediction time) — `scripts/run_log_predictions.py`
Builds the inference window exactly like the frontend predictor, runs the
per-sport model (or Elo heuristic), and writes one **open** ledger row per
fixture to `predictions/<sport>/date=<day>/predictions.parquet`. Each row stores:

- identity & timing: `match_id, sport, league, home_team, away_team, kickoff, predicted_at`
- model provenance: `model_version` (from `registry/latest_versions.json`), `model_used`
- the prediction: `prob_<class>` columns, `predicted_class`, `predicted_pick`, `confidence`
- the **exact feature snapshot** (`FEATURE_COLUMNS`) the prediction was made from

Storing the feature snapshot is what makes the loop leakage-safe: reconciliation
never recomputes features, so there is no way to peek at the result.

### 2. Reconcile (after the match) — `scripts/run_reconcile_outcomes.py`
Joins **open** ledger rows to finished results by `match_id`. For each match with
a final score it derives the realized outcome + label columns (reusing
`build_training_dataset.label_row`) and scores the prediction:

- `correct` — did the argmax pick match the result?
- `prob_actual` — probability we assigned to the realized class (drives log loss)
- `brier` — `Σ (p_c − 1{c=actual})²` across classes
- `log_loss` — `−log(prob_actual)`

Settled rows are appended to `gold/outcomes/<sport>/date=<day>/settled.parquet`;
the ledger partition is rewritten to keep only the still-open rows (so the ledger
is a clean queue and nothing settles twice).

### 3. Learn
- **Monitor.** `quality/model_performance.json` aggregates rolling accuracy, log
  loss, Brier and a **calibration** table (predicted confidence vs realized hit
  rate), split **model vs heuristic** so we can prove the trained models beat the
  Elo baseline — the signal that justifies (or triggers) a retrain.
- **Retrain.** `build_prediction_dataset` projects settled rows into
  leakage-safe training rows, and `merge_training_rows` folds them into the
  history-derived training set (settled real outcomes win on `match_id`).
  `run_build_training_dataset.py` then runs the usual leakage checks +
  chronological split, and `train-models` retrains on the augmented data.

## Cadence

| Step | Script | Workflow | Frequency |
|------|--------|----------|-----------|
| Log predictions | `run_log_predictions.py` | `sports-predict-tomorrow` | daily |
| Reconcile outcomes | `run_reconcile_outcomes.py` | `hf-historical-results` | daily |
| Rebuild training data (+ settled) | `run_build_training_dataset.py` | `hf-build-training-dataset` | weekly |
| Retrain & publish models | `run_train_models.py` | `train-models` | weekly |

All steps are **dual-mode**: live uploads to Hugging Face when `HF_TOKEN` is set,
otherwise dry-run against the local `.data_lake/`.

## Lake layout additions

```
predictions/<sport>/date=YYYY-MM-DD/predictions.parquet   # open ledger
gold/outcomes/<sport>/date=YYYY-MM-DD/settled.parquet      # prediction ⨝ result (labelled)
quality/model_performance.json                             # rolling accuracy/log-loss/Brier/calibration
```

## Why this earns trust

- **Auditable track record.** Every prediction and its realized outcome is kept,
  so model quality is measured on out-of-sample, real future matches — not
  in-sample claims.
- **Calibration, not just accuracy.** We report log loss / Brier / reliability
  buckets, the right metrics for probabilistic predictions.
- **Always fresh.** Retraining consumes accumulated real outcomes, so the live
  models track the latest form, transfers and results.
- **Leakage-safe by construction.** Feature snapshots are frozen at prediction
  time and re-checked by the leakage report before any retrain.
