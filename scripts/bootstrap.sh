#!/bin/bash
# ============================================================================
# bootstrap.sh — Reativação do ambiente Hermes em VM nativa (sem Docker)
# ============================================================================
# Uso:  bash bootstrap.sh [--restore-backup /caminho/do/backup.tar.gz]
#       [--skip-services] [--skip-cloudflare]
#
# Pré-requisitos (preparar ANTES no host):
#   - Ubuntu 24.04+ (ou derivado) com systemd
#   - Python 3.11+ instalado (apt install python3 python3-venv)
#   - uv instalado (curl -LsSf https://astral.sh/uv/install.sh | sh)
#   - Git configurado (user.name, user.email)
#   - cloudflared instalado e token NO DASHBOARD (não migra no backup)
#
# Este script executa:
#   Fase 1: Clonar repositórios (hermes_mpt_ops, hermes_mpt_kb)
#   Fase 2: Configurar credenciais Git
#   Fase 3: Restaurar ~/.hermes do backup (opcional)
#   Fase 4: Criar/atualizar .env do WebUI
#   Fase 5: Instalar deps Python (uv sync) + criar venvs
#   Fase 6: Configurar systemd --user services (gateway + webui)
#   Fase 7: Configurar cloudflared (se token disponível)
#   Fase 8: Backup inicial
# ============================================================================

set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
HERMES_DATA="${HERMES_DATA:-$HOME/hermes-data}"
OPS_URL="https://github.com/aspadeto/hermes_mpt_ops.git"
KB_URL="https://github.com/aspadeto/hermes_mpt_kb.git"
RESTORE_BACKUP=""
SKIP_SERVICES=false
SKIP_CLOUDFLARE=false

# ── Args ────────────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
  case "$1" in
    --restore-backup) RESTORE_BACKUP="$2"; shift 2 ;;
    --skip-services) SKIP_SERVICES=true; shift ;;
    --skip-cloudflare) SKIP_CLOUDFLARE=true; shift ;;
    -h|--help)
      grep '^#' "$0" | head -40
      exit 0
      ;;
    *) echo "Argumento desconhecido: $1"; exit 1 ;;
  esac
done

log()  { echo -e "\n\033[1;34m== $* \033[0m"; }
ok()   { echo -e "\033[1;32m  ✓ $* \033[0m"; }
warn() { echo -e "\033[1;33m  ⚠ $* \033[0m"; }
fail() { echo -e "\033[1;31m  ✗ $* \033[0m"; exit 1; }

# ── Verificações iniciais ───────────────────────────────────────────────────
log "Verificando pré-requisitos"

command -v python3 >/dev/null 2>&1 || fail "python3 não encontrado (apt install python3)"
command -v git >/dev/null 2>&1 || fail "git não encontrado (apt install git)"
command -v uv >/dev/null 2>&1 || warn "uv não encontrado — instalando via script oficial..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
  command -v uv >/dev/null 2>&1 || fail "uv ainda não disponível após instalação"

# Git user/email
git config --global user.name >/dev/null 2>&1 || fail "Configure git user.name (git config --global user.name 'Seu Nome')"
git config --global user.email >/dev/null 2>&1 || fail "Configure git user.email (git config --global user.email 'email@exemplo.com')"

ok "Pré-requisitos OK"

# ── Fase 1: Clonar repositórios ─────────────────────────────────────────────
log "Fase 1: Clonando repositórios"

mkdir -p "$HERMES_DATA"
cd "$HERMES_DATA"

# Token GitHub (precisa de permissão para repos privados)
TOKEN="${GITHUB_TOKEN:-}"
if [[ -z "$TOKEN" && -f "$PWD/GITHUB_TOKEN.txt" ]]; then
  TOKEN=$(cat "$PWD/GITHUB_TOKEN.txt")
fi
[[ -z "$TOKEN" ]] && warn "GITHUB_TOKEN não encontrado — clones públicos funcionarão, privados falharão"

