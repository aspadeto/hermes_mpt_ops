# Extração PDF→MD de boletins (pipeline flat)

Técnica validada em ago/2026 (lote de 508 boletins). Converte os PDFs de
`KB_RAW_BOLETINS/` em Markdown plano em `KB_BOLETINS/`.

## Script

`OPS_PATH/scripts/extrair_md_boletins.py` — fez **porque** o `pdf2kb.py`
gera estrutura `raw/articles/<slug>/` com assets para artigos; boletins precisam
de saída plana, um arquivo por boletim. Dependência: PyMuPDF, venv
`OPS_PATH/.venv-bol` (o mesmo usado pelo `baixar_boletim.py`).

```bash
cd OPS_PATH
.venv-bol/bin/python scripts/extrair_md_boletins.py \
  --orig KB_RAW_BOLETINS --dest KB_BOLETINS \
  [--filtro glob]    # default *.pdf; use para testar 1 arquivo antes do lote
```

Argumentos: `--orig` (default `KB_RAW_BOLETINS`), `--dest` (default `KB_BOLETINS`),
`--filtro` (default `*.pdf`).

## Formato de saída (fiel ao histórico da base)

```
---
title: "BS 071-2025"
data: 2025-04-14
created: 2025-04-14
updated: 2025-04-14
type: boletim-servico
tags: [boletim, mpt, 2025-04]
---

# BS-071-2025

> 16 paginas

## Capa

<!-- pag 1 -->
<texto página 1>
<!-- pag 2 -->
...
```

## Detecção da data (`data:` no frontmatter)

Prioridade dentro de `detectar_data()`:
1. `CIRCULAÇÃO: DD/MM/AAAA` (nas páginas 2+ de cada boletim)
2. Cabeçalho da capa `DD DE MÊS DE AAAA` (ex: "SEGUNDA-FEIRA, 14 DE ABRIL DE 2025")
3. Fallback `DD/MM/AAAA`

Boletins extraordinários (`BS-NNN.N-AAAA`) NÃO têm data na página 1 (só o
cabeçalho "BOLETIM EXTRAORDINÁRIO"); a data só aparece a partir da página 2 no
`CIRCULAÇÃO`. O laço atual olha as 3 primeiras páginas por isso.

## Pitfalls

- **NÃO usar `f"{mes:02d}"` quando `mês` vem de um dict de nomes** (`MESES[...]`
  → string `"04"`). Causa `ValueError: Unknown format code 'd' for object of
  type 'str'`. Normalizar num helper `_fmt(ano: int, mes: str, dia: int)` usando
  `mes.rjust(2, "0")` e `f"{ano:04d}-{mes}-{dia:02d}"`. (Aconteceu ao copiar o
  padrão de formatação do `catalogar_atos.py` sem notar que lá o mês era int.)
- **Texto extraído difere do MD histórico de referência só em linhas em branco
  entre páginas** — não é bug. Comparar ignorando linhas vazias.
- **Sempre validar em mostra** (`--dest /tmp/test_md --filtro "BS-071-*.pdf"`,
  comparar com o MD antigo de `boletins/2025-04/`), antes de rodar o lote nos
  arquivos reais do KB.

## Estrutura de destino (preferência do usuário)

- **PDFs**: `KB_RAW_BOLETINS/` (canônico, plano — 508 em ago/2026)
- **MDs**: `KB_BOLETINS/` **PLANOS na raiz, SEM subcarpetas por mês**

O usuário prefere SEM subpasta por mês porque os boletins já são numerados
(`BS-NNN-AAAA` é único) — subpasta por mês torna difícil achar um boletim
específico. Ao reestruturar, os 70 MDs antigos de `boletins/2025-04|05|06/`
ficam duplicados em relação aos novos da raiz; remover as subpastas só com aval
explícito do usuário (arquivos já versionados).

## Commit

Após gerar os MDs: `git add boletins/ && git commit`. Commit de referência:
`478ac12` ("boletins: extração completa PDF→MD plano (508 boletins)").