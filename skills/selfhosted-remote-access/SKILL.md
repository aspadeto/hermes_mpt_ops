---
name: selfhosted-remote-access
description: "Expor serviço self-hosted quando VPN é bloqueada."
version: 1.0.0
author: HAL 9000
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [cloudflare, tunnel, access, ngrok, ddns, cgnat, webui, vpn-blocked]
    category: hermes-ops
---

# Acesso Remoto a Serviços Self-Hosted (quando VPN é bloqueada)

Como expor um serviço local (ex: WebUI do Hermes na porta 8787) para acesso
**externo** quando o caminho óbvio (Tailscale/VPN) está bloqueado na rede de
origem — tipicamente rede corporativa com firewall.

## ⚠️ ESTADO ATUAL (ago/2026): Cloudflare Tunnel implementado e ATIVO

- Rota ativa: `https://webui-01.asideia.net` (túnel `webui-tunnel`, domínio `asideia.net`)
  - ⚠️ **hostname é `webui-01`** (não `webui`) — o usuário renomeou em 04/08/2026
- **Dashboard (desde 15/08/2026):** segundo hostname `dashboard-01.asideia.net → localhost:9119`,
  serviço systemd --user `hermes-dashboard` (porta 9119). Auth: ver `references/hermes-dashboard-serving.md`.
- **Tailscale foi DESINSTALADO do host** (serve reset → systemctl stop/disable → apt remove).
  Não tentar `tailscale up`/reinstalar — a rota atual é o Cloudflare Tunnel.
- Detalhes da implementação: skill `tailscale-remote-access` → `references/cloudflare-tunnel-setup.md`

## Quando Usar

- Usuário quer acessar o WebUI/serviço de uma rede que **bloqueia VPN** (ex: rede MPT)
- `tailscale netcheck` falha com timeout ao buscar DERP map
- Telegram/sites HTTPS funcionam, mas Tailscale não → bloqueio seletivo
- Precisa de URL fixa, HTTPS e autenticação extra para expor um serviço interno

## Diagnóstico (fazer ANTES de escolher a solução)

### Padrão típico de bloqueio corporativo

| Sintoma | Diagnóstico | Conclusão |
|---------|-------------|-----------|
| `tailscale netcheck` → `Failed to fetch DERP map` / timeout em `controlplane.tailscale.com` | Servidor de CONTROLE do TS bloqueado (não é UDP) | Tailscale inviável na rede de origem |
| Telegram + sites HTTPS funcionam | HTTPS:443 liberado | Túnel HTTPS (Cloudflare/ngrok) passa |
| `curl https://controlplane.tailscale.com` → timeout; `curl google.com` → OK | Blocklist seletiva por domínio de VPN | Usar domínio PRÓPRIO (não está na blocklist) |

### Comandos de diagnóstico (rodar na rede de origem)

```bash
# 1. O erro clássico — control plane bloqueado:
tailscale netcheck
# → "Failed to fetch a DERP map ... controlplane.tailscale.com ... timeout"

# 2. Confirmar bloqueio seletivo (comparar):
curl -v --max-time 8 https://controlplane.tailscale.com/derpmap/default   # timeout = bloqueado
curl -v --max-time 8 https://www.google.com                                 # OK = HTTPS liberado
```

**Regra de ouro:** se HTTPS funciona (Telegram/sites passam) e só o domínio da
VPN é bloqueado → **túnel HTTPS com domínio próprio resolve**. O bloqueio é
por domínio, não por porta.

## Framework de Decisão

| Opção | Custo | Exige domínio? | Segurança | Quando escolher |
|-------|-------|----------------|-----------|-----------------|
| **Cloudflare Tunnel** ⭐ | Grátis + domínio (~R$40-65/ano) | ✅ Sim | 🟢 Alta (Access + origin oculto) | Solução definitiva; recomendado |
| **ngrok Free** | $0 | ❌ Não | 🟡 Média (URL pública, 1GB/mês, banner "free") | POC rápida / validação |
| **IP público + DDNS** | $0 (se ISP liberar CGNAT) | DDNS | 🔴 Alta exposição (abre porta, scanner/bots) | Só se precisar expor além de túnel |
| Tailscale | $0 | ❌ Não | 🟢 Alta | ❌ **Bloqueado** em rede corporativa (control plane) |