# Clone hermes_mpt_ops
if [[ ! -d hermes_mpt_ops/.git ]]; then
  if [[ -n "$TOKEN" ]]; then
    git clone "https://aspadeto:${TOKEN}@github.com/aspadeto/hermes_mpt_ops.git" && ok "hermes_mpt_ops clonado (privado)"
  else
    git clone "https://github.com/aspadeto/hermes_mpt_ops.git" && ok "hermes_mpt_ops clonado (público)"
  fi
else
  ok "hermes_mpt_ops já existe"
fi

# Clone hermes_mpt_kb
if [[ ! -d hermes_mpt_kb/.git ]]; then
  if [[ -n "$TOKEN" ]]; then
    git clone "https://aspadeto:${TOKEN}@github.com/aspadeto/hermes_mpt_kb.git" && ok "hermes_mpt_kb clonado (privado)"
  else
    git clone "https://github.com/aspadeto/hermes_mpt_kb.git" && ok "hermes_mpt_kb clonado (público)"
  fi
else
  ok "hermes_mpt_kb já existe"
fi

# ── Fase 2: Configurar credenciais Git ──────────────────────────────────────
log "Fase 2: Configurando credenciais Git"

# Helper usa arquivo em /home/hermes/ (não no HERMES_DATA) — portátil entre máquinas
GIT_CREDS_FILE="/home/hermes/.git-credentials"
if [[ -n "$TOKEN" ]]; then
  git config --global credential.helper "store --file=$GIT_CREDS_FILE" || true
  printf 'https://aspadeto:%s@github.com\n' "$TOKEN" > "$GIT_CREDS_FILE"
  chmod 600 "$GIT_CREDS_FILE"
  # Também salva token para uso futuro (scripts que precisam)
  echo "$TOKEN" > "/home/hermes/GITHUB_TOKEN.txt"
  chmod 600 "/home/hermes/GITHUB_TOKEN.txt"
  ok "Credenciais Git configuradas em $GIT_CREDS_FILE"
else
  warn "Sem token — push para repos privados não funcionará"
fi

# ── Fase 3: Restaurar ~/.hermes do backup ───────────────────────────────────
log "Fase 3: Restaurando identidade (backup do Drive)"

if [[ -n "$RESTORE_BACKUP" ]]; then
  [[ -f "$RESTORE_BACKUP" ]] || fail "Backup não encontrado: $RESTORE_BACKUP"
  TMP=$(mktemp -d)
  tar xzf "$RESTORE_BACKUP" -C "$TMP"
  if [[ -d "$TMP/.hermes" ]]; then
    # Backup inclui ~/.hermes/ (config.yaml, auth.json, skills, etc.)
    cp -a "$TMP/.hermes" "$HOME/.hermes" && ok "~/.hermes restaurado"
  fi
  if [[ -d "$TMP/host-secrets" ]]; then
    # host-secrets: webui.env, himalaya/, git-credentials, GITHUB_TOKEN.txt
    if [[ -f "$TMP/host-secrets/webui.env" ]]; then
      mkdir -p "$HOME/hermes-webui"
      cp "$TMP/host-secrets/webui.env" "$HOME/hermes-webui/.env"
      ok "WebUI .env restaurado (inclui HERMES_WEBUI_PASSWORD)"
    fi
    if [[ -d "$TMP/host-secrets/himalaya" ]]; then
      mkdir -p "$HOME/.config/himalaya"
      cp -a "$TMP/host-secrets/himalaya/." "$HOME/.config/himalaya/"
      ok "Himalaya config restaurado"
    fi
    if [[ -f "$TMP/host-secrets/git-credentials" ]]; then
      cp "$TMP/host-secrets/git-credentials" "$GIT_CREDS_FILE"
      chmod 600 "$GIT_CREDS_FILE"
      ok "Git credentials restaurado"
    fi
    if [[ -f "$TMP/host-secrets/GITHUB_TOKEN.txt" ]]; then
      cp "$TMP/host-secrets/GITHUB_TOKEN.txt" "/home/hermes/GITHUB_TOKEN.txt"
      chmod 600 "/home/hermes/GITHUB_TOKEN.txt"
      ok "GITHUB_TOKEN restaurado"
    fi
  fi
  rm -rf "$TMP"
