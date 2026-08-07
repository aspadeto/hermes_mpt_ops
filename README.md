# DR MPT — Repositório de Operações (hermes_mpt_ops)

Repositório de **engenharia e operações** da Diretoria Regional do MPT.
Complementar ao [hermes_mpt_kb](https://github.com/aspadeto/hermes_mpt_kb) (conhecimento).

> 🤖 **Agentes (Hermes, Claude Code, Copilot):** leia o
> **[AGENTS.md](AGENTS.md)** — diretrizes comportamentais adaptadas do
> [CLAUDE.md de Andrej Karpathy](https://github.com/multica-ai/andrej-karpathy-skills)
> (simplicidade, mudanças cirúrgicas, pensar antes de agir).

**Divisão de trabalho:**
- `hermes_mpt_kb` = **conhecimento** — PGEAs, artigos, referências, processos (documentos)
- `hermes_mpt_ops` = **engenharia** — scripts, bancos de dados, configurações versionáveis

> 📥 **Ingestão de documentos:** veja [docs/FLUXO-INGESTAO.md](docs/FLUXO-INGESTAO.md) —
> caminho padrão do PDF → auditoria → KB/OPS (sem duplicação).

---

## 1. Visão Geral da Infraestrutura

> **⚠️ MUDANÇA ESTRUTURAL (07/08/2026):** o ambiente saiu de **Docker Compose
> (2 containers) para VM nativa** (`hermes-01`, Ubuntu 24.04). Não há mais
> containers, `docker-compose`, rede docker nem Tailscale. Docker e Tailscale
> foram **removidos**; a pasta `docker/` deste repo é só **histórico sanitizado**.

O **Hermes Agent** roda como **user service do systemd** (`hermes-gateway.service`),
e a **Hermes WebUI** roda como processo daemon da própria WebUI (`ctl.sh start`),
exposta via **Cloudflare Tunnel**.

| Componente | Como roda | Endereço |
|-----------|-----------|----------|
| Hermes Agent (gateway: Telegram + API) | `systemctl --user` → `hermes-gateway.service` (venv `~/.hermes/hermes-agent`) | API local `127.0.0.1:20241` |
| Hermes WebUI | daemon `~/hermes-webui/ctl.sh start` → `server.py` | `127.0.0.1:8787` (login) |
| Acesso remoto (WebUI) | Cloudflare Tunnel (serviço `cloudflared.service`, token no dashboard) | `https://webui-01.asideia.net` |
| SSH | `sshd` padrão | porta 22 |

**Fatos verificados (07/08/2026, pós-migração):**
- O gateway e a WebUI rodam como **processos nativos** do usuário `hermes` (sem container).
  O processo da WebUI ficou no cgroup do user service (`/proc/<pid>/cgroup` →
  `app.slice/hermes-gateway.service`) — a gestão do serviço é via `systemctl --user`.
- `/opt/data/hermes-data` é **diretório real** na VM (não é bind mount de container).
- Segredos migraram para **fora** do `hermes-data`: `/home/hermes/GITHUB_TOKEN.txt`,
  `/home/hermes/.git-credentials`, `~/.hermes/.env`, `~/hermes-webui/.env`.
- **Docker inacessível por design** — não há daemon nem socket no host.
- **Tailscale removido** (bloqueio de rede); acesso remoto via Cloudflare Tunnel.
- ⚠️ `browser.cdp_url: ws://browser:3000/` no `config.yaml` ainda aponta para o
  container `hermes-browser` (browserless) que **não existe mais** — ferramentas de
  browser precisam de reconfiguração (pendência aberta).

---

## 2. Estrutura do Repositório

```
hermes_mpt_ops/
├── scripts/     ← todos os scripts (dados + automação)
├── data/        ← bancos SQLite versionados (pendencias.db, regional-orcamento.db)
├── docker/      ← ⚠️ HISTÓRICO — compose sanitizado do modelo container (removido 07/08/2026). NÃO USAR
├── configs/     ← reservado p/ templates de config (.env.example, compose.example)
├── docs/        ← runbooks e notas de infra (recuperação, manutenção da VM)
└── bin/         ← (removido — scripts consolidados em scripts/)
```

> Scripts `host-restart.sh`, `host-reboot.sh`, `host-status.sh` (SSH container→host)
> e `update_hermes-agente-src.sh` (volume docker) estão **obsoletos** — aguardando
> remoção. `bootstrap.sh` ainda segue o fluxo docker (desatualizado).

---

## 3. Scripts

| Script | Função | Depende de |
|--------|--------|------------|
| `pdf2kb.py` | Converte PDF → Markdown + assets para o KB | pymupdf (venv) |
| `pendencia.py` | Sistema de pendências (TODO assíncrono) | sqlite3 (stdlib) |
| `consultar.py` | Consultas SQL no regional-orcamento.db | — |
| `importar-demandas.py` | Importa demandas do SGA para regional-orcamento.db | — |
| `importar-execucao.py` | Importa execução orçamentária | — |
| `hermes-backup.py` | Backup do Hermes para Google Drive | google-api (venv) |
| `kb-auto-commit.sh` | Auto-commit do KB + OPS (cron 10min) | git |

### Wrappers de cron

O cron do Hermes exige scripts reais em `~/.hermes/scripts/` (sem symlinks, sem
argumentos, sem caminho absoluto — decisão de segurança do scheduler). O padrão é:

```
hermes_mpt_ops/scripts/          ← CÓDIGO REAL (versionado)
~/.hermes/scripts/           ← WRAPPERS (atalhos p/ cron, não versionados)
```

> Detalhes completos: `wiki/referencias/cron-scripts-hermes.md`

---

## 4. Instalação (VM nativa)

```bash
# No host, clonar
git clone https://github.com/aspadeto/hermes_mpt_ops.git

# Venv para scripts com dependências (pdf2kb, backup)
uv venv .venv
uv pip install pymupdf

# Segredos e config (ver docs/RUNBOOK-RECUPERACAO.md):
#   /home/hermes/GITHUB_TOKEN.txt + /home/hermes/.git-credentials  (git)
#   ~/.hermes/.env          (Telegram, OpenRouter — lido pelo gateway)
#   ~/hermes-webui/.env     (HERMES_WEBUI_HOST/PORT/PASSWORD)
```

Subir o ambiente:

```bash
# Gateway (user service — sobe no login do usuário)
systemctl --user enable --now hermes-gateway.service

# WebUI (daemon próprio)
cd ~/hermes-webui && ./ctl.sh start

# Túnel Cloudflare (serviço de sistema; token SÓ no dashboard)
sudo systemctl enable --now cloudflared
```

---

## 5. Atualização da Infraestrutura

### Atualizar o agente (hermes-agent)

O código vive no venv `~/.hermes/hermes-agent` (instalado via `uv`/`pip`).
Atualizar e reiniciar o serviço:

```bash
systemctl --user restart hermes-gateway.service   # gateway (Telegram/API)
cd ~/hermes-webui && ./ctl.sh restart             # WebUI
```

### Ver status

```bash
systemctl --user status hermes-gateway.service
~/hermes-webui/ctl.sh status
systemctl status cloudflared
```

> Operações do dia a dia: [docs/RUNBOOK-MANUTENCAO-VM.md](docs/RUNBOOK-MANUTENCAO-VM.md)

---

## 6. Automações Ativas

| Automação | Frequência | Descrição |
|-----------|-----------|-----------|
| Auto-commit KB + OPS | a cada 10 min | Commita e faz push dos dois repositórios |
| Backup Google Drive | diário 03:00 UTC | tar.gz de `~/.hermes` + `hermes-data` (exclui repos git) |
| Lembrete de pendências | 3x/dia (9h, 14h, 18h UTC) | Avisa quando há pendências a resolver |

> Cron ativo no scheduler do Hermes (jobs `enabled: true` — conferir com
> `hermes cron list`). Lembretes via `pendencia-remind.py`.

---

## 7. Segredos

⚠️ **NUNCA** commitar tokens, credentials ou `.env`. O `.gitignore` bloqueia
`GITHUB_TOKEN.txt`, `.git-credentials`, `client_secret*.json`, `google_token.json`,
`.env` e `.env.*` (com exceção do template `docker/.env-default`, sanitizado).

Segredos vivem **fora** dos repositórios (raiz do hermes-data foi **esvaziada** de
segredos na migração):

| Segredo | Local |
|---------|-------|
| GitHub (token + credentials) | `/home/hermes/GITHUB_TOKEN.txt`, `/home/hermes/.git-credentials` |
| Telegram + OpenRouter | `~/.hermes/.env` |
| Senha do WebUI | `~/hermes-webui/.env` (⚠️ fora do backup do Drive — guardar no gerenciador) |
| Nous / providers | `~/.hermes/auth.json` |
| Google Workspace | `~/.hermes/google_client_secret.json`, `~/.hermes/google_token.json` |
| Email (Himalaya/Gmail) | `~/.config/himalaya/` |
| Cloudflare Tunnel | token no **dashboard** + `/etc/cloudflared/token` (⚠️ fora do backup) |

Para versionar configuração, usar **templates** (ex: `docker/.env-default`) sem valores.

---

## 8. Recuperação de Desastre

O ambiente é **replicável**: se o host falhar, o sistema pode ser reativado em uma
máquina nova com `git` + backup do Google Drive (não há mais dependência de Docker).

**Documentação completa:**
- 📋 **[docs/RUNBOOK-RECUPERACAO.md](docs/RUNBOOK-RECUPERACAO.md)** — passo a passo
  detalhado (7 fases) + **como criar/obter cada segredo**

**Cobertura da recuperação:**

| Camada | Fonte |
|--------|-------|
| Engenharia (scripts, bancos) | `hermes_mpt_ops` (git) |
| Conhecimento (wiki) | `hermes_mpt_kb` (git) |
| Identidade (config, memória, tokens) | **Backup Google Drive** (diário) |

> ⚠️ **Segredos fora de qualquer backup** (restaurar manualmente): `WEBUI_PASSWORD`
> (`~/hermes-webui/.env`) e o **token do Cloudflare Tunnel** (dashboard). Guardar em
> gerenciador de senhas.

---

## 9. Limitações Conhecidas

- Ferramentas de **browser** do Hermes: `cdp_url` aponta para o container
  `hermes-browser` (browserless) que não existe mais pós-migração — reconfigurar
  (pendência aberta).
- `~/hermes-webui/.env` (senha do WebUI) **não entra no backup** do Drive (fora de
  `~/.hermes` e `hermes-data`).
- Token do Cloudflare Tunnel vive só no dashboard + `/etc/cloudflared/token` — não
  migra em backup.
- Firewall da rede pode bloquear o domínio novo (`webui-01.asideia.net`) por ~30
  dias após criação.
