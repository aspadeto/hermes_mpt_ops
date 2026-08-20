---
name: browser-infrastructure
description: "Deploy/diagnose local/cloud browser on CDP/TLS/WAF fails."
version: 1.0.0
author: HAL 9000
platforms: [linux]
metadata:
  hermes:
    tags: [browser, cdp, chromium, browserless, waf, tls, docker, docker-compose]
    category: hermes-ops
---

# Browser Infrastructure for Hermes

Como configurar, gerenciar e diagnosticar serviços de browser para o Hermes
Agente — tanto cloud (Browser Use / Browserbase) quanto local
(browserless/chromium em Docker).

## Quando Ativar

- Browser Use cloud está fora (502 Bad Gateway no CDP) e precisa de fallback local
- Um site bloqueia requisições HTTP (curl/Python requests) — só browser negocia TLS
- Um site tem WAF que detecta headless Chromium e bloqueia (ex: MPT, Attack ID 20000051)
- Precisar configurar browserless/chromium no docker-compose do host
- Diagnosticar por que `browser_navigate` está falhando

## Arquitetura

```
┌─ Hermes Agent ─────────────────┐
│  browser_tool.py                │
│  ├── cloud_provider (Browser Use│
│  │   └── api.browser-use.com)   │
│  ├── browser.cdp_url (local)    │  ← config.yaml
│  │   └── browserless/chromium   │
│  │       (Docker: hermes-browser)
│  └── agent-browser CLI          │
└─────────────────────────────────┘
```

O Hermes tem **3 modos de browser**:

| Modo | Config | Quando usar |
|------|--------|-------------|
| **Cloud Browser Use** | `cloud_provider: browser-use` | Sites com WAF + proxy residencial necessário |
| **CDP local** | `cdp_url: ws://host:port/` | Sites sem WAF, ou Chromium local próprio |
| **agent-browser local** | `cloud_provider: ""` (sem cdp_url) | Chromium embutido no $HOME |

## Nous Tool Gateway (rota cloud sem chave direta — validado 07/08/2026)

Com assinatura Nous paga, o browser cloud pode usar o **Tool Gateway** (Browser
Use gerenciado pela Nous) **sem** chave direta do Browser Use. Config:

```yaml
browser:
  cloud_provider: browser-use
  use_gateway: true
```

- `use_gateway: true` roteia pela Nous mesmo sem `BROWSER_USE_API_KEY` no `.env`
  (chaves diretas coexistem; o gateway tem precedência).
- Estado por tool: `~/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main portal info`
  → mostra "Web tools via Nous Portal", "Browser automation Local browser | via Nous".
- **`hermes config set browser.cloud_provider "browser-use"` avisa "not a
  recognized config key" — IGNORAR o aviso**: é o schema de validação do CLI,
  mas o `browser_tool.py` lê o YAML cru via `read_raw_config()` e a chave
  funciona (validado: sessão real `https://*.cdp.browser-use.com` criada e
  fechada com `create_session(task_id=...)` + `close_session(session_id)`).
- **Local e cloud COEXISTEM**: `browser.auto_local_for_private_urls: True`
  (default) → URLs LAN/localhost usam o Chromium local; URLs públicas vão ao
  cloud. Não é ou-um-ou-outro.

## Provisionamento de Browser Local

### Opção 1: browserless/chromium em Docker (recomendado)

```yaml
# Adicionar ao docker-compose.yml
services:
  browser:
    image: ghcr.io/browserless/chromium:latest
    container_name: hermes-browser
    restart: unless-stopped
    shm_size: 2gb
    environment:
      - CONCURRENT=10
      - TIMEOUT=300000        # 5 min (ms)
      - HEALTH=true
      - MAX_QUEUE_LENGTH=20
      - USER_AGENT=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36
        (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36
    networks:
      - hermes-net
```

```bash
# Configurar Hermes para usar
hermes config set browser.cloud_provider ""
hermes config set browser.cdp_url "ws://browser:3000/"
```

Verificar se o CDP está respondendo:
```bash
curl -s http://browser:3000/json/version | grep -o '"Browser":"[^"]*"'
# → "Browser":"Chrome/151.0.7922.34"
```

