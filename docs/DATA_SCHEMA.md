# Data Schema

## Canonical match (normalized)

Every provider record is normalized to these fields
(`sports_trends.ingestion.normalize_matches`):

| Field | Notes |
| --- | --- |
| `match_id` | Stable id — provider id, else `sport-league-home-away-date` slug |
| `sport` | football, basketball, tennis, cricket, baseball, esports |
| `league_id`, `league_name`, `season`, `country` | League/competition metadata |
| `match_date`, `kickoff`, `venue` | Schedule |
| `home_team_id`, `home_team`, `away_team_id`, `away_team` | Sides |
| `home_score`, `away_score` | Numbers, or strings for cricket/tennis sets |
| `status`, `is_live`, `is_finished` | Lifecycle |
| `provider`, `last_updated` | Provenance |

A pydantic model (`ingestion/canonical.py::CanonicalMatch`) validates every record.

## Public frontend JSON (`assets/data/sports/`)

`status.json`, `today.json`, `tomorrow.json`, `live.json`, `trending.json`,
`predictions.json`, `rankings.json`. Each `*.json` is validated against the JSON
Schemas in `src/sports_trends/schemas/` by
`datasets/validate_dataset.py::validate_frontend_json`.

## ML feature columns

See `features/feature_pipeline.py::FEATURE_COLUMNS` — Elo, rolling form (5/10),
goals for/against, rest days, home advantage, head-to-head, league importance,
social interest. All features are computed using **only matches before** the
fixture date (no leakage).
