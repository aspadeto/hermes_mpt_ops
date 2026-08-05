# FLUXO DE INGESTÃO — Documentos para a Base de Conhecimento

**Objetivo:** padronizar o caminho que um documento (ex: PGEA em PDF) percorre desde a
chegada no workspace até a publicação nos repositórios — **sem duplicação de conteúdo
nem de soluções**.

**Aplicável a:** qualquer documento administrativo em PDF (PGEAs, portarias, contratos,
artigos) processado pelo agente.

---

## 1. Papéis dos repositórios (regra de 2 linhas)

| Área | Papel | Contém |
|------|-------|--------|
| `hermes_mpt_kb` | **Conhecimento** — o que se sabe | PDFs brutos (`raw/`), extrações, resumos, análises, wiki |
| `hermes_mpt_ops` | **Soluções** — o que se faz com o conhecimento | scripts, bancos, configs, runbooks, relatórios de operação |
| `/workspace` (WebUI) | **Balcão de entrada** — trânsito temporário | nada permanente; é lavável |

> **Princípio:** KB = dados e conhecimento · OPS = código e operação · workspace = buffer.
> Um artefato vive em **um único lugar** — nunca em dois.

---

## 2. Regras de ouro

1. **Workspace nunca é repositório** — nada de produção mora nele; é limpo após cada ingestão.
2. **Documento nunca duplica** — 1 cópia do PDF em `KB/raw/<categoria>/`; o workspace apaga após migração.
3. **Script só entra no OPS quando consolidado** — rascunhos morrem no workspace (não versionar).
4. **Relatório de auditoria = dado de operação** → `OPS/data/auditorias/` (não polui o KB).
5. **Frontmatter YAML obrigatório** em todo MD do KB (tipo, numero, data, assunto, interessado, tags).
6. **Toda ação registrada** no `KB/log.md` (formato `## [data] verbo | título`).

---

## 3. Fluxo passo a passo

```
┌─ /workspace (WebUI) ──────────────────────────────────────────┐
│ ① PDF chega (upload/arraste no chat ou no workspace)          │
│ ② Auditoria roda: python3 <OPS>/scripts/extrair_auditar_pgea.py PGEA.pdf │
│    → gera PGEA_*.md (extração) + auditoria_PGEA_*.md          │
│ ③ Você valida o relatório (decisão final é humana)            │
└───────────────────────────────┬───────────────────────────────┘
                                │ aprovado?
              ┌─────────────────┴──────────────────┐
              ▼                                    ▼
┌─ hermes_mpt_kb ──────────────────┐  ┌─ hermes_mpt_ops ─────────────────┐
│ ④ PDF → raw/pgeas/ (ou categoria)│  │ ⑦ script consolidado → scripts/   │
│ ⑤ extração → pgeas/pgea-xxx/     │  │ ⑧ relatório → data/auditorias/   │
│    extracao.md (+ frontmatter)   │  │                                  │
│ ⑥ index.md + log.md atualizados  │  │                                  │
└──────────────────────────────────┘  └──────────────────────────────────┘
                                │
                                ▼
               ⑨ commit + push (KB e OPS separados)
               ⑩ workspace LIMPO (arquivos-fonte apagados)
```

### Passos detalhados

| # | Ação | Comando / local |
|---|------|-----------------|
| ① | PDF chega | `/workspace` (WebUI) |
| ② | Auditoria | `python3 /opt/data/hermes-data/hermes_mpt_ops/scripts/extrair_auditar_pgea.py /workspace/PGEA_*.pdf` |
| ③ | Validação humana | relatório `auditoria_*.md` — suspeitas → judge LLM amostral |
| ④ | PDF → KB | `cp PGEA.pdf KB/raw/pgeas/` (verificar sha256) |
| ⑤ | Extração → KB | pasta `KB/pgeas/<slug>/extracao.md` (usar pasta existente se o PGEA já tiver; ex: `pgea-biblioteca`) |
| ⑥ | Índices | atualizar `KB/pgeas/index.md` e anexar entrada em `KB/log.md` |
| ⑦ | Script → OPS | `cp script.py OPS/scripts/` + `chmod +x` |
| ⑧ | Relatório → OPS | `cp auditoria_*.md OPS/data/auditorias/` (nome curto: `auditoria-pgea-281-2026.md`) |
| ⑨ | Git | commit + push **separados** em KB e OPS (mensagens descritivas) |
| ⑩ | Limpeza | remover do workspace: PDF, extração, relatório, scripts de rascunho |

---

## 4. Convenção de nomes

| Artefato | Padrão | Exemplo |
|----------|--------|---------|
| PDF no KB | nome original do sistema | `PGEA 000385-2026-14-900-9_...pdf` |
| Pasta de PGEA | `pgeas/pgea-<num>-<ano>/` | `pgeas/pgea-337-2026/` |
| Extração | `extracao.md` (frontmatter YAML obrigatório) | `pgeas/pgea-337-2026/extracao.md` |
| Relatório no OPS | `data/auditorias/auditoria-pgea-<num>-<ano>.md` | `auditoria-pgea-337-2026.md` |
| Script | `scripts/<verbo>_<alvo>.py` | `scripts/extrair_auditar_pgea.py` |

---

## 5. Ferramenta de extração + auditoria (`scripts/extrair_auditar_pgea.py`)

Valida a extração de um PGEA em 3 camadas (custo zero):

| Camada | Verifica |
|--------|----------|
| 1+2 | Inventário de peças (cabeçalho `TIPO NNN.2026 (ID) − PGEA...`) + páginas vazias/escaneadas |
| 3 | Completude (peça ausente?), cobertura (página faltando?) e fidelidade (páginas pequenas por conteúdo exato; grandes por razão de volume) |

**Lições empíricas (importantes para evoluir a ferramenta):**
- Páginas pequenas (< ~500 chars) devem ser comparadas **por conteúdo**, não por volume — o marcador `<!-- pág N -->` distorce a razão.
- O parser de chunks deve parar em `\n## ` (início de seção), senão o cabeçalho da peça seguinte "vaza" para o chunk anterior (bug real encontrado na 1ª execução).

---

## 6. Exemplo real (PGEAs 281/337/372 — 2026-08-05)

Primeira ingestão usando este fluxo: 3 PGEAs auditados (0 suspeitas), migrados e
versionados. Ver `KB/log.md` (entrada `[2026-08-05] ingerir`) e `OPS/data/auditorias/`.
