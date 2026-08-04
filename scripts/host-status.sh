#!/bin/bash
# host-status.sh — Verifica status do Docker e dos containers no host
#
# Uso (do container):  ./host-status.sh
# O script roda via SSH no host (alias 'host' do ~/.ssh/config).
# Sem sudo — usa o grupo docker do usuário hermes.

set -uo pipefail

HOST_ALIAS="${HOST_ALIAS:-host}"
COMPOSE_DIR="${COMPOSE_DIR:-~/hermes-data/hermes_mpt_ops/docker}"

echo "=== 🔍 Status do Docker e containers no host ==="
echo "Data/hora: $(ssh -o ConnectTimeout=5 "$HOST_ALIAS" 'date "+%Y-%m-%d %H:%M:%S %Z"')"
echo

echo "--- 1. Serviço Docker (systemd) ---"
ssh "$HOST_ALIAS" 'systemctl is-active docker 2>/dev/null || echo "inativo/desconhecido"'
echo

echo "--- 2. Containers (docker ps) ---"
ssh "$HOST_ALIAS" 'docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"'
echo

echo "--- 3. Containers do compose (saúde) ---"
ssh "$HOST_ALIAS" "cd $COMPOSE_DIR && docker compose ps 2>&1"
echo

echo "--- 4. Recursos do host ---"
ssh "$HOST_ALIAS" 'echo "Uptime: $(uptime -p)"; echo "Disco: $(df -h / | tail -1 | awk '\''{print $3" usado de "$2" ("$5")"}'\'')"; echo "Mem: $(free -h | awk '\''/Mem:/{print $3" usado de "$2}'\'')"'
echo

echo "--- 5. Health check WebUI + API ---"
WEBUI=$(ssh "$HOST_ALIAS" 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 4 http://localhost:8787 2>/dev/null || echo "sem resposta"')
API=$(ssh "$HOST_ALIAS" 'curl -s -o /dev/null -w "%{http_code}" --connect-timeout 4 http://localhost:8642/health 2>/dev/null || echo "sem resposta"')
echo "WebUI (8787): HTTP $WEBUI"
echo "API   (8642): HTTP $API"

echo
echo "=== ✅ Status verificado ==="