### Opção 2: agent-browser nativo (simples, sem Docker)

```bash
# Instala Chromium dentro do $HOME do Hermes
agent-browser install --with-deps

# Config para modo local (sem CDP externo)
hermes config set browser.cloud_provider ""
```

### Opção 3: Obscura (Rust headless browser, ~70MB binary)

Projeto novo (v0.2.0, ago/2026): https://github.com/h4ckf0r0day/obscura

```bash
# Docker (persistente, sobrevive a reboot com --restart unless-stopped)
docker run -d --name obscura --restart unless-stopped -p 127.0.0.1:9222:9222 h4ckf0r0day/obscura

# Plugin Hermes: hermes plugins enable browser-obscura (já bundled)
# Config:
browser:
  cloud_provider: "obscura"
# Env para modo remoto (conecta no server existente, não spawna):
OBSCURA_CDP_URL=http://127.0.0.1:9222
```

**Vantagens testadas (ago/2026):**
- Passa no WAF do MPT (onde Chromium headless e Browser Use cloud falhavam)
- Binário único Rust (~70MB, ~30MB RAM), sem Chrome/Node
- CDP nativo — `Target.createTarget` + sessão funciona; target default (`page-1` em `about:blank`) tem bug `Page.navigate: No page for session` no v0.2.0
- Modo remoto (Docker) + plugin Hermes: navegação OK, cliques/console via CDP têm bugs conhecidos no v0.2.0

**Caveats:**
- Projeto muito novo (4 meses, 818 commits) — bugs de interação CDP no modo remoto
- Para automação completa (cliques, selects PrimeFaces), `fetch --eval` do CLI local funciona melhor que CDP remoto
- Roadmap: "Drop-in CDP para Puppeteer/Playwright" em progresso

## TLS Problemático (MPT e similares)

O servidor do MPT (`mpt.mp.br`) rejeita conexões TLS de HTTP clients não-browser
(curl, Python requests, wget). O erro é `SSL: UNEXPECTED_EOF_WHILE_READING`
durante o handshake — o servidor fecha a conexão após o Client Hello.

**Diagnóstico:**
```bash
curl -v https://mpt.mp.br/ 2>&1 | grep "SSL\|error\|alert"
# → TLSv1.3 (OUT), TLS alert, decode error (562)
# → SSL routines::unexpected eof while reading
```

**Solução:** Chromium tem stack TLS próprio que negocia onde OpenSSL do sistema
falha. Usar `browser_navigate` + `browser_console` (fetch) ou browserless/chromium
em Docker.

## WAF que Bloqueia Headless Chromium

Alguns sites (ex: MPT via Cloudflare) usam WAF que detecta navegadores headless:

| Indicador | Como o WAF detecta |
|-----------|-------------------|
| `navigator.webdriver = true` | Flag de headless Chrome |
| `HeadlessChrome` no User-Agent | Presente mesmo com `USER_AGENT` sobrescrito |
| Fingerprint | WebGL, fontes ausentes, plugins |

Sites que bloqueiam headless Chromium retornam "Sua requisição foi bloqueada"
com Attack ID 20000051 (Cloudflare).

### Soluções para WAF

| Abordagem | Funciona? | Custo |
|-----------|-----------|-------|
| **Browser Use cloud** (proxies residenciais + stealth) | ✅ | Incluso subscrição Nous |
| **browserless/chromium local** puro | ❌ WAF detecta | Zero |
| **browserless + puppeteer-extra-stealth** (Docker customizado) | ⚠️ Parcial | Zero + manutenção |
| **VPN residencial + browserless** | ✅ | Custo do proxy |

**Browser Use cloud** é a única solução testada que passa no WAF do MPT.

## Infraestrutura Docker via SSH do Container

Quando o Hermes roda em container e precisa modificar o docker-compose no host:

