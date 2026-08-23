# Boletins no KB — Papéis das pastas e estratégia de consolidação

> Decisão (pendência #35, 23/08/2026). Documenta os papéis das 3 pastas de
> boletins no `hermes_mpt_kb` e a estratégia para, no futuro, descartar a pasta
> de MDs planos sem perder dados nem romper scripts.

## Por que 3 pastas existem

O mesmo corpus de boletins vive em 3 representações diferentes no KB, cada uma
gerada por um pipeline distinto ao longo da evolução do ambiente:

| Pasta | Conteúdo | Gerado por | Qtd (ago/2026) | Papel |
|-------|----------|-----------|----------------|-------|
| `raw/boletins/` | **PDFs** originais | `baixar_boletim.py` (cloudscraper) | 512 | **Fonte imutável** — documento original do portal |
| `boletins/` | **.md planos** (frontmatter `data:`) | `extrair_md_boletins.py` (PyMuPDF) | 512 | Representação legada, **em desuso** |
| `boletins_docling/` | **.md docling** estruturados (headings + tabelas) | `converter_docling.py` (Docling) | 512 | **Representação pesquisável de referência** |

## Decisão (pendência #35)

**Manter todas as 3 pastas por ora e documentar os papéis.** A estratégia é
**evolutiva**: migrar gradualmente os consumidores (scripts) que ainda leem a
pasta `boletins/` (MD plano) para `boletins_docling/`, até que seja possível
**descartar a pasta `boletins/`**, permanecendo apenas:

- `raw/boletins/` — PDFs (fonte imutável)
- `boletins_docling/` — MDs estruturados (representação pesquisável)

## Papel de cada pasta (fonte de verdade)

1. **`raw/boletins/` = fonte da verdade bruta.** PDFs baixados do portal MPT.
   NUNCA regenerado por script; é o documento original. Serve de origem para
   qualquer re-extração e para conferência de fidelidade.
2. **`boletins_docling/` = representação pesquisável de referência.** MD
   estruturado (headings `##`, tabelas Markdown, seções). É o formato que os
   **novos** scripts de busca devem usar. Usa `N°` (grau) no lugar de `Nº`.
3. **`boletins/` = representação legada (em desuso).** MD plano com frontmatter.
   Ainda referenciado por scripts antigos. **Destino: ser descartada** quando
   todos os consumidores migrarem.

## Estratégia de evolução (até descartar `boletins/`)

### Critérios de prontidão para descartar `boletins/`
- [ ] Nenhum script ativo lê `boletins/` (MD plano)
- [ ] Todos os scripts de busca/catálogo apontam para `boletins_docling/`
- [ ] Pendência #41 (unificar 3 gerações de pesquisa) resolvida
- [ ] Índices (`_indice_md.json`, `atos_normativos.csv`) regenerados do corpus docling
- [ ] Regex `Nº`→`N°` ajustada nos parsers (pendência #33)
- [ ] Validação neuro-simbólica (#24) — se destravada — lê de docling

### Consumidores atuais a migrar
| Script | Lê hoje | Migrar para | Pendência |
|--------|---------|-------------|-----------|
| `pesquisar_boletins.py` | `boletins/` + CSV | `boletins_docling/` | #25, #41 |
| `catalogar_atos.py` | pastas `YYYY-MM-DD/` | `boletins_docling/` | #27, #41 |
| `exportar_atos_formatos.py` | `boletins/` | `boletins_docling/` | #29 |
| `pesquisar_docling.py` | `boletins_docling/` (parcial) | genérico sobre docling | #26, #41 |

## Quando NÃO descartar `boletins/`

- Se algum script ainda depender do frontmatter `data:` que só existe no MD
  plano (o docling não tem frontmatter — o ano vem do nome do arquivo).
- Se houver fidelidade de extração não validada entre plano e docling.

> ⚠️ Antes de remover a pasta, confirmar que PDFs em `raw/boletins/` cobrem
> integralmente os 512 boletins (para re-extração futura não perder nada).

## Git

As 3 pastas são versionadas no `hermes_mpt_kb`. A remoção de `boletins/` (futura)
será um `git rm boletins/` + atualização de scripts/docs. Nenhum `.db` vive nestas
pastas.
