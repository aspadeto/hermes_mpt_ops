# DR MPT — Repositório de Operações (hermes_mpt_ops)

Repositório de **engenharia e operações** da Diretoria Regional do MPT (Rondônia/Acre).
Complementar ao [hermes_mpt_kb](https://github.com/aspadeto/hermes_mpt_kb) (conhecimento).

> 🤖 **Agentes (Hermes, Claude Code, Copilot):** leia o
> **[AGENTS.md](AGENTS.md)** — diretrizes comportamentais adaptadas do
> [CLAUDE.md de Andrej Karpathy](https://github.com/multica-ai/andrej-karpathy-skills)
> (simplicidade, mudanças cirúrgicas, pensar antes de agir).

**Divisão de trabalho:**
- `hermes_mpt_kb` = **conhecimento** — PGEAs, artigos, referências, processos (documentos)
- `hermes_mpt_ops` = **engenharia** — scripts, bancos de dados, configurações versionáveis

---

## 1. Visão Geral da Infraestrutura

O ambiente roda o **Hermes Agent** com a **Hermes WebUI** em dois containers conectados
(via Docker Compose), acessíveis remotamente via **Tailscale**.

| Componente | Endereço | Porta |
|-----------|----------|-------|
| Hermes Agent (gateway) | `localhost` (host) | 8642 |
| Hermes WebUI | `https://as7-hermes-docker.tail15f7e7.ts.net` | 8787 |
| Dashboard | `localhost` (host) | 9119 |

> Detalhes completos do Tailscale (grants, serve, SSH): `wiki/referencias/tailscale-acesso-remoto.md`

### Compose e Volumes

O compose vive em **`docker/`** e é parametrizado via `.env` (veja abaixo):

| Variável (`.env`) | Host (default) | Container | Conteúdo |
|-------------------|---------------|-----------|----------|
| `HOST_HERMES_HOME` | `${HOME}/.hermes` | `/home/hermes/.hermes` (agent) / `/home/hermeswebui/.hermes` (webui) | Config, sessões, skills, memória, cache |
| `HOST_HERMES_DATA` | `${HOME}/hermes-data` | `/opt/data/hermes-data` | **Este repositório** + wiki + tokens |
| `HOST_HERMES_WEBUI_WORKSPACE` | `${HOME}/hermes-data/hermes-webui/workspace` | `/workspace` | Área de trabalho (WebUI) |
| `hermes-agent-src` (volume Docker) | — | `/opt/hermes` | Código-fonte do Hermes Agent (volume nomeado) |

> 💡 Os valores usam `${HOME}` — o Compose expande com o home real do usuário do
> host, tornando o `.env` portátil entre máquinas. Só use caminho absoluto se o
> layout do host for atípico.

> **Nota:** O container usa UID/GID `1000` por padrão. Se seu usuário host tem UID
> diferente, ajuste no `.env`: `echo "UID=$(id -u)" >> .env` e `GID=$(id -g)`.

---

## 2. Estrutura do Repositório

```
hermes_mpt_ops/
├── scripts/     ← todos os scripts (dados + automação)
├── data/        ← bancos SQLite versionados (pendencias.db, regional-orcamento.db)
├── docker/      ← docker-compose.yml + .env-default (template SEM segredos)
├── configs/     ← reservado p/ templates de config (.env.example, compose.example)
├── docs/        ← runbooks e notas de infra (recuperação, SSH host)
└── bin/         ← (removido — scripts consolidados em scripts/)
```

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
| `bootstrap.sh` | Reativação do ambiente em host novo (recuperação) | docker, git |
| `update_hermes-agente-src.sh` | Recria o volume `hermes-agent-src` no Docker | docker |

### Wrappers de cron

O cron do Hermes exige scripts reais em `~/.hermes/scripts/` (sem symlinks, sem
argumentos, sem caminho absoluto — decisão de segurança do scheduler). O padrão é:

```
hermes_mpt_ops/scripts/          ← CÓDIGO REAL (versionado)
~/.hermes/scripts/           ← WRAPPERS (atalhos p/ cron, não versionados)
```

> Detalhes completos: `wiki/referencias/cron-scripts-hermes.md`

---

## 4. Instalação

```bash
# No host, clonar
git clone https://github.com/aspadeto/hermes_mpt_ops.git

# Venv para scripts com dependências (pdf2kb, backup)
uv venv .venv
uv pip install pymupdf

# Docker: configurar o .env a partir do template
cd docker
cp .env-default .env
# preencher: HERMES_WEBUI_PASSWORD e API_SERVER_KEY (ver runbook)
```

---

## 5. Atualização da Infraestrutura

### Atualizar a imagem do agente

```bash
docker compose pull
docker compose down
docker compose up -d
```

### Atualizar o código-fonte do agente (volume `hermes-agent-src`)

O volume nomeado `hermes-agent-src` NÃO é atualizado pelo `docker compose pull`.
Use o script dedicado:

```bash
scripts/update_hermes-agente-src.sh
# (faz: down → rm volume → pull → up)
```

---

## 6. Automações Ativas

| Automação | Frequência | Descrição |
|-----------|-----------|-----------|
| Auto-commit KB + OPS | a cada 10 min | Commita e faz push dos dois repositórios |
| Backup Google Drive | diário 03:00 UTC | tar.gz de `~/.hermes` + `hermes-data` (exclui repos git) |
| Lembrete de pendências | 3x/dia (9h, 14h, 18h UTC) | Avisa quando há pendências a resolver |

---

## 7. Segredos

⚠️ **NUNCA** commitar tokens, credentials ou `.env`. O `.gitignore` bloqueia
`GITHUB_TOKEN.txt`, `.git-credentials`, `client_secret*.json`, `google_token.json`,
`.env` e `.env.*` (com exceção do template `docker/.env-default`, sanitizado).

Segredos vivem **fora** dos repositórios:
- `hermes-data/GITHUB_TOKEN.txt` — token do GitHub (clones/push)
- `hermes-data/.git-credentials` — credenciais git (store)
- `docker/.env` — segredos do Docker (senha WebUI, API key, caminhos)
- `~/.hermes/.env` — segredos do Hermes (Telegram, OpenRouter)

Para versionar configuração, usar **templates** (ex: `docker/.env-default`) sem valores.

---

## 8. Recuperação de Desastre

O ambiente é **replicável**: se o host falhar, o sistema pode ser reativado
em uma máquina nova com:

```bash
bash <(curl -s https://raw.githubusercontent.com/aspadeto/hermes_mpt_ops/main/scripts/bootstrap.sh) \
  --restore-backup /caminho/hermes-backup-*.tar.gz
```

**Documentação completa:**
- 📋 **[docs/RUNBOOK-RECUPERACAO.md](docs/RUNBOOK-RECUPERACAO.md)** — passo a passo
  detalhado (7 fases) + **como criar/obter cada segredo** (10 segredos documentados)
- ⚙️ **`scripts/bootstrap.sh`** — automação das fases 2-6 (clone, restore, .env, up)

**Cobertura da recuperação:**

| Camada | Fonte |
|--------|-------|
| Engenharia (scripts, docker, bancos) | `hermes_mpt_ops` (git) |
| Conhecimento (wiki) | `hermes_mpt_kb` (git) |
| Identidade (config, memória, tokens) | **Backup Google Drive** (diário) |

> ⚠️ **2 segredos não estão em nenhum backup** (vivem no `.env` local):
> `HERMES_WEBUI_PASSWORD` e `API_SERVER_KEY`. **Guardar em gerenciador de senhas.**

---

## 9. Limitações Conhecidas

- Ferramentas acionadas da WebUI rodam no container da WebUI, **não** no agente (issue #681 do hermes-webui)
- O Gateway API fica exposto apenas em `localhost` por padrão
- WebUI precisa de `HERMES_NIX_BUILD=1` (bug #6441 do hermes-webui — fix em andamento)