```bash
# Acessar host
ssh -F ~/.ssh/config -i ~/.ssh/hermes_host_key host

# Localizar compose
find ~ -name "docker-compose*" -not -path "*node_modules*" 2>/dev/null

# Backup antes
cp compose.yml compose.yml.bak.$(date +%Y%m%d_%H%M%S)

# Adicionar serviço via Python (evita problemas de quoting com heredoc)
python3 << 'PYEOF'
import re
COMPOSE = "/caminho/docker-compose.yml"
with open(COMPOSE) as f:
    content = f.read()
# ... modificar ...
with open(COMPOSE, "w") as f:
    f.write(content)
PYEOF

# Reaplicar
docker compose up -d browser    # serviço específico
docker compose up -d            # tudo

# Verificar
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## Scripts Relacionados

- `audit_boletim.py` — auditoria de extração de Boletins de Serviço MPT
  (usa pymupdf, detecta 25+ tipos de ato, 3 camadas de validação)
  (em `hermes_mpt_ops/scripts/` — fonte da verdade; ver skill `boletim-servico-mpt`)

## Referências

- `references/browserless-mpt-setup.md`
- `references/cloudscraper-waf-mpt.md` — cloudscraper bypass do WAF MPT (fluxo multipart + ViewState + gatilho j_idt183)
- `references/obscura-docker-setup.md` — Obscura Docker persistente (survive reboot, CDP bug v0.2.0)

> ⚠️ **Docker removido (07/08/2026):** o ambiente migrou para **VM nativa**
> (`hermes-01`, sem Docker/Tailscale). As seções acima sobre
> browserless/chromium em docker-compose e SSH container→host são
> **históricas** — os scripts `host-{status,restart,reboot}.sh` e
> `update_hermes-agente-src.sh` foram **removidos** do OPS (pendência #12).
> No modelo VM: browser local = agent-browser + Chromium do $HOME
> (auto `--no-sandbox`), cloud = Nous Tool Gateway (ver seção acima).

## Pitfalls

- **`browser.cdp_url` obsoleto (pós-migração) QUEBRA o browser silenciosamente**
  — Se o `config.yaml` mantém `cdp_url` apontando para um container/serviço que
  foi removido (ex: `ws://browser:3000/` do Docker browserless, após migrar para
  VM sem Docker), o Hermes **pula o launcher local** e tenta conectar no endpoint
  morto → `browser_navigate` falha sem mensagem clara. Diagnóstico:
  ```python
  from tools.browser_tool import _get_cdp_override_raw, _get_cdp_override
  _get_cdp_override_raw()   # valor configurado (sem I/O)
  _get_cdp_override()       # resolve o endpoint (faz HTTP /json/version)
  ```
  Correção: `hermes config set browser.cdp_url ""` → volta ao **modo local**
  (agent-browser + Chromium do $HOME). O config é lido em runtime — **não precisa
  reiniciar o gateway**.
- **Chromium em VM Ubuntu 23.10+ falha com "No usable sandbox"** — o Hermes
  **auto-injeta** `AGENT_BROWSER_ARGS="--no-sandbox,--disable-dev-shm-usage"`
  quando detecta root, Docker, ou `/proc/sys/kernel/apparmor_restrict_unprivileged_userns=1`
  (função `_needs_chromium_sandbox_bypass()`). Testar via CLI manual exige passar
  a flag explicitamente (`agent-browser open URL --args "--no-sandbox"`), mas o
  tool do Hermes já injeta sozinho — não configurar manualmente.
- **browserless/chromium retorna `ws://0.0.0.0:3000/` no `/json/version`**
  — NÃO usar este valor literal. Configurar `cdp_url` como `ws://browser:3000/`
  (o nome do serviço Docker, não `0.0.0.0`).
- **`browser.cloud_provider: browser-use` + `cdp_url` configurados simultaneamente**
  — O cloud_provider tem prioridade sobre cdp_url. Para usar CDP local, ZERAR
  cloud_provider: `hermes config set browser.cloud_provider ""`.
- **`use_gateway: true` conflita com CDP local** — remover esta chave do config
  quando migrar para local.
- **ssh host falha com quoting complexo** — scripts multi-linha via SSH exigem
  Python heredoc ou scp de arquivo temporário. Heredoc simples com `'PYEOF'`
  (aspas simples) evita expansão local de variáveis.
- **`pip install requests` pode ser necessário** no container WebUI — o módulo
  não vem pré-instalado.