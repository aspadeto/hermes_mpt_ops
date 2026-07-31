# DR MPT OPS — Repositório de Operações

Repositório complementar ao [dr_mpt_kb](https://github.com/aspadeto/dr_mpt_kb) (conhecimento).

**Divisão de trabalho:**
- `dr_mpt_kb` = **conhecimento** — PGEAs, artigos, referências, processos (documentos)
- `dr_mpt_ops` = **engenharia** — scripts, bancos de dados, configurações versionáveis

## Estrutura

```
dr_mpt_ops/
├── scripts/     ← todos os scripts (dados + automação)
├── data/        ← bancos SQLite versionados (pendencias.db, futuramente prt14.db)
├── configs/     ← templates de configuração SEM segredos (.env.example, compose.example)
└── docs/        ← notas técnicas de infra
```

## Scripts

| Script | Função | Depende de |
|--------|--------|------------|
| `pdf2wiki.py` | Converte PDF → Markdown + assets para o KB | pymupdf (venv) |
| `pendencia.py` | Sistema de pendências (TODO assíncrono) | sqlite3 (stdlib) |
| `consultar.py` | Consultas SQL no prt14.db | — |
| `importar-demandas.py` | Importa demandas do SGA para prt14.db | — |
| `importar-execucao.py` | Importa execução orçamentária | — |
| `hermes-backup.py` | Backup do Hermes para Google Drive | google-api (venv) |
| `wiki-auto-commit.sh` | Auto-commit do KB (cron 10min) | git |
| `update_hermes-agente-src.sh` | Recria volume do hermes-agent no Docker | docker |

## Instalação

```bash
# No host, clonar
git clone https://github.com/aspadeto/dr_mpt_ops.git

# Venv para scripts com dependências (pdf2wiki)
uv venv .venv
uv pip install pymupdf
```

## Segredos

⚠️ **NUNCA** commitar tokens, credentials ou `.env`. O `.gitignore` bloqueia
`GITHUB_TOKEN.txt`, `.git-credentials`, `client_secret*.json`, etc.