else
  warn "Sem backup informado — o ambiente subirá sem memória/credenciais de providers."
  echo "     Use --restore-backup /caminho/hermes-backup-*.tar.gz para restaurar."
  echo "     O backup do Drive roda diariamente às 03:00 UTC (cron)."
fi

# ── Fase 4: Criar/atualizar .env do WebUI ───────────────────────────────────
log "Fase 4: Configurando .env do WebUI"

WEBUI_ENV="$HOME/hermes-webui/.env"
if [[ ! -f "$WEBUI_ENV" ]]; then
  cat > "$WEBUI_ENV" <<'EOF'
# Hermes Web UI -- configuração VM nativa
# Preencha os valores abaixo

# Senha do WebUI (obrigatória)
HERMES_WEBUI_PASSWORD=

# Diretório do agente (onde está run_agent.py / config.yaml)
HERMES_WEBUI_AGENT_DIR=/home/hermes/.hermes/hermes-agent

# Python a usar (venv do agente)
HERMES_WEBUI_PYTHON=/home/hermes/.hermes/hermes-agent/venv/bin/python

# Host/port do servidor WebUI
HERMES_WEBUI_HOST=127.0.0.1
HERMES_WEBUI_PORT=8787
EOF
  warn "Criado $WEBUI_ENV — EDITE e preencha HERMES_WEBUI_PASSWORD"
  echo "     Também verifique HERMES_WEBUI_AGENT_DIR e HERMES_WEBUI_PYTHON"
  read -r -p "  Pressione ENTER após editar (ou Ctrl+C para editar depois)... " _
else
  ok "$WEBUI_ENV já existe"
fi

# ── Fase 5: Instalar deps Python ────────────────────────────────────────────
log "Fase 5: Instalando dependências Python (uv sync)"

# Agente principal
if [[ -d "$HOME/.hermes/hermes-agent" ]]; then
  cd "$HOME/.hermes/hermes-agent"
  uv sync --frozen 2>/dev/null || uv sync
  ok "Agente: deps instaladas"
else
  warn "Diretório do agente não encontrado em $HOME/.hermes/hermes-agent"
fi

# WebUI
if [[ -d "$HOME/hermes-webui" ]]; then
  cd "$HOME/hermes-webui"
  uv sync --frozen 2>/dev/null || uv sync
  ok "WebUI: deps instaladas"
else
  warn "Diretório do WebUI não encontrado em $HOME/hermes-webui"
fi

# OPS scripts (hermes-backup.py, pendencia.py, etc.)
cd "$HERMES_DATA/hermes_mpt_ops"
if [[ -f "pyproject.toml" || -f "requirements.txt" ]]; then
  uv sync --frozen 2>/dev/null || uv sync
  ok "OPS: deps instaladas"
else
  # Scripts usam stdlib + libs já no agente/WebUI
  ok "OPS: sem deps dedicadas (usa stdlib)"
fi

# ── Fase 6: Configurar systemd --user services ──────────────────────────────
if [[ "$SKIP_SERVICES" == "true" ]]; then
  warn "Pulando configuração de services (--skip-services)"
else
  log "Fase 6: Configurando systemd --user services"

  # Habilitar lingering para user services subirem no boot
  loginctl enable-linger "$USER" 2>/dev/null || warn "loginctl enable-linger falhou (precisa sudo?)"

  # Recarregar daemon
  systemctl --user daemon-reload

  # hermes-gateway (já deve existir em ~/.config/systemd/user/)
  if [[ -f "$HOME/.config/systemd/user/hermes-gateway.service" ]]; then
    systemctl --user enable hermes-gateway 2>/dev/null && ok "hermes-gateway enabled"
    systemctl --user restart hermes-gateway 2>/dev/null && ok "hermes-gateway reiniciado"
  else
    warn "hermes-gateway.service não encontrado em ~/.config/systemd/user/"
  fi

  # hermes-webui (criado hoje)
  if [[ -f "$HOME/.config/systemd/user/hermes-webui.service" ]]; then
    systemctl --user enable hermes-webui 2>/dev/null && ok "hermes-webui enabled"
    systemctl --user restart hermes-webui 2>/dev/null && ok "hermes-webui reiniciado"
  else
    warn "hermes-webui.service não encontrado"
  fi

  # Verificar status
  sleep 2
  systemctl --user is-active hermes-gateway >/dev/null 2>&1 && ok "gateway: ATIVO" || warn "gateway: INATIVO"
  systemctl --user is-active hermes-webui >/dev/null 2>&1 && ok "webui: ATIVO (porta 8787)" || warn "webui: INATIVO"