### Por que NÃO IP público + porta (mesmo com DDNS)
- Depende do ISP liberar CGNAT (briga com atendimento, pode reverter/cobrar)
- Expõe o serviço na internet ABERTA → brute-force, scanners
- DDNS tem latência de atualização; porta aberta = superfície de ataque
- **O túnel HTTPS funciona MESMO atrás de CGNAT** (conexão de saída) — independe do ISP

### Cloudflare Tunnel vs ngrok
- **Cloudflare Tunnel**: domínio próprio, banda ilimitada (grátis), Access (e-mail/OTP) grátis, sem banner — **definitivo**
- **ngrok Free**: 1 domínio automático `xxx.ngrok-free.app` (feio), **1 GB/mês**, 20k req/mês, banner "free" para visitantes — **POC apenas**

## Setup Cloudflare Tunnel (passo a passo real)

### 1. Registrar o domínio (no próprio Cloudflare — preço de custo, sem markup)
- Registrar direto no Cloudflare elimina etapa de nameservers
- TLD: `.dev`/`.app` forçam HTTPS; `.net`/`.com` mais "institucional" p/ apresentar a chefes
- Verificar disponibilidade via RDAP (whois pode não existir no container):
  ```bash
  curl -s https://rdap.org/domain/<nome> → 404 = DISPONÍVEL; 200 = registrado
  ```

### 2. Criar o túnel (dashboard, usuário)
1. https://dash.cloudflare.com → **Networking → Tunnels → Create a tunnel**
2. Nome (ex: `webui-tunnel`) → **Create tunnel**
3. Copiar o **token** (`cloudflared service install eyJ...` — a parte `eyJ...`)

### 3. Instalar cloudflared no host (usuário ou agente)
```bash
# Binário oficial (Linux amd64):
curl -fsSL -o cloudflared "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/cloudflared
sudo cloudflared service install <TOKEN>   # cria systemd, active + enabled
# Verificar: systemctl status cloudflared → "Registered tunnel connection ... protocol=quic"
```
> Se o agente não tem sudo para `/usr/local/bin`: instalar em `~/.local/bin/`
> e o usuário roda `sudo cloudflared service install <TOKEN>` no host.

### 4. Rota (Public Hostname) — dashboard, usuário
1. Túnel → **Public Hostname** (ou Routes) → **Add a public hostname**
2. Subdomain: `webui` | Domain: `asideia.net` | Service: `HTTP` → `localhost:8787`
3. Testar: `https://webui.asideia.net` deve abrir o serviço

### 5. Proteção com Cloudflare Access (obrigatório para serviço sensível)
1. **Zero Trust → Access → Applications → Create → Self-hosted**
2. Domain `asideia.net` + subdomain `webui` → Save
3. **Policy:** Action `Allow` | Include → **Emails** → e-mail do usuário (NUNCA "Everyone")
4. Session duration: 24h
5. Testar em janela anônima → deve pedir login por e-mail + código

**Camadas de proteção resultantes:**
```
https://webui.asideia.net
  ├─ 1º Cloudflare Access (e-mail + código OTP)   ← camada nova
  └─ 2º Senha do próprio serviço (ex: WebUI)      ← camada existente
```

## ⚠️ Pitfall CRÍTICO: variável do `.env` NÃO é injetada no container

**Sintoma:** o serviço (ex: WebUI) sobe **sem pedir senha** mesmo com
`HERMES_WEBUI_PASSWORD` definida no `.env` do compose.

**Causa:** variáveis do `.env` do Docker Compose são usadas para
**interpolação** (`${VAR}` no YAML) — mas **NÃO** viram env var do container
automaticamente. Precisa linha explícita no `environment:` do serviço:

```yaml
# docker-compose.yml — serviço hermes-webui
environment:
  - HERMES_WEBUI_PASSWORD=${HERMES_WEBUI_PASSWORD:-}   # ← linha que faltava
```

**Verificação (diagnóstico):**
```bash
ssh host 'docker inspect hermes-webui --format "{{range .Config.Env}}{{println .}}{{end}}" | grep -i password'
# vazio = variável NÃO chegou ao container → adicionar no compose + docker compose up -d
```

**Correção:** adicionar a linha no `environment:` → `docker compose up -d`
(recria o container) → testar. **Sempre conferir se a env chegou ao container**
após mudanças de compose — "está no .env" ≠ "está no container".

## ⚠️ Pitfall: domínio NOVO é bloqueado por firewall corporativo (~30 dias)

**Sintoma:** o túnel funciona (testado de casa/celular), mas na rede corporativa
o acesso é bloqueado com erro de categoria **"Newly Observed Domain"**.

