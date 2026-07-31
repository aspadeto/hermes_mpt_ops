#!/bin/bash
# Auto-commit script for wiki-prt14
# Commits and pushes any uncommitted changes to GitHub
WIKI_PATH="${WIKI_PATH:-/opt/data/hermes-data/wiki}"

cd "$WIKI_PATH" || exit 1

# Check if there are any changes
if [[ -z $(git status --porcelain) ]]; then
    # No changes, nothing to do
    exit 0
fi

# Add all changes, commit, and push
git add -A
git commit -m "feat: sync automático $(date '+%Y-%m-%d %H:%M')"
git pull --rebase origin main 2>/dev/null || true
git push origin main 2>&1

exit 0
