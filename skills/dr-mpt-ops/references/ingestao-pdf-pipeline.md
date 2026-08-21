# Pipeline de Ingestão de PDFs (Portarias, Manuais, Artigos)

## Visão Geral

Pipeline padronizado para converter PDFs (portarias, manuais, artigos, papers) em artigos Markdown estruturados na base de conhecimento (`KB_PATH/raw/articles/<slug>/`).

## Script Canônico

`OPS_PATH/scripts/pdf2kb.py` (anteriormente `pdf2wiki.py`)

## Fluxo Completo

```bash
cd KB_PATH
.venv/bin/python scripts/pdf2kb.py <arquivo.pdf> [--dest DIR] [--slug NOME] [--no-render]
```

## Saída Gerada

```
raw/articles/<slug>/
├── artigo.md          # Markdown estruturado (texto + tabelas + páginas)
├── fonte.pdf          # PDF original (cópia imutável)
├── assets/            # Imagens extraídas + PNGs de páginas com tabelas
└── indexacao.json     # Metadados detectados (para confirmação)
```

## Frontmatter do Artigo

```yaml
---
tipo: artigo
titulo: "Título do Documento"
fonte: arquivo.pdf
paginas: N
conversao: 2026-08-19
---
```

## Metadados de Indexação (`indexacao.json`)

```json
{
  "arquivo_original": "portaria-822-2021.pdf",
  "slug": "portaria-822-2021",
  "titulo": "Portaria PGT nº 822/2021 - Diretrizes para Gestão de Processos no MPT",
  "autores": ["Alberto Bastos Balazeiro"],
  "publicacao": "PGT / MPT",
  "ano": "2021",
  "tema": "Gestão de Processos, Cadeia de Valor, Macroprocessos, BPM, PGEA",
  "paginas": 3,
  "tabelas": [],
  "imagens": ["p001-img-20.jpeg"],
  "status": "confirmado"
}
```

**Campos obrigatórios para confirmação:**
- `titulo` — título limpo (sem metadados do PDF)
- `autores` — lista (PGT, MPT, órgão emissor)
- `publicacao` — órgão publicador
- `ano` — ano da portaria/documento
- `tema` — palavras-chave separadas por vírgula
- `status`: `aguardando_confirmacao` → `confirmado`

## Pipeline de Confirmação (Obrigatório)

1. **Converter** → gera `indexacao.json` com status `aguardando_confirmacao`
2. **Apresentar JSON ao usuário** — usuário revisa/enriquece metadados
3. **Usuário confirma** → status → `confirmado`
4. **Enriquecer frontmatter** do `artigo.md` com metadados confirmados
5. **Atualizar catálogo** `raw/articles/index.md`
6. **Commit + push** (auto-commit cobre)

## Exemplos Ingeridos

### Portaria PGT nº 822/2021
- **Arquivo**: `portaria-822-2021.pdf` (47 KB, 3 págs)
- **Slug**: `portaria-822-2021`
- **Título**: "Portaria PGT nº 822/2021 - Diretrizes para Gestão de Processos no MPT"
- **Tema**: "Gestão de Processos, Cadeia de Valor, Macroprocessos, BPM, Planejamento Estratégico, PGEA"
- **PGEA**: 20.02.0001.0005529/2021-06
- **Revoga**: Portaria PGT nº 567/2019

### Manual Módulo Finanças Cosmos MPU v1.6
- **Arquivo**: `manualFinancas_1_6.pdf` (7.5 MB, 76 págs)
- **Slug**: `manualfinancas-1-6`
- **Título**: "Manual do Módulo de Finanças - Cosmos MPU (Versão 1.6)"
- **Tema**: "Finanças, Orçamento, Empenho, SIAFI, eSocial, Sistema Cosmos MPU"
- **Tabelas**: 2 (páginas 2 e 69)
- **Imagens**: 188 (inclui 2 renders de páginas com tabelas)

## Pitfalls

- **Título detectado errado**: heurística pega o maior fonte da página 1 → frequentemente pega cabeçalho/rodapé. Sempre validar/editar `titulo` no `indexacao.json`.
- **Autores não detectados**: papers arXiv usam formato "1st/2nd Nome" ou superscripts †/‡. Extrair da página 1 manualmente.
- **Slug feio**: nome do arquivo com acento/número grudado (`ofício-circular-0004162026`). Renomear pasta para slug limpo (`oficio-circular-416-2026`) e atualizar em 3 lugares: `indexacao.json` (slug), frontmatter `artigo.md`, catálogo `index.md`. Use `git add -A raw/articles/` para stagear renames.
- **`--dest` com slug**: se passar `--dest raw/articles/hyde-2022 --slug hyde-2022`, cria pasta aninhada `hyde-2022/hyde-2022/`. Corrigir: `mv hyde-2022/hyde-2022/* hyde-2022/ && rmdir hyde-2022/hyde-2022`.
- **Render de tabelas**: `--no-render` pula PNGs de fallback. Para boletins/portarias, tabelas simples funcionam bem em MD puro.
- **Arquivo já existe**: script aborta se `--slug` já existe. Remover pasta ou usar `--slug` diferente.
- **Autores de papers arXiv**: não detectados pela heurística (formato "1st/2nd Nome" ou "Nome†"). Extrair da página 1 manualmente.
- **Frontmatter enriquecido**: após confirmação, atualizar `artigo.md` com metadados completos antes de commitar.

## Exemplos Confirmados

| Documento | Slug | Status |
|-----------|------|--------|
| Portaria PGT nº 822/2021 | portaria-822-2021 | ✅ confirmado |
| Manual Finanças Cosmos v1.6 | manualfinancas-1-6 | ✅ confirmado |

## Próximos Documentos Candidatos

- Portarias PGT recentes (823+)
- Manuais de outros módulos Cosmos
- Papers arXiv citados em vídeos/frameworks
- Resoluções CSMPT transcritas em boletins