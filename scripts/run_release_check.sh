#!/bin/bash
# run_release_check.sh — run release detection, then commit & push any changes
set -e
cd "$(dirname "$0")/.."
python3 scripts/update_releases.py
git add data/news.json data/story.json data/release_state.json data/apps.json
if git diff --cached --quiet; then
  echo "NO_DATA_CHANGES"
else
  git commit -m "chore(next): record released app updates from store check" >/dev/null
  git push >/dev/null 2>&1 && echo "PUSHED" || echo "PUSH_FAILED_BUT_COMMITTED"
fi