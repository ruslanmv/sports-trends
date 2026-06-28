#!/usr/bin/env bash
# Copy the /sports/ section into the main Jekyll site (e.g. ruslanmv.github.io)
# so it serves at ruslanmv.com/sports/. Run from the sports-trends repo root.
#
# Usage: ./scripts/sync_to_site.sh /path/to/ruslanmv.github.io
set -euo pipefail

DEST="${1:?Usage: sync_to_site.sh <path-to-site-repo>}"
[ -d "$DEST" ] || { echo "Destination not found: $DEST"; exit 1; }

echo "Syncing sports section -> $DEST"
mkdir -p "$DEST/_includes/sports" "$DEST/_layouts" \
         "$DEST/assets/css" "$DEST/assets/js" \
         "$DEST/assets/images/sports" "$DEST/assets/data/sports" \
         "$DEST/sports"

# Pages + components
cp -r sports/. "$DEST/sports/"
cp -r _includes/sports/. "$DEST/_includes/sports/"
cp _layouts/sports*.html "$DEST/_layouts/"
# Assets (namespaced to avoid clobbering the main site)
cp assets/css/sports*.css "$DEST/assets/css/"
cp assets/js/sports*.js "$DEST/assets/js/"
cp -r assets/images/sports/. "$DEST/assets/images/sports/"
cp -r assets/data/sports/. "$DEST/assets/data/sports/"

echo "Done. Review and commit inside $DEST:"
echo "  cd $DEST && git add sports _includes/sports _layouts assets && git commit -m 'Add sports section' && git push"
