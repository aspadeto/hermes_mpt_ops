#!/bin/bash
# Auto-commit script — DR MPT (KB + OPS)
# Commits and pushes any uncommitted changes to GitHub for both repos:
#   - hermes_mpt_kb  (conhecimento)  KB_DIR
#   - hermes_mpt_ops (engenharia)    OPS_DIR
# Usado pelo cron (a cada 10 min). Silencioso quando não há mudanças.

# ── Paths (com fallback, consistente com bootstrap.sh) ──────────────────────
HERMES_DATA="${HERMES_DATA:-/opt/data/hermes-data}"
OPS_DIR="${OPS_DIR:-$HERMES_DATA/mpt_workspace/hermes_mpt_ops}"
KB_DIR="${KB_DIR:-$HERMES_DATA/mpt_workspace/hermes_mpt_kb}"

REPOS=(
  "${KB_DIR}:hermes_mpt_kb"
  "${OPS_DIR}:hermes_mpt_ops"
)

for entry in "${REPOS[@]}"; do
  repo_path="${entry%%:*}"
  repo_name="${entry##*:}"

  cd "$repo_path" 2>/dev/null || { echo "ERRO [$repo_name]: pasta não existe: $repo_path"; continue; }

  # Sem mudanças → próximo
  if [[ -z $(git status --porcelain) ]]; then
    continue
  fi

  # Commit + push (com rebase para evitar conflitos)
  git add -A
  git commit -m "feat: sync automático $(date '+%Y-%m-%d %H:%M') [$repo_name]" 2>/dev/null || true

  # Se não há remote configurado, apenas commita localmente
  if ! git remote get-url origin >/dev/null 2>&1; then
    echo "ℹ️  [$repo_name] sem remote configurado — commit local apenas"
    continue
  fi

  git pull --rebase origin main 2>/dev/null || true
  git push origin main 2>&1 | grep -v "^$" | head -3

  echo "✅ [$repo_name] sync OK"
done

exit 0
