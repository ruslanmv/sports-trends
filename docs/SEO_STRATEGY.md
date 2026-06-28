# SEO Strategy

## Programmatic pages

- `sports/match/{slug}.md` — one page per fixture (`seo/generate_match_pages.py`),
  with title/description (`seo/generate_meta_descriptions.py`) and **SportsEvent**
  JSON-LD (`seo/generate_json_ld.py`) for rich results.
- `sports/league/{slug}.md` — one page per league (`seo/generate_league_pages.py`).
- `sports/sitemap-sports.xml` — static + per-match URLs (`seo/generate_sitemap.py`).

## Structured data

`_includes/sports/json-ld.html` emits `page.jsonld` (a SportsEvent object) when a
page provides it, else a WebSite object.

## Social / sharing

- `social/generate_og_images.py` — 1200×630 SVG OG cards per match.
- `social/generate_share_text.py` — X / WhatsApp share intents.
- `assets/js/sports-share.js` — native share, X/WhatsApp, copy-link.

Pages are generated daily by `sports-generate-seo-pages.yml` from `tomorrow.json`.
