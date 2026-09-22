# Arquitetura de pesquisa e ingestão de boletins

Estado atual (2026-09, decisão #41): a pesquisa de boletins foi **unificada sobre o corpus docling**.

## Corpus

| Pasta | Papel |
|-------|-------|
| `raw/boletins/` | PDFs baixados (fonte) |
| `boletins_docling/` | Markdown estruturado docling — **canônico para pesquisa** |
| `boletins/` | **REMOVIDA** — MDs planos abandonados (arquivados em `OPS/legado/`; apagados do disco) |

## Pipeline ingestão — split em 2 crons

1. **Download** — cron `Baixar boletins novos MPT` (06:00): `baixar_boletins_novos.py` baixa só os PDFs novos → `raw/boletins/`. **Não gera mais MD plano nem CSV.**
2. **Conversão Docling** — cron separado `Converter docling novos MPT` (07:00, 1h depois): `converter-docling-novos.py` converte só os PDFs **faltantes** (`--jobs 1` sequencial, anti-OOM) → `boletins_docling/`. Watchdog: sem faltantes, saída vazia (silêncio no cron).

O wrapper do docling delega para `/opt/data/hermes-data/.tool-venv/bin/python` — é aí que o `docling` está instalado (o python do sistema e o `.venv-bol` NÃO o têm).

## Ferramentas de pesquisa

Quem fica (canônico):
- **`pesquisar_boletins_fulltext.py`** — conteúdo/nome próprio nos `.md` docling (nível 2).
- **`pesquisar_docling.py`** — POC estruturado (referência, 5 perguntas hardcoded; não escalável mas serve de demo).

Usados pelo `benchmark_boletins.py` para avaliação.

Abandonadas e arquivadas em `OPS/legado/2026-09-pesquisa-legada/`:
- `pesquisar_boletins.py` (full-text MD plano)
- `pesquisar_boletins_csv.py` (factual)
- `exportar_atos_formatos.py` + `exportar_atos_docling.py` (geradores de CSV)
- `extrair_md_boletins.py` (gerador dos MDs planos)
- `data/indices/` (`atos_normativos.csv`, `_indice_md.json`)

Depois (fecha a #42), também arquivados em `legado/2026-09-pesquisa-legada/`:
- `catalogar_atos.py`, `indexar_boletins_prt14.py` (scripts)
- `data/atos.db`, `data/curadoria_atos.json` (dados)
- skill `catalogar-atos-boletins/` (inteira)

Pendências fechadas em lote: #42 `resolvida`; #27, #25, #29 `canceladas` (absorvidas pela unificação). A #26 (revisar o POC `pesquisar_docling.py`) permanece pendente — o POC é a referência do benchmark.

Verificação antes de arquivar scripts: conferir que nenhum script ATIVO faz import do alvo (`catalogar_atos.py` só era importado pelo já-arquivado `exportar_atos_formatos.py`). Referência de docs de skill ≠ dependência em runtime — só imports reais quebram.

## Regra de limpeza (pitfall)

**Ao remover um artefato gerado, o passo que o regenera continua correndo — a remoção se reverte sozinha.** Antes de apagar, desativar o regenerador, não só o artefato:
- Passo do pipeline/cron que o recria (ex: passos 5–6 do `baixar_boletins_novos.py`).
- `mkdir` auxiliar em `ops_paths.py` que recria a pasta vazia a cada import (remover o path da lista de `mkdir`, manter a constante por compatibilidade com scripts legados).

## Formato de arquivo (preferência do usuário)

Ao abandonar soluções/scripts/dados, **arquivar em `OPS/legado/<data>-<tema>/`** (reversível, `git` mantém histórico) em vez de `rm` permanente — salvo quando o usuário pedir apagar de vez. Mostrar o plano do que será removido/arquivado e pedir decisão **antes de apagar**.
