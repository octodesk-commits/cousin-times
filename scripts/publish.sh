#!/usr/bin/env bash
set -euo pipefail

DATE="${1:-$(TZ=Europe/Dublin date +%F)}"
REPO="/home/adrian/cousin-times"

python3 "$REPO/scripts/build_site.py" "$DATE"
cd "$REPO"

git add index.html archive.html sitemap.xml editions CNAME robots.txt .nojekyll scripts
if git diff --cached --quiet; then
  echo "No site changes for $DATE"
  exit 0
fi

git commit -m "Publish The Cousin Times $DATE"
git push origin main
echo "Published The Cousin Times $DATE"
