# Bootstrap VM Nativa (sem Docker) — 07/08/2026

## Contexto
Migração completa de Docker Compose (2 containers) para **VM nativa** (`hermes-01`, Ubuntu 24.04). O antigo `bootstrap.sh` tinha referências a Docker + Tailscale — reescrito para o modelo atual.

## Novo bootstrap.sh (`hermes_mpt_ops/scripts/bootstrap.sh`)

**8 fases:**
1. **Clonar repos** — `hermes_mpt_ops`, `hermes_mpt_kb` (usa `GITHUB_TOKEN` se houver)
2. **Credenciais Git** — helper em `/home/hermes/.git-credentials` + `GITHUB_TOKEN.txt` (fora do hermes-data, portável)
3. **Restaurar `~/.hermes` + host-secrets** — do backup Drive (opcional `--restore-backup`)
   - host-secrets: `webui.env` (senha), `himalaya/`, `git-credentials`, `GITHUB_TOKEN.txt`
4. **Criar/atualizar `~/hermes-webui/.env`** — `HERMES_WEBUI_PASSWORD`, `AGENT_DIR`, `PYTHON`
5. **`uv sync`** — agente, WebUI, OPS
6. **systemd --user services** — `hermes-gateway` + `hermes-webui` (com `loginctl enable-linger`)
7. **Cloudflare Tunnel** — verifica `cloudflared` + token em `/etc/cloudflared/token` (NÃO migra no backup)
8. **Backup inicial** — `hermes-backup.py` → Drive

**Flags:**
```bash
--restore-backup /caminho/backup.tar.gz   # restaura identidade
--skip-services                           # pula systemd
--skip-cloudflare                         # pula cloudflared
```

## WebUI systemd --user service (criado 07/08/2026, corrigido 10/08/2026)

`/home/hermes/.config/systemd/user/hermes-webui.service`:
- `Type=simple`, `ExecStart` roda `bootstrap.py --foreground` (não `ctl.sh start` que daemoniza)
- `After=network-online.target hermes-gateway.service`
- `Restart=on-failure`, `RestartSec=5`
- **Hardening compatível com user service** (sem CAP_DROP):
  ```ini
  NoNewPrivileges=true
  PrivateTmp=true
  ProtectSystem=strict
  ProtectHome=read-only
  ReadWritePaths=%h/.hermes %h/hermes-webui
  RestrictRealtime=true
  RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
  ```
  > Opções que exigem `CAP_DROP` (`ProtectKernelTunables`, `ProtectKernelModules`, `ProtectControlGroups`, `RestrictNamespaces`, `LockPersonality`, `MemoryDenyWriteExecute`) **comentadas** — falham com `Failed to drop capabilities: Operation not permitted` (status 218).
- `Linger=yes` (sobe no boot sem login)
- Senha carrega do `~/hermes-webui/.env` (`HERMES_WEBUI_PASSWORD`)

**ExecStart correto (foreground):**
```ini
ExecStart=%h/.hermes/hermes-agent/venv/bin/python %h/hermes-webui/bootstrap.py \
  --no-browser --foreground --host 127.0.0.1 8787
```
> `ctl.sh start` daemoniza (`nohup ... &`) → systemd `Type=simple` acha que terminou e roda `ExecStop`. `--foreground` mantém o processo vivo.

**Comandos:**
```bash
systemctl --user daemon-reload
systemctl --user enable --now hermes-webui
systemctl --user status hermes-webui
journalctl --user -u hermes-webui -f
```

**Uma vez só sudo:**
```bash
sudo loginctl enable-linger hermes   # user services no boot
```

## Cloudscraper Bypass WAF MPT (cross-ref: `analise-pgea/references/cloudscraper-waf-mpt.md`)

O WAF do `mpt.mp.br` bloqueia **Chromium headless** (local E cloud/Browser Use) por **detecção de automação/JS** — não por IP. O **`cloudscraper` (Python) PASSA** (fingerprint TLS próprio).

**Script versionado:** `hermes_mpt_ops/scripts/baixar_boletil.py`
- POST multipart com campo-gatilho `j_idt183` + ViewState pós-consulta
- CLI: `ano mês [--baixar N|todos] [--dir]`

**Indexador PRT14:** `hermes_mpt_ops/scripts/indexar_boletins_prt14.py`
- Varre MDs extraídos (`audit_boletil.py` → headers `## TIPO Nº X`)
- Isola sub-bloco `PRT-14ª REGIÃO` dentro da seção `PROCURADORIAS REGIONAIS`
- 2 níveis: nível 2 = ato DA PRT14 (assinado); nível 1 = menciona 14ª/RO/AC
- SQLite com tabela `atos` (boletim, data, tipo, numero, ementa, relevância)

## Bug fix `audit_boletil.py` (07/08/2026)
- NameError `suspeitas` na linha 370 (variável só existia dentro de `auditar_extracao`)
- Fix: capturar retorno de `auditar_extracao` e extrair número de suspeitas do texto
- `n_susp` inicializado antes dos branches para evitar unbound