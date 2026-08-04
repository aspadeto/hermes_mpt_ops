#!/bin/bash
# host-restart.sh — Reinicia os containers Docker no host
#
# Uso (do container):  ./host-restart.sh [--force]
# Sem --force, pede confirmação antes de reiniciar.
# Sem sudo — usa o grupo docker do usuário hermes.

set -uo pipefail

HOST_ALIAS="${HOST_ALIAS:-host}"
COMPOSE_DIR="${COMPOSE_DIR:-~/hermes-data/hermes_mpt_ops/docker}"
FORCE="${1:-}"

if [[ "$FORCE" != "--force" ]]; then
  echo "⚠️  Isso vai REINICIAR os containers (hermes-agent, hermes-webui)."
  echo "    O agente ficará indisponível por alguns segundos."
  read -r -p "Continuar? [s/N] " resp
  [[ "$resp" =~ ^[sSyY] ]] || { echo "Cancelado."; exit 1; }
fi

echo "=== 🔄 Reiniciando containers no host ==="
ssh -o ConnectTimeout=5 "$HOST_ALIAS" "cd $COMPOSE_DIR && docker compose restart 2>&1"
echo

echo "--- Aguardando serviços subirem (10s) ---"
sleep 10

echo "--- Estado pós-restart ---"
ssh "$HOST_ALIAS" "cd $COMPOSE_DIR && docker compose ps 2>&1"
echo

echo "--- Health check ---"
ssh "$HOST_ALIAS" 'curl -s -o /dev/null -w "WebUI (8787): HTTP %{http_code}\n" --connect-timeout 5 http://localhost:8787 2>/dev/null || echo "WebUI: sem resposta"'
ssh "$HOST_ALIAS" 'curl -s -o /dev/null -w "API   (8642): HTTP %{http_code}\n" --connect-timeout 5 http://localhost:8642/health 2>/dev/null || echo "API: sem resposta"'

echo
echo "=== ✅ Containers reiniciados ==="
