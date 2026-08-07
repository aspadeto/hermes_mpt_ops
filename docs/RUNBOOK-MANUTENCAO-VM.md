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
| **WebUI** (porta 8787) | daemon `~/hermes-webui/server.py` via `ctl.sh` | `~/hermes-webui/ctl.sh ...` |
| **Túnel Cloudflare** | system service `cloudflared.service` (root) | `sudo systemctl ...` |
| **Cron do Hermes** | scheduler dentro do gateway | `hermes cron list` |

**Fatos da migração (07/08/2026):**
- Unit do gateway: `~/.config/systemd/user/hermes-gateway.service` (enabled).
  ExecStart: `~/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run`.
- O processo da WebUI roda no cgroup do user service (`app.slice/hermes-gateway.service`),
  com pid/log em `~/.hermes/webui.pid` e `~/.hermes/webui.log`.
- `/opt/data/hermes-data` é diretório real da VM (não bind mount).

---

## 2. Comandos de rotina

```bash
# Gateway — status, logs, restart
systemctl --user status hermes-gateway.service
journalctl --user -u hermes-gateway --no-pager -n 100        # logs
systemctl --user restart hermes-gateway.service              # reiniciar gateway

# WebUI — status, logs, restart
~/hermes-webui/ctl.sh status
~/hermes-webui/ctl.sh logs --lines 100
~/hermes-webui/ctl.sh restart

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
| 20241 | API interna do gateway | só 127.0.0.1 |

## 4. Backup

- Diário 03:00 UTC → Google Drive (pasta `HermesBackup`), via `hermes-backup.py`.
- Exclui repos git (KB/OPS) e `.google-venv`.
- Testar manualmente: `hermes_mpt_ops/scripts/hermes-backup.py` (rodar e conferir upload).

## 5. Pendências conhecidas (pós-migração)

- `browser.cdp_url: ws://browser:3000/` no `config.yaml` — container browserless
  removido; ferramentas de browser precisam de reconfiguração (ex: apontar para
  browser local via CDP ou serviço externo).
- `~/hermes-webui/.env` e o token do Cloudflare Tunnel **não entram no backup** do
  Drive — garantir cópia no gerenciador de senhas.
- Scripts obsoletos no OPS: `host-restart.sh`, `host-reboot.sh`, `host-status.sh`,
  `update_hermes-agente-src.sh` (modelo container) e `bootstrap.sh` (ainda docker) —
  aguardando remoção/reescrita.
