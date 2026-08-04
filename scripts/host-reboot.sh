#!/bin/bash
# host-reboot.sh — Reinicia o HOST (máquina inteira)
#
# Uso (do container):  ./host-reboot.sh [--force]
# Sem --force, pede confirmação. ⚠️  DERRUBA TUDO (Docker, Hermes, WebUI).
# Requer sudo NOPASSWD configurado no host (ver docs/RUNBOOK-SSH-HOST.md Fase 5).
# ⚠️  Após o reboot, o Hermes volta sozinho? Depende do restart policy
#      (unless-stopped) e se o docker inicia com o sistema.

set -uo pipefail

HOST_ALIAS="${HOST_ALIAS:-host}"
FORCE="${1:-}"

if [[ "$FORCE" != "--force" ]]; then
  echo "⚠️⚠️  ISSO VAI REINICIAR O HOST INTEIRO (hermes-01)."
  echo "    Docker, Hermes e WebUI ficarão indisponíveis até o host voltar."
  read -r -p "Tem CERTEZA? Digite 'REINICIAR' para confirmar: " resp
  [[ "$resp" == "REINICIAR" ]] || { echo "Cancelado."; exit 1; }
fi

echo "=== 🔴 Reiniciando o host ==="
ssh -o ConnectTimeout=5 "$HOST_ALIAS" 'sudo -n /sbin/reboot 2>&1 || { echo "Falha: sudo reboot indisponível (NOPASSWD configurado?)"; exit 1; }'

echo "Comando de reboot enviado. O host está reiniciando..."
echo "A conexão SSH será perdida. O host deve voltar em 1-2 minutos."

# Aguarda o host voltar (até 3 min) e valida
echo "--- Aguardando host voltar ---"
for i in $(seq 1 36); do
  sleep 5
  if ssh -o ConnectTimeout=3 -o BatchMode=yes "$HOST_ALIAS" 'echo up' 2>/dev/null | grep -q up; then
    echo "✅ Host voltou após ~$((i * 5))s"
    break
  fi
  if [[ $i -eq 36 ]]; then
    echo "⚠️  Host não respondeu em 3 min. Verifique manualmente."
    exit 1
  fi
done

echo "--- Verificando Docker e containers ---"
ssh "$HOST_ALIAS" 'docker ps --format "{{.Names}}: {{.Status}}" 2>&1'
echo

echo "--- Health check ---"
sleep 10
ssh "$HOST_ALIAS" 'curl -s -o /dev/null -w "WebUI (8787): HTTP %{http_code}\n" --connect-timeout 5 http://localhost:8787 2>/dev/null || echo "WebUI: sem resposta"'
ssh "$HOST_ALIAS" 'curl -s -o /dev/null -w "API   (8642): HTTP %{http_code}\n" --connect-timeout 5 http://localhost:8642/health 2>/dev/null || echo "API: sem resposta"'

echo
echo "=== ✅ Host reiniciado e verificado ==="
