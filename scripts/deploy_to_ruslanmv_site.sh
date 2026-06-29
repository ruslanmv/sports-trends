#!/usr/bin/env bash
# Production deploy is handled entirely inside THIS repository by the
# "Sports Deploy (GitHub Pages)" workflow (.github/workflows/sports-deploy.yml),
# which regenerates the public JSON, builds the Jekyll site and publishes it to
# https://ruslanmv.com/sports-trends/ . No assets are ever copied into the
# ruslanmv.github.io repo, so this script is intentionally a no-op pointer.
#
# To deploy on demand: trigger the "Sports Deploy (GitHub Pages)" workflow
# (Actions tab → Run workflow), or run `make build` locally to produce _site/.
set -euo pipefail

cat <<'MSG'
Nothing to do here.

Production is served from this repo via GitHub Pages:
  workflow : .github/workflows/sports-deploy.yml  (push to main / schedule / manual)
  local    : make build   ->   ./_site
  docs     : docs/DEPLOYMENT.md
MSG
