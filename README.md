# DR MPT — Repositório de Operações (dr_mpt_ops)

Repositório de **engenharia e operações** da Diretoria Regional do MPT (Rondônia/Acre).
Complementar ao [dr_mpt_kb](https://github.com/aspadeto/dr_mpt_kb) (conhecimento).

**Divisão de trabalho:**
- `dr_mpt_kb` = **conhecimento** — PGEAs, artigos, referências, processos (documentos)
- `dr_mpt_ops` = **engenharia** — scripts, bancos de dados, configurações versionáveis

---

## 1. Visão Geral da Infraestrutura

O ambiente roda o **Hermes Agent** com a **Hermes WebUI** em dois containers conectados
(via Docker Compose no host), acessíveis remotamente via **Tailscale**.

| Componente | Endereço | Porta |
|-----------|----------|-------|
| Hermes Agent (gateway) | `localhost` (host) | 8642 |
| Hermes WebUI | `https://as7-hermes-docker.tail15f7e7.ts.net` | 8787 |
| Dashboard | `localhost` (host) | 9119 |

> Detalhes completos do Tailscale (grants, serve, SSH): `wiki/referencias/tailscale-acesso-remoto.md`

### Estrutura de Volumes (host → container)

| Pasta no host | Montagem no container | Conteúdo |
|---------------|----------------------|----------|
| `~/.hermes` | `/home/hermes/.hermes` | Config, sessões, skills, memória, cache |
| `~/hermes-agent` | `/opt/hermes` | Código-fonte do Hermes Agent |
| `~/hermes-data` | `/opt/data/hermes-data` | **Este repositório** + wiki + tokens |
| `~/workspace` | `/workspace` | Área de trabalho (WebUI) |

> **Nota:** O container usa UID/GID `1000` por padrão. Se seu usuário host tem UID
> diferente, ajuste no `.env`: `echo "UID=$(id -u)" >> .env` e `GID=$(id -g)`.

---

## 2. Estrutura do Repositório

```
dr_mpt_ops/
├── scripts/     ← todos os scripts (dados + automação)
├── data/        ← bancos SQLite versionados (pendencias.db, prt14.db)
├── configs/     ← templates de configuração SEM segredos (.env.example, compose.example)
└── docs/        ← notas técnicas de infra
```

---

## 3. Scripts

| Script | Função | Depende de |
|--------|--------|------------|
| `pdf2wiki.py` | Converte PDF → Markdown + assets para o KB | pymupdf (venv) |
| `pendencia.py` | Sistema de pendências (TODO assíncrono) | sqlite3 (stdlib) |
| `consultar.py` | Consultas SQL no prt14.db | — |
| `importar-demandas.py` | Importa demandas do SGA para prt14.db | — |
| `importar-execucao.py` | Importa execução orçamentária | — |
| `hermes-backup.py` | Backup do Hermes para Google Drive | google-api (venv) |
| `wiki-auto-commit.sh` | Auto-commit do KB + OPS (cron 10min) | git |
| `update_hermes-agente-src.sh` | Recria volume do hermes-agent no Docker | docker |

### Wrappers de cron

O cron do Hermes exige scripts reais em `~/.hermes/scripts/` (sem symlinks, sem
argumentos, sem caminho absoluto — decisão de segurança do scheduler). O padrão é:

```
dr_mpt_ops/scripts/          ← CÓDIGO REAL (versionado)
~/.hermes/scripts/           ← WRAPPERS (atalhos p/ cron, não versionados)
```

> Detalhes completos: `wiki/referencias/cron-scripts-hermes.md`

---

## 4. Instalação

```bash
# No host, clonar
git clone https://github.com/aspadeto/dr_mpt_ops.git

# Venv para scripts com dependências (pdf2wiki, backup)
uv venv .venv
uv pip install pymupdf
```

---

## 5. Atualização da Infraestrutura

### Atualizar a imagem do agente

```bash
docker compose pull
docker compose down
docker compose up -d
```

### Atualizar a pasta de código-fonte (`~/hermes-agent`)

Como é bind mount, o Docker **não** atualiza a pasta do host automaticamente:

**Opção A — Copiar da imagem (recomendado)**

```bash
docker create --name temp-hermes nousresearch/hermes-agent:latest
rm -rf ~/hermes-agent/*
docker cp temp-hermes:/opt/hermes/. ~/hermes-agent/
docker rm temp-hermes
```

**Opção B — Clonar do GitHub**

```bash
git clone https://github.com/NousResearch/hermes-agent.git ~/hermes-agent
# atualizar depois:
cd ~/hermes-agent && git pull
```

Após qualquer opção: `docker compose down && docker compose up -d`

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
`GITHUB_TOKEN.txt`, `.git-credentials`, `client_secret*.json`, `google_token.json` etc.

Segredos vivem **fora** dos repositórios, na raiz de `hermes-data/`:
- `GITHUB_TOKEN.txt` — token do GitHub (clones/push)
- `.git-credentials` — credenciais git (store)
- `.env` — variáveis de ambiente com chaves

Para versionar configuração, usar **templates** em `configs/` (sem valores).

---

## 8. Limitações Conhecidas

- Ferramentas acionadas da WebUI rodam no container da WebUI, **não** no agente (issue #681 do hermes-webui)
- O Gateway API fica exposto apenas em `localhost` por padrão
- WebUI precisa de `HERMES_NIX_BUILD=1` (bug #6441 do hermes-webui — fix em andamento)
