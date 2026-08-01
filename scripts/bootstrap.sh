#!/bin/bash
# ============================================================================
# bootstrap.sh — Reativação do ambiente Hermes PRT14 em host novo
# ============================================================================
# Uso:  bash bootstrap.sh [--restore-backup /caminho/do/backup.tar.gz]
#
# Pré-requisitos (Fase 1 do runbook):
#   - Docker + Tailscale instalados e autenticados
#   - Token GitHub disponível (GITHUB_TOKEN.txt na pasta atual OU variável
#     GITHUB_TOKEN exportada)
#
# Este script executa as Fases 2-6 do runbook. O backup do Drive (Fase 3) é
# opcional via --restore-backup — sem ele, o ambiente sobe "vazio" (sem
# memória/credenciais de providers).
# ============================================================================

set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
HERMES_DATA="${HERMES_DATA:-$HOME/hermes-data}"
OPS_URL="https://github.com/aspadeto/hermes_mpt_ops.git"
KB_URL="https://github.com/aspadeto/hermes_mpt_kb.git"
RESTORE_BACKUP=""

# ── Args ────────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --restore-backup) RESTORE_BACKUP="$2"; shift 2 ;;
    -h|--help) grep '^#' "$0" | head -30; exit 0 ;;
    *) echo "Argumento desconhecido: $1"; exit 1 ;;
  esac
done

log()  { echo -e "\n\033[1;34m== $* \033[0m"; }
ok()   { echo -e "\033[1;32m  ✓ $* \033[0m"; }
fail() { echo -e "\033[1;31m  ✗ $* \033[0m"; exit 1; }

# ── Fase 2: Clonar repositórios ─────────────────────────────────────────────
log "Fase 2: Clonando repositórios"

TOKEN="${GITHUB_TOKEN:-}"
if [[ -z "$TOKEN" && -f "$PWD/GITHUB_TOKEN.txt" ]]; then
  TOKEN=$(cat "$PWD/GITHUB_TOKEN.txt")
fi
[[ -z "$TOKEN" ]] && fail "Token GitHub não encontrado (exporte GITHUB_TOKEN ou coloque GITHUB_TOKEN.txt na pasta)"

mkdir -p "$HERMES_DATA"
cd "$HERMES_DATA"

if [[ ! -d hermes_mpt_ops/.git ]]; then
  git clone "https://${TOKEN}@github.com/aspadeto/hermes_mpt_ops.git" && ok "hermes_mpt_ops clonado"
else
  ok "hermes_mpt_ops já existe"
fi

if [[ ! -d hermes_mpt_kb/.git ]]; then
  git clone "https://${TOKEN}@github.com/aspadeto/hermes_mpt_kb.git" && ok "hermes_mpt_kb clonado"
else
  ok "hermes_mpt_kb já existe"
fi

# Credencial helper (push automático futuro)
git config --global credential.helper "store --file=${HERMES_DATA}/.git-credentials" || true
printf 'https://aspadeto:%s@github.com\n' "$TOKEN" > "${HERMES_DATA}/.git-credentials"
chmod 600 "${HERMES_DATA}/.git-credentials"
# Grava token p/ uso futuro
echo "$TOKEN" > "${HERMES_DATA}/GITHUB_TOKEN.txt"
chmod 600 "${HERMES_DATA}/GITHUB_TOKEN.txt"
ok "credenciais git configuradas"

# ── Fase 3: Restaurar identidade (backup do Drive) ──────────────────────────
log "Fase 3: Restaurando identidade"

if [[ -n "$RESTORE_BACKUP" ]]; then
  [[ -f "$RESTORE_BACKUP" ]] || fail "Backup não encontrado: $RESTORE_BACKUP"
  TMP=$(mktemp -d)
  tar xzf "$RESTORE_BACKUP" -C "$TMP"
  if [[ -d "$TMP/.hermes" ]]; then
    cp -a "$TMP/.hermes" "$HOME/.hermes" && ok "~/.hermes restaurado"
  fi
  if [[ -d "$TMP/data" ]]; then
    cp -a "$TMP/data/." "$HERMES_DATA/" 2>/dev/null || true
    ok "dados restaurados (tokens etc.)"
  fi
  rm -rf "$TMP"
else
  echo "  ⚠️  Sem backup informado — o ambiente subirá sem memória/credenciais de providers."
  echo "     Use --restore-backup /caminho/hermes-backup-*.tar.gz para restaurar."
fi

# ── Fase 4: Criar .env ──────────────────────────────────────────────────────
log "Fase 4: Criando .env do Docker"

ENV_FILE="$HERMES_DATA/hermes_mpt_ops/docker/.env"
if [[ ! -f "$ENV_FILE" ]]; then
  cp "$HERMES_DATA/hermes_mpt_ops/docker/.env-default" "$ENV_FILE"
  echo ""
  echo "  ⚠️  Edite $ENV_FILE e preencha:"
  echo "      HERMES_WEBUI_PASSWORD=  (senha do WebUI)"
  echo "      API_SERVER_KEY=         (openssl rand -hex 32)"
  echo ""
  read -r -p "  Pressione ENTER após editar (ou Ctrl+C para editar depois)... " _
else
  ok ".env já existe"
fi

# ── Fase 5: Subir ambiente ──────────────────────────────────────────────────
log "Fase 5: Subindo containers"

cd "$HERMES_DATA/hermes_mpt_ops/docker"
docker compose up -d
sleep 5
curl -s -o /dev/null -w "%{http_code}" http://localhost:8787 --connect-timeout 5 | grep -q 200 \
  && ok "WebUI respondendo em http://localhost:8787" \
  || echo "  ⚠️  WebUI ainda iniciando — verifique com: docker compose ps"

# ── Fase 6: Conectividade ───────────────────────────────────────────────────
log "Fase 6: Conectividade remota"

if command -v tailscale >/dev/null 2>&1; then
  sudo tailscale up --ssh 2>/dev/null || true
  sudo tailscale serve --bg http://127.0.0.1:8787 2>/dev/null || echo "  ⚠️  tailscale serve falhou (verifique a versão)"
  ok "Tailscale configurado (SSH + serve)"
else
  echo "  ⚠️  Tailscale não encontrado — pular"
fi

# ── Fim ─────────────────────────────────────────────────────────────────────
log "Bootstrap concluído!"
echo ""
echo "  WebUI:  https://as7-hermes-docker.tail15f7e7.ts.net (ou http://localhost:8787)"
echo "  Próximos passos:"
echo "    - Verificar Telegram: envie msg ao bot"
echo "    - Verificar pendências: $HERMES_DATA/hermes_mpt_ops/scripts/pendencia.py stats"
echo "    - Rodar backup inicial: $HERMES_DATA/hermes_mpt_ops/scripts/hermes-backup.py"
echo "    - Reconfigurar cron jobs (auto-commit, lembretes, backup)"
