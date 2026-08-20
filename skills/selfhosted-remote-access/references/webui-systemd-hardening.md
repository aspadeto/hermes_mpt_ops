# WebUI systemd --user Service — Hardening Compatível

**Problema (ago/2026):** unit `hermes-webui.service` falhava com
`Failed to drop capabilities: Operation not permitted` (status 218/CAPABILITIES).

**Causa:** opções de hardening que exigem `CAP_DROP` **não funcionam em user
services** (systemd roda sem CAP_SYS_ADMIN no user slice).

## Opções INCOMPATÍVEIS (comentadas no unit atual)

```ini
# Estas requerem CAP_DROP → NÃO funcionam em user service
# ProtectKernelTunables=true
# ProtectKernelModules=true
# ProtectControlGroups=true
# RestrictNamespaces=true
# LockPersonality=true
# MemoryDenyWriteExecute=true
```

## Opções COMPATÍVEIS (mantidas)

```ini
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=%h/.hermes %h/hermes-webui
RestrictRealtime=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
```

## ExecStart — foreground obrigatório

`ctl.sh start` **daemoniza** (usa `nohup ... &`) → systemd `Type=simple` acha
que terminou e roda `ExecStop`. **Correção:** rodar `bootstrap.py --foreground`
direto:

```ini
ExecStart=%h/.hermes/hermes-agent/venv/bin/python %h/hermes-webui/bootstrap.py \
  --no-browser --foreground --host 127.0.0.1 8787
```

> ⚠️ **Argumento posicional `8787`** (não `--port 8787`) — `bootstrap.py` usa
> positional argument para porta.

## Unit corrigida (resumo)

```ini
[Unit]
Description=Hermes WebUI (Dashboard)
After=network-online.target hermes-gateway.service
Wants=network-online.target

[Service]
Type=simple
Environment=HERMES_HOME=%h/.hermes
EnvironmentFile=-%h/hermes-webui/.env
ExecStart=%h/.hermes/hermes-agent/venv/bin/python %h/hermes-webui/bootstrap.py \
  --no-browser --foreground --host 127.0.0.1 8787
Restart=on-failure
RestartSec=5
TimeoutStartSec=60
TimeoutStopSec=15

# Hardening compatível com user services
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ReadWritePaths=%h/.hermes %h/hermes-webui
RestrictRealtime=true
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX

[Install]
WantedBy=default.target
```

## Permissões sudo

**Apenas uma vez** (primeiro boot):
```bash
sudo loginctl enable-linger hermes   # user services no boot
```
Depois: tudo `systemctl --user` — **sem sudo**.