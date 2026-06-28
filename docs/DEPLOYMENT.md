# Deployment

Production has **two independent parts**:

1. **Data pipeline** (HF dataset refresh + daily model training + JSON). Runs in
   **GitHub Actions** — needs no hosting. With the `HF_TOKEN` secret set, it is
   already production-ready. Trigger it from the Actions tab → *Sports Daily
   Pipeline* → *Run workflow*, or wait for the crons (daily 03:20 UTC, live every
   30 min).
2. **Website** (the `/sports/` dashboard). Static Jekyll output — this is the
   only part that needs hosting.

> ⚠️ Asset paths are **root-absolute** (`/assets/...`, permalink `/sports/`), so
> the site must be served at a **domain root** (apex or subdomain), not at a
> `*.github.io/<repo>/` subpath.

## Recommended: GitHub Pages

Your main site is already Jekyll on Pages with the `ruslanmv.com` domain, so Pages
is the natural fit. Two routes:

### Route A — serve at `ruslanmv.com/sports/` (merge into the main site)
Matches the product URL and reuses your existing Pages + domain.

```bash
# from the sports-trends repo, copy the section into your site repo:
./scripts/sync_to_site.sh ../ruslanmv.github.io
```
This copies `sports/`, `_includes/sports/`, `_layouts/sports*.html`,
`assets/{css,js,images,data}/sports*`, then you commit in `ruslanmv.github.io`.
To keep it fresh, add a step in this repo's daily workflow to push the generated
`assets/data/sports/*.json` to `ruslanmv.github.io` (or run the sync in CI).

### Route B — standalone on a subdomain (`sports.ruslanmv.com`)
No changes to your main site. Already wired:
1. Repo **Settings → Pages → Source = "GitHub Actions"**.
2. (custom domain) **Settings → Pages → Custom domain =** `sports.ruslanmv.com`,
   then add a DNS `CNAME` record: `sports` → `ruslanmv.github.io`.
3. Merge to `main` (or run *Sports Deploy (GitHub Pages)* manually). The workflow
   builds the site, adds a root → `/sports/` redirect, and deploys.

## Alternative: Vercel
A `vercel.json` is included (Ruby/Jekyll build). Import the repo at vercel.com,
or:
```bash
npm i -g vercel && vercel --prod
```
Point a domain/subdomain at Vercel in its dashboard. Note: the apex `ruslanmv.com`
can only point to one host, so use a subdomain if Pages keeps the apex.

## Summary
| Goal | Do this |
|------|---------|
| Live data + daily models | ✅ already done (Actions + `HF_TOKEN`) |
| Site at `ruslanmv.com/sports/` | Route A (sync into `ruslanmv.github.io`) |
| Isolated site, no main-site changes | Route B (Pages + `sports.ruslanmv.com`) |
| Preview deploys / separate stack | Vercel |
