#!/usr/bin/env bash
# Set the GitHub Actions secrets used by the sports-trends workflows.
#
# A token is a SECRET — never commit it or put it in an Actions *variable*.
# This script sets it via the GitHub CLI without it ever touching the repo.
#
# Prereqs: GitHub CLI (https://cli.github.com) authenticated with `gh auth login`.
#
# Usage:
#   export HF_TOKEN=hf_xxx                       # your Hugging Face write token
#   # optional provider keys:
#   export SPORTS_API_FOOTBALL_KEY=...           # etc.
#   ./scripts/setup_github_secrets.sh [owner/repo]
#
# Defaults to ruslanmv/sports-trends.
set -euo pipefail

REPO="${1:-ruslanmv/sports-trends}"

set_secret() {
  local name="$1" value="${2:-}"
  if [[ -z "$value" ]]; then
    echo "skip  $name (not set in environment)"
    return
  fi
  printf '%s' "$value" | gh secret set "$name" --repo "$REPO" --body -
  echo "ok    $name -> $REPO"
}

echo "Setting Actions secrets on $REPO ..."
set_secret HF_TOKEN                "${HF_TOKEN:-}"
set_secret SPORTS_API_KEY          "${SPORTS_API_KEY:-}"
set_secret SPORTS_API_FOOTBALL_KEY "${SPORTS_API_FOOTBALL_KEY:-}"
set_secret SPORTS_BASKETBALL_API_KEY "${SPORTS_BASKETBALL_API_KEY:-}"
set_secret SPORTS_TENNIS_API_KEY   "${SPORTS_TENNIS_API_KEY:-}"
set_secret SPORTS_CRICKET_API_KEY  "${SPORTS_CRICKET_API_KEY:-}"

echo "Done. Verify with: gh secret list --repo $REPO"