**Causa:** firewalls corporativos (Fortinet/Palo Alto/etc.) classificam domínios
**recém-registrados** como suspeitos (anti-phishing) e bloqueiam por ~30 dias.
Não é problema de configuração — é a idade do domínio.

**O que fazer:**
- Confirmar que o acesso funciona de OUTRAS redes (4G, casa) → isola o problema no firewall
- **Opções:** (a) aguardar ~30 dias (o domínio sai da categoria automaticamente);
  (b) solicitar whitelist/reclassificação ao TI (categoria correta: "Business/Technology");
  (c) ponte temporária com ngrok (domínio `ngrok-free.app` é antigo/conhecido → passa)
- Não é um bug do Cloudflare Tunnel — o túnel está correto

**Detalhe:** se o usuário **renomear o hostname** (ex: `webui` → `webui-01`),
o hostname antigo para de resolver (HTTP 000). Verificar o hostname atual no
painel antes de citar a URL.

## Operações pós-setup

- Túnel: `systemctl status cloudflared` (host) — restart: `sudo systemctl restart cloudflared`
- Alterar rota/Access: dashboard Cloudflare (não precisa tocar no host)
- Remover: `sudo cloudflared service uninstall` + remover túnel no dashboard

## ⚠️ Migração de host: o túnel NÃO migra com backup (validado 07/08/2026)

Ao mover o serviço para outra máquina (ex: container Docker → VM nativa), o
túnel morre **silenciosamente**: o DNS continua apontando para o proxy
Cloudflare (104.21.x.x/172.67.x.x), mas o `cloudflared` local não existe na
máquina nova → `curl https://webui-01.asideia.net` → HTTP 000/502.

Fatos verificados na migração:

- **O token do túnel NÃO está em nenhum backup** (nem tgz, nem `.env`, nem
  compose) — é recuperável **somente no dashboard** (Zero Trust → Networks →
  Tunnels → `<túnel>` → Configure → aba "Install and run" → comando
  `cloudflared service install <TOKEN>`). Pedir ao usuário para copiar.
- **cloudflared não vem no backup** — reinstalar do GitHub
  (`cloudflared-linux-amd64` → `~/.local/bin/`, sem sudo) e o usuário roda
  `sudo ~/.local/bin/cloudflared service install <TOKEN>` (sem sudo o agente
  instala o binário, mas o service systemd exige root).
- **WebUI nativo sem senha é comum pós-migração** (bootstrap log: "No password
  set. Any process on this machine can read sessions and memory via the local
  API") — definir `HERMES_WEBUI_PASSWORD` ANTES de religar o túnel (1ª camada
  Access + 2ª senha do serviço). No WebUI nativo a senha vai em
  `~/hermes-webui/.env` (carregada no start do `server.py` — editar exige
  restart do serviço).
- **WebUI nativo (sem docker) precisa de unit systemd --user para sobreviver a
  reboot** (decisão final 07/08/2026 — Opção A): unit em
  `~/.config/systemd/user/hermes-webui.service`, mesmo padrão do
  `hermes-gateway.service` (Type=simple + ExecStart=`~/hermes-webui/start.sh`
  em foreground; fixar `HERMES_WEBUI_PYTHON` porque o PATH do systemd não
  inclui o venv; parar o daemon ctl.sh antes do primeiro start). **sem sudo**:
  `systemctl --user enable --now hermes-webui` + `Linger=yes` (já ativo no
  usuário hermes) → sobrevive a logout/reboot. NÃO usar unit system (systemd
  system exigiria sudo; a opção --user é consistente com o gateway).
- A **rota** (Public Hostname → localhost:8787) e o **Access** sobrevivem no
  dashboard — não precisam ser recriados, só o `cloudflared` local.

## Referências

- Skill relacionada: `container-host-ssh` (SSH container→host — base para operar o host)
- Skill relacionada: `tailscale-remote-access` (por que TS falha em rede corporativa)
- Runbook de recuperação: `hermes_mpt_ops/docs/RUNBOOK-RECUPERACAO.md`
- Caso real documentado (erro exato + decisão): `references/tailscale-blocked-corporate-case.md`
- **Dashboard Hermes — serving, auth e session token:** `references/hermes-dashboard-serving.md`
  (dual auth model: loopback `HERMES_DASHBOARD_SESSION_TOKEN` vs não-loopback `dashboard.basic_auth`;
  systemd user service porta 9119; `--insecure` é no-op desde jun/2026)
