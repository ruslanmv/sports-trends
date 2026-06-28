# FIFA World Cup & International Football

A dedicated international-football module under `football`, covering the **2026
World Cup** (group → Round of 32 → … → Final) and **World Cup qualifiers**.

## Free data sources (priority order)

| # | Source | Key? | Reachability (verified) | Use |
|---|--------|------|--------------------------|-----|
| 1 | API-Football / API-SPORTS | `SPORTS_API_FOOTBALL_KEY` | 403 without key (reachable) | best live; 100 req/day free |
| 2 | football-data.org | `FOOTBALL_DATA_TOKEN` | 403 without token (reachable) | free delayed fixtures/tables |
| 3 | **OpenFootball worldcup.json** | none | **HTTP 200, no key** | public-domain schedule/results (2018/2022/2026 live) |
| 4 | bundled mock | none | always | offline fallback (Round-of-32 seed) |

`WorldCupProvider` selects the best available source and always degrades to the
next one, so the feature renders with or without keys/network.

## Data model additions

```
competition_type : "world_cup" | "world_cup_qualifier"
confederation    : UEFA | CONMEBOL | CONCACAF | CAF | AFC | OFC | INTERNATIONAL
stage            : qualifying_group | playoff | group_stage | round_of_32 |
                   round_of_16 | quarterfinals | semifinals | third_place | final
group, is_country_match, neutral_venue, host_advantage, stage_importance
```

## Prediction layers (not just home/draw/away)

- **Knockout**: `result_90` (team1 / draw / team2) **+ `to_advance`** (includes extra
  time / penalties).
- **Qualifier**: win/draw/loss **+ `group_qualification_probability`** and
  `elimination_risk`.
- A **viral interest score** ranks country-vs-country ties.

Features: national-team Elo, host advantage (non-neutral venues), neutral venue,
confederation strength, stage importance.

## Outputs & pages

- JSON: `assets/data/sports/worldcup{,-predictions,-live,-qualifiers,-standings,-trending}.json`
- Page: `/sports/football/world-cup/` (knockout board, qualifiers, standings)
- Pipeline: `scripts/run_worldcup_pipeline.py` (run by `sports-daily-pipeline` +
  `sports-live-refresh`).
