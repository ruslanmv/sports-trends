# Deployment — GitHub Pages (this repo only)

Everything is committed and served from **this repo** (`ruslanmv/sports-trends`).
Nothing is ever pushed into `ruslanmv.github.io`.

Production has two independent parts:

1. **Data pipeline** (HF dataset refresh + daily model training + JSON). Runs in
   **GitHub Actions** — no hosting needed. With the `HF_TOKEN` secret set it is
   already live (daily 03:20 UTC + every 30 min). Trigger manually from the
   Actions tab if you want a run now.
2. **Website** — a GitHub Pages **project site** for this repo, published at
   **https://ruslanmv.com/sports-trends/** (a project page served under the user
   site's custom domain).

## Why it was 404'ing — and the fix

A project page lives at the `/sports-trends/` subpath, but the site previously
used root-absolute paths (`/assets/...`) and had no page at the project root, so
`ruslanmv.com/sports-trends/` had nothing to serve.

Fixed by making the site **baseurl-aware**:
- `_config.yml`: `url: https://ruslanmv.com`, `baseurl: /sports-trends`.
- The dashboard now has `permalink: /`, so it renders at the project root
  (`/sports-trends/`).
- All asset/link references use Jekyll's `relative_url` (or paths relative to the
  CSS file), and the JS reads a `<meta name="sports-base">` to build JSON/fetch
  URLs. So every request resolves under `/sports-trends/`.

## Enable it (one-time)

1. Push this branch to `main`.
2. Repo **Settings → Pages → Source = "GitHub Actions"**.
3. The **Sports Deploy (GitHub Pages)** workflow builds the Jekyll site (with
   fresh JSON) and publishes it. Done — visit `https://ruslanmv.com/sports-trends/`.

No DNS changes are required: the project page is automatically available under
the existing `ruslanmv.com` custom domain of the user site.

## Notes

- The daily/30-min workflows commit the generated `assets/data/sports/*.json`
  into this repo; the deploy workflow then republishes the site.
- A `vercel.json` is included if you ever want a Vercel preview, but the
  supported production target is GitHub Pages on this repo.
