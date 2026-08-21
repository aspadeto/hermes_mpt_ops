# RUNBOOK — Manutenção da VM (modelo nativo)

Operações do dia a dia no ambiente **VM nativa** (sem Docker, sem Tailscale).
Criado em 07/08/2026 junto com a migração container → VM.

> Antes (até 06/08/2026) a administração era feita via **SSH do container para o
> host** (`ssh host ... docker ...`) — ver `RUNBOOK-SSH-HOST.md` (OBSOLETO). Agora o
> agente roda **na própria VM**: os comandos são executados diretamente, sem SSH.

---

## 1. Componentes e como gerenciar

| Componente | Processo | Gestão |
|-----------|----------|--------|
| **Gateway** (Telegram + API, porta 20241) | user service `hermes-gateway.service` | `systemctl --user ...` |
| **WebUI** (porta 8787) | user service `hermes-webui.service` (`bootstrap.py --no-browser --host 127.0.0.1 8787`) | `systemctl --user ...` |
| **Dashboard** (porta 9119) | user service `hermes-dashboard.service` (`dashboard --host 0.0.0.0 --port 9119`) | `systemctl --user ...` |
| **Túnel Cloudflare** | system service `cloudflared.service` (root) | `sudo systemctl ...` |
| **Cron do Hermes** | scheduler dentro do gateway | `hermes cron list` |

**Fatos da migração (07/08/2026) e sistema de units:**
- Units em `~/.config/systemd/user/`: `hermes-gateway.service`, `hermes-webui.service`,
  `hermes-dashboard.service` (todas enabled, Linger=yes → sobem no boot).
- ExecStart gateway: `~/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run`.
- ExecStart WebUI: `%h/.hermes/hermes-agent/venv/bin/python %h/hermes-webui/bootstrap.py --no-browser --foreground --host 127.0.0.1 8787`.
- ExecStart Dashboard: `%h/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main dashboard --no-open --host 0.0.0.0 --port 9119 --skip-build`.
- ⚠️ WebUI e Dashboard agora são **user services systemd** — o antigo daemon via
  `ctl.sh` (e o `hermes-webui/server.py` via start.sh) foi descontinuado.
- `/opt/data/hermes-data` é diretório real da VM (não bind mount).

---

## 2. Comandos de rotina

```bash
# Gateway — status, logs, restart
systemctl --user status hermes-gateway.service
journalctl --user -u hermes-gateway --no-pager -n 100        # logs
systemctl --user restart hermes-gateway.service              # reiniciar gateway

# WebUI — status, logs, restart
systemctl --user status hermes-webui.service
journalctl --user -u hermes-webui --no-pager -n 100          # logs
systemctl --user restart hermes-webui.service                # reiniciar webui

# Dashboard — status, logs, restart
systemctl --user status hermes-dashboard.service
journalctl --user -u hermes-dashboard --no-pager -n 100
systemctl --user restart hermes-dashboard.service

# Túnel
systemctl status cloudflared
journalctl -u cloudflared --no-pager -n 50
sudo systemctl restart cloudflared

# Cron
hermes cron list        # jobs ativos (todos enabled: true)
```

## 3. Portas

| Porta | Serviço | Escopo |
|-------|---------|--------|
| 22 | SSH | rede (0.0.0.0) |
| 8787 | WebUI | **só 127.0.0.1** (externo via Cloudflare Tunnel) |
| 9119 | Dashboard | **0.0.0.0** (externo via Cloudflare Tunnel/Access) |
| 20241 | API interna do gateway | só 127.0.0.1 |

## 4. Backup

- Diário 03:00 UTC → Google Drive (pasta `HermesBackup`), via `hermes-backup.py`.
- Exclui repos git (KB/OPS) e `.google-venv`.
- Testar manualmente: `hermes_mpt_ops/scripts/hermes-backup.py` (rodar e conferir upload).
- O wrapper de cron `~/.hermes/scripts/hermes-backup.py` chama o script real (path na
  variável `OPS_SCRIPTS` do cabeçalho). Detalhes completos: `BACKUP-RESTAURACAO.md`.

## 5. Auto-commit (cron de 10 min)

- `hermes_mpt_ops/scripts/kb-auto-commit.sh` commita+push KB e OPS quando há mudanças.
- Define `HERMES_DATA`/`OPS_DIR`/`KB_DIR` no cabeçalho **com fallback**
  (`HERMES_DATA="${HERMES_DATA:-/opt/data/hermes-data}"`,
  `OPS_DIR="$HERMES_DATA/mpt_workspace/hermes_mpt_ops"`,
  `KB_DIR="$HERMES_DATA/mpt_workspace/hermes_mpt_kb"`). **Não remover o fallback** —
  sem ele o cron roda com variáveis vazias e falha silenciosamente.
- Testar: `bash hermes_mpt_ops/scripts/kb-auto-commit.sh`.

## 6. Pendências conhecidas (pós-migração)

- ~~`browser.cdp_url: ws://browser:3000/`~~ — **resolvido** (07/08/2026, pendência
  #13): zerado para `''`, browser via Nous Tool Gateway + Chromium local.
- `~/hermes-webui/.env` e o token do Cloudflare Tunnel **não entram no backup** do
  Drive — garantir cópia no gerenciador de senhas.
- Scripts obsoletos no OPS: `host-restart.sh`, `host-reboot.sh`, `host-status.sh`,
  `update_hermes-agente-src.sh` (modelo container) e `bootstrap.sh` (ainda docker) —
  aguardando remoção/reescrita.