fi

# ── Fase 7: Cloudflare Tunnel ───────────────────────────────────────────────
if [[ "$SKIP_CLOUDFLARE" == "true" ]]; then
  warn "Pulando Cloudflare Tunnel (--skip-cloudflare)"
else
  log "Fase 7: Cloudflare Tunnel (cloudflared)"

  if command -v cloudflared >/dev/null 2>&1; then
    if [[ -f "/etc/cloudflared/token" ]]; then
      # Verificar se serviço systemd existe e está ativo
      if systemctl is-active cloudflared >/dev/null 2>&1; then
        ok "cloudflared já rodando como serviço system (token em /etc/cloudflared/token)"
      else
        warn "Token existe mas serviço não está ativo — ative com: sudo systemctl enable --now cloudflared"
      fi
    else
      warn "cloudflared instalado mas SEM token em /etc/cloudflared/token"
      echo "     Configure no Dashboard Cloudflare (Zero Trust → Tunnels)"
      echo "     Depois: sudo cloudflared service install <TOKEN>"
    fi
  else
    warn "cloudflared NÃO instalado — instale e configure token no Dashboard"
    echo "     curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared"
    echo "     chmod +x /usr/local/bin/cloudflared"
    echo "     sudo cloudflared service install <TOKEN_DO_DASHBOARD>"
  fi
fi

# ── Fase 8: Backup inicial ──────────────────────────────────────────────────
log "Fase 8: Backup inicial (Drive)"

if [[ -f "$HERMES_DATA/hermes_mpt_ops/scripts/hermes-backup.py" ]]; then
  cd "$HERMES_DATA/hermes_mpt_ops"
  # hermes-backup.py já lê config e faz backup para Drive
  python3 scripts/hermes-backup.py 2>&1 | tail -5
  ok "Backup executado (verifique logs acima)"
else
  warn "hermes-backup.py não encontrado — backup manual depois"
fi

# ── Fim ─────────────────────────────────────────────────────────────────────
log "Bootstrap concluído!"

echo ""
echo "  Resumo:"
echo "    - Repositórios: $HERMES_DATA/hermes_mpt_ops, hermes_mpt_kb"
echo "    - Credenciais Git: $GIT_CREDS_FILE"
echo "    - WebUI: http://127.0.0.1:8787 (senha no .env)"
echo "    - Gateway: systemd --user (hermes-gateway)"
echo "    - WebUI service: systemd --user (hermes-webui)"
echo "    - Cloudflare Tunnel: https://webui-01.asideia.net (via cloudflared)"
echo ""
echo "  Próximos passos:"
echo "    - Verificar WebUI: curl -s http://127.0.0.1:8787/health"
echo "    - Verificar Telegram: envie msg ao bot"
echo "    - Verificar pendências: $HERMES_DATA/hermes_mpt_ops/scripts/pendencia.py stats"
echo "    - Cron jobs: hermes config set cron.enabled true (se desativado)"
echo ""
echo "  ⚠️  IMPORTANTE:"
echo "    - Token Cloudflare NÃO migra no backup — configure no Dashboard"
echo "    - GITHUB_TOKEN em /home/hermes/GITHUB_TOKEN.txt"
echo "    - webui.env em $HOME/hermes-webui/.env (inclui HERMES_WEBUI_PASSWORD)"