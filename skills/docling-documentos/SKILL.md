---
name: docling-documentos
description: "Converter PDFs com Docling preservando estrutura."
version: 1.0.0
author: HAL 9000
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [docling, pdf, estrutura, rag, boletins, pesquisa]
    category: produtividade
---

# Docling — Conversão Estruturada de Documentos

Usa o **Docling** (IBM, MIT license) para extrair a **estrutura em árvore** de
PDFs (headings hierárquicos, seções, tabelas reais, ordem de leitura) — em vez
de achatá-los em texto plano como o PyMuPDF. Validado em PoC de pesquisa em
boletins do MPT (ago/2026): 5/5 acertos.

## Quando Ativar

- Usuário pedir conversão de PDF preservando **estrutura hierárquica** (headings/tabelas)
- PoC de pesquisa/Chunkless RAG sobre documentos estruturados
- Comparar Docling vs. PyMuPDF (markdown plano)

## Instalação

```bash
# no .tool-venv (Python 3.12)
uv pip install --python /opt/data/hermes-data/.tool-venv/bin/python docling
# requer Python >= 3.10; baixa modelos de layout/OCR na primeira execução (centenas de MB)
# CPU: ~124s/boletim, ~1.5GB RAM por processo. ⚠️ ANTI-OOM (21/08/2026): --jobs 3 ESTOURA RAM (11GB) e mata processo + WebUI — usar SEMPRE --jobs 1.
```

## Diretório de saída

**Definitivo:** `hermes_mpt_kb/boletins_docling/` (markdown estruturado por boletim `BS-NNN-AAAA.md`)

## Scripts (versionados no OPS)

| Script | Função |
|--------|--------|
| `hermes_mpt_ops/scripts/converter_docling.py` | PDF → markdown estruturado (paralelo, `--jobs N`) |
| `hermes_mpt_ops/scripts/pesquisar_docling.py` | Pesquisa por estrutura Docling (headings + tabelas) |

## Uso

```bash
# Converter todos os boletins (SEQUENCIAL jobs=1 — anti-OOM, validado)
export HERMES_DATA_ROOT=/opt/data/hermes-data
export OPS_PATH=/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops
export KB_PATH=/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb
/opt/data/hermes-data/.tool-venv/bin/python \
  hermes_mpt_ops/scripts/converter_docling.py --todos --jobs 1

# Converter PDFs específicos (aceita nome com/sem .pdf)
/opt/data/hermes-data/.tool-venv/bin/python \
  hermes_mpt_ops/scripts/converter_docling.py --pdf BS-012-2025 BS-144-2025 --jobs 1

# Pesquisar (pergunta) — lê de boletins_docling/
/opt/data/hermes-data/.tool-venv/bin/python \
  hermes_mpt_ops/scripts/pesquisar_docling.py "Qual portaria altera a PRT10?"
```

## API essencial (README oficial)

```python
from docling.document_converter import DocumentConverter
converter = DocumentConverter()
result = converter.convert("caminho/ou/url.pdf")
doc = result.document
doc.export_to_markdown()   # markdown estruturado
doc.export_to_dict()       # JSON lossless (árvore completa)
doc.export_to_text()       # texto simples
```

## O que preserva (e o que não)

**Preserva:**
- Headings hierárquicos (`## PORTARIAS`, `## Nº 56, DE ...`)
- Tabelas Markdown reais (`| Chefe de Gabinete | CC-4 |`)
- Seções e ordem de leitura

**Não preserva (limitação):** PDFs escaneados sem OCR nativo (precisa OCR, que
o Docling faz via RapidOCR); fórmulas complexas podem degradar.

## Pitfalls

- **`export_to_dict()` retorna dict** — serializar com `json.dumps(..., ensure_ascii=False)` antes de escrever.
- **Primeira conversão baixa modelos** (layout/OCR) e demora mais.
- **Conversão ~2-3min/PDF em CPU** (vs. PyMuPDF instantâneo) — usar seletivamente.
- **RAM limitada — NUNCA `--jobs 3`:** a VM tem 11GB; 3 workers (~1.5-3GB cada) + sistema + WebUI estouram e o OOM killer mata o processo (às vezes derrubando o WebUI). **Sempre `--jobs 1`** (sequencial, ~2-3min/PDF). Validado em 21/08/2026 na conversão dos 512 boletins.
- **Env vars viciadas criam pasta órfã na raiz:** `KB_PATH`/`OPS_PATH` podem estar setadas apontando para `/opt/data/hermes-data/hermes_mpt_kb` (raiz) em vez de `mpt_workspace/`. Como o `ops_paths.py` respeita as env vars (prioridade), o Docling grava na raiz errada. **Sintoma:** pasta `hermes_mpt_kb/` na raiz do hermes-data recriada. **Fix:** `export HERMES_DATA_ROOT=/opt/data/hermes-data`, `OPS_PATH=.../mpt_workspace/hermes_mpt_ops`, `KB_PATH=.../mpt_workspace/hermes_mpt_kb` antes de rodar.
- **`--pdf` aceita nome com ou sem `.pdf`:** corrigido em 21/08 — antes, passar `BS-012-2025` (sem extensão) resultava em "0 PDFs convertidos" porque o script não acrescentava `.pdf`.
- **Mesmo número de ato pode existir em várias regionais** (ex: várias "Nº 26") — buscar DENTRO da seção da regional alvo (`## PRT-18ª REGIÃO`).
- **`Nº X` pode ser heading OU texto corrido** no output Docling — testar ambos.
- Avisos `NNPACK: Unsupported hardware` são inofensivos (sem otimização, roda em CPU).

## Referência

- Repo: `https://github.com/docling-project/docling`
- Doc: `https://docling-project.github.io/docling/`
- Relatório técnico: arXiv 2408.09869

