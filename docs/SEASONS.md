# Season Calendar — always-on coverage

`features/sports_calendar.py` encodes the major competitions and their date
windows so the portal stays relevant every day of the year. When one tournament
ends, `featured_competition()` rolls over to the next most important active one.

## How it works

- Each `Tournament` has a `(month, day)` start/end window (wrap-around supported,
  e.g. club seasons Aug→May) and an `importance` score. One-off events (World
  Cup, Euro, Copa América, AFCON, T20 WC) are pinned to their years.
- `active_tournaments(date)` → what's in season, ranked by importance.
- `featured_competition(date)` → the headline competition right now.
- `worldcup_active(date)` → drives the World Cup banner + mini-card visibility.
- `season_context(date)` is published to `assets/data/sports/season.json` and
  consumed by the dashboard (season-aware featured mini-card) and the README
  (`<!-- SEASON:START -->` block, refreshed daily).

## Rollover examples

| Date | Featured | Also active |
|------|----------|-------------|
| 28 Jun 2026 | FIFA World Cup | Wimbledon, T20 WC, MLB |
| 15 Sep 2026 | UEFA Champions League | Premier League, La Liga, Serie A |
| 20 Jan 2027 | UEFA Champions League | Australian Open, NBA |

So after the World Cup final the homepage automatically returns to the club
season and the next Grand Slam — no manual changes, refreshed by the daily and
30-minute workflows.
