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
# CPU: ~124s/boletim, ~1.5GB RAM por processo. VM: 3 jobs paralelos (limite RAM)
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
# Converter todos os boletins (paralelo 3 jobs, só MD)
/opt/data/hermes-data/.tool-venv/bin/python \
  hermes_mpt_ops/scripts/converter_docling.py --todos --dest hermes_mpt_kb/boletins_docling --jobs 3

# Converter PDFs específicos
/opt/data/hermes-data/.tool-venv/bin/python \
  hermes_mpt_ops/scripts/converter_docling.py --pdf BS-012-2025.pdf BS-144-2025.pdf --dest hermes_mpt_kb/boletins_docling

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
- **RAM limitada:** usar `--jobs 3` em VM de 4.8GB (3 × ~1.5GB ≈ 4.5GB).
- **Mesmo número de ato pode existir em várias regionais** (ex: várias "Nº 26") — buscar DENTRO da seção da regional alvo (`## PRT-18ª REGIÃO`).
- **`Nº X` pode ser heading OU texto corrido** no output Docling — testar ambos.
- Avisos `NNPACK: Unsupported hardware` são inofensivos (sem otimização, roda em CPU).

## Referência

- Repo: `https://github.com/docling-project/docling`
- Doc: `https://docling-project.github.io/docling/`
- Relatório técnico: arXiv 2408.09869

