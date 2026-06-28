# GitHub Actions

Eleven workflows in `.github/workflows/`. All support `workflow_dispatch`, run on a
cron schedule, fall back to mock data when secrets are missing, and only commit
when files actually changed.

| Workflow | Schedule (UTC) | Purpose | Commits? |
| --- | --- | --- | --- |
| `sports-daily-pipeline` | `20 3 * * *` | **dataset refresh + daily model retrain + predictions + README** | README, assets/data, sports/, og/ |
| `sports-live-refresh` | `*/30 * * * *` | live/today/status JSON | assets/data/sports |
| `hf-refresh-dataset` | `*/30 * * * *` | upload raw partitions to HF | no (HF) |
| `hf-generate-inference-window` | `15 3 * * *` | tomorrow inference window | no (HF) |
| `sports-predict-tomorrow` | `30 3 * * *` | tomorrow/predictions/trending JSON | assets/data/sports |
| `hf-feature-generation` | `0 3 * * *` | gold/features parquet | no (HF) |
| `hf-historical-results` | `0 2 * * *` | finished results to HF | no (HF) |
| `sports-generate-seo-pages` | `0 6 * * *` | match/league pages, sitemap, OG | sports/, og/ |
| `hf-build-training-dataset` | `30 4 * * 1` | gold/training parquet | no (HF) |
| `train-models` | `0 5 * * 1` | train + publish models | no (HF) |
| `sports-deploy` | push / dispatch | validate JSON + tests (CI gate) | no |

## Configure the `HF_TOKEN` secret (and optional API keys)

The workflows read `HF_TOKEN` from **GitHub Actions secrets** (never from a
committed file). Add it once — choose either option:

**A. GitHub UI**
`Settings -> Secrets and variables -> Actions -> New repository secret`
- Name: `HF_TOKEN`  ·  Value: your Hugging Face **write** token (`hf_...`).
- (optional) `SPORTS_API_FOOTBALL_KEY`, `SPORTS_BASKETBALL_API_KEY`,
  `SPORTS_TENNIS_API_KEY`, `SPORTS_CRICKET_API_KEY`, `SPORTS_API_KEY`.

**B. One command (GitHub CLI)**
```bash
export HF_TOKEN=hf_xxxxxxxx
./scripts/setup_github_secrets.sh ruslanmv/sports-trends
gh secret list --repo ruslanmv/sports-trends   # verify
```

> ⚠️ A token must be a **secret**, not an Actions *variable* — variables are
> visible in logs and the API. All 11 workflows already reference
> `${{ secrets.HF_TOKEN }}`; with the secret set, HF uploads go live, otherwise
> they run in dry-run.

## Required secrets

`HF_TOKEN` (uploads; dry-run without it), and optionally `SPORTS_API_KEY`,
`SPORTS_API_FOOTBALL_KEY`, `SPORTS_BASKETBALL_API_KEY`, `SPORTS_TENNIS_API_KEY`,
`SPORTS_CRICKET_API_KEY`. With no provider keys, providers serve mock data.
