# Ruslan Magana Sports Intelligence

Premium sports intelligence section for `ruslanmv.com/sports/`.

**Navigation name:** Sports  
**URL:** `/sports/`  
**Product name:** Ruslan Magana Sports Intelligence  
**Headline:** Tomorrow’s Biggest Games  
**Primary section:** Tomorrow’s Top Matches  
**Tagline:** AI predictions, live results, and trending games updated every 30 minutes.

This repository is a complete starter scaffold. It includes the expected Jekyll pages, Liquid includes, frontend assets, JSON data placeholders, Python ingestion/prediction/ranking modules, templates, tests, documentation, and GitHub Actions workflows. The next step is to let an AI coder populate the placeholder modules with provider-specific implementation.


## Technical naming

- GitHub repository: `sports-trends`
- Python package: `sports_trends`
- Hugging Face dataset: `ruslanmv/sports-trends-dataset`
- Hugging Face model repo: `ruslanmv/sports-trends-models`

Large raw data, parquet archives, training datasets, and model artifacts belong in Hugging Face repositories. GitHub keeps code, workflows, Jekyll pages, templates, tests, docs, and small frontend JSON files only.

## Repository purpose

This repo is designed to generate and maintain a premium sports destination that can be copied or deployed into the main `ruslanmv.com` site under `/sports/`.

The system is intended to:

1. Fetch today's fixtures and live results.
2. Fetch tomorrow's fixtures.
3. Generate AI predictions.
4. Rank matches by global interest, league importance, social velocity, and model confidence.
5. Write static JSON files for the frontend.
6. Generate programmatic match/league/sport pages for SEO.
7. Generate Open Graph cards for viral sharing.
8. Deploy the final generated section into the main website.

## Minimum launch version

```txt
/sports/
├── Hero
├── Stats cards
├── Status bar
├── Tomorrow’s Top Matches
├── Live Results
├── Trending Matches
└── Explore Sports
```

Minimum data files:

```txt
assets/data/sports/status.json
assets/data/sports/tomorrow.json
assets/data/sports/live.json
assets/data/sports/trending.json
```

Minimum workflows:

```txt
.github/workflows/sports-live-refresh.yml
.github/workflows/sports-predict-tomorrow.yml
.github/workflows/sports-deploy.yml
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_fetch_raw_data.py
python scripts/run_generate_inference_window.py
python scripts/run_predict_tomorrow.py
python scripts/run_generate_pages.py
```

For frontend-only preview, copy this directory into a Jekyll-compatible `ruslanmv.com` checkout and open `/sports/`.

## Important disclaimer

Predictions are informational and educational only. They must not be presented as betting advice, guaranteed outcomes, or financial advice.
