# FIFA World Cup & International Football

A dedicated international-football module under `football`, covering the **2026
World Cup** (group → Round of 32 → … → Final) and **World Cup qualifiers**.

## Free data sources (priority order)

| # | Source | Key? | Reachability (verified) | Use |
|---|--------|------|--------------------------|-----|
| 1 | API-Football / API-SPORTS | `SPORTS_API_FOOTBALL_KEY` | 403 without key (reachable) | best live; 100 req/day free |
| 2 | football-data.org | `FOOTBALL_DATA_TOKEN` | 403 without token (reachable) | free delayed fixtures/tables |
| 3 | **OpenFootball worldcup.json** | none | **HTTP 200, no key** | public-domain **full 104-match** schedule + results (2018/2022/2026 live) |
| 3b | **TheStatsAPI fixtures.json** | none (attribution) | **HTTP 200, no key** | clean absolute-UTC kick-off times + official stadiums; backfills (3) |
| 4 | bundled mock | none | always | offline fallback (Round-of-32 seed) |

`WorldCupProvider` selects the best available source and always degrades to the
next one, so the feature renders with or without keys/network. Sources **3** and
**3b** are merged: OpenFootball provides the canonical schedule/results, and
TheStatsAPI backfills accurate kick-off timestamps onto it (OpenFootball stores
local time + UTC offset, e.g. `"17:00 UTC-4"`).

### What we derive from the free feed (no key)

From the single OpenFootball 2026 file (104 matches, real teams/venues) the
provider derives, with TheStatsAPI kick-off enrichment:

- **`fetch_fixtures()`** — the complete schedule (group → final), chronological,
  with knockout placeholder slots (`W74`, `1A`, …) filtered out.
- **`fetch_upcoming()`** — scheduled matches, soonest first (knockouts preferred).
- **`fetch_standings()`** — live group tables (P/W/D/L/GF/GA/GD/Pts) computed
  from finished group results via `compute_standings()`.
- **`fetch_finished()`** — completed matches with scorers, newest first.

Additional keyless sources evaluated for live in-play data:
`worldcup26.ir/get/games` (live scores + scorers, no key) and
`thesportsdb.com` (year-round multi-sport). Both reachable; wired opportunistically.

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

- JSON: `assets/data/sports/worldcup{,-predictions,-live,-qualifiers,-fixtures,-standings,-trending}.json`
- Page: `/sports/football/world-cup/` — premium, Apple-inspired layout:
  cinematic hero with live **countdown** to the next kick-off, stat ribbon,
  **full Match Schedule** (segmented Upcoming / Group Stage / Knockouts /
  Results, grouped by day), knockout prediction board, **Road to the Final**
  bracket, **live group standings** and qualifiers. Styles in
  `assets/css/sports-worldcup.css`; hydration in `assets/js/sports-worldcup.js`.
- Pipeline: `scripts/run_worldcup_pipeline.py` (run by `sports-daily-pipeline` +
  `sports-live-refresh`).

### `worldcup-fixtures.json`

The schedule feed powering the new Match Schedule section. Shape:

```json
{ "competition": "FIFA World Cup 2026", "total": 104, "upcoming": 15,
  "sections": [ { "stage": "round_of_32", "label": "Round of 32",
    "matches": [ { "home_team": "...", "away_team": "...", "group": "",
      "date": "2026-06-29", "kickoff": "2026-06-29T22:00:00+00:00",
      "kickoff_label": "29 Jun 22:00", "venue": "...", "host_city": "...",
      "status": "scheduled", "home_score": null, "away_score": null } ] } ] }
```
