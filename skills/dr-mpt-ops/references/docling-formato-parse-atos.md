# Docling (boletins_docling/) vs MD plano (boletins/) — diferenças estruturais que quebram os parsers

Contexto da migração (ago/2026, pendências #35/#41/#42): o usuário decidiu que a
base de referência para regenerar conteúdo e pesquisar boletins é **`boletins_docling/`**
(MD estruturado por Docling), não mais o MD plano de `boletins/` nem o catálogo
SQLite (`atos.db`). Ao migrar, os parsers feitos para o MD plano **não funcionam**
no docling. Este doc lista as diferenças e o que precisa mudar.

## Diferenças estruturais (MD plano vs docling)

| Aspecto | MD plano (`boletins/`, via `extrair_md_boletins.py`) | Docling (`boletins_docling/`, via `converter_docling.py`) |
|---------|------------------------------------------------------|------------------------------------------------------------|
| Frontmatter | Tem `---\ndata: ...\ntitle: "BS 071-2025"\n---` | **NÃO tem** — ano vem do nome do arquivo `BS-012-2025.md` |
| Cabeçalho de ato | Linha solta `Nº 1529, DE 30 DE OUTUBRO DE 2024` | **Heading Markdown** `## Nº 56, DE 15 DE JANEIRO DE 2025` |
| Tipo+num explícito | `PORTARIA Nº 1030/2024` | `## DECISÃO N°111.2025` (varia; `N°` com grau também) |
| Marcador de página | `<!-- pág N -->` | `<!-- image -->` (sem número) |
| Assinaturas | linhas soltas | headings `## GLÁUCIO ARAÚJO DE OLIVEIRA`, `## RESOLVE :` |
| Regional | `PRT-18ª REGIÃO ...` | heading `## PRT-3ª REGIÃO - BELO HORIZONTE/MG` |
| Tabelas (ex: CC-4) | texto | tabelas Markdown reais `\| Chefe de Gabinete \| CC-4 \|` |

## Por que o parser atual (`catalogar_atos.py`) falha no docling

Testado em `BS-012-2025.md` (que tem ~15 atos reais): o `catalogar_atos.atos_por_arquivo()`
detecta **6 atos errados** (números truncados, `secao=None`, ementa vazando headings
vizinhos). Causas:
1. O parser itera **linhas soltas** e `detectar_num_data()` exige `^N[º°]` no início
   da linha — mas no docling o ato é `## Nº ...`, que **não casa** (começa com `##`).
2. `UNIDADE_RE` e o filtro de linha curta ignoram parte dos headings; assinaturas
   `## GLÁUCIO...` são tratadas como conteúdo.
3. `PAG_RE` busca `<!-- pág N -->` — inexistente no docling (só `<!-- image -->`).
4. `parse_frontmatter()` retorna `{}` no docling → `boletim_data` vira `None`.

O regex `N[º°]` (com classe de caractere) **já cobre** tanto `Nº` quanto `N°` — esse
não é o problema; o problema é o parser não aceitar headings e não ter frontmatter.

## O que um parser docling-aware deve fazer

1. Varrer **headings** `^## ` — remover o `## ` e tentar `detectar_num_data`/
   `detectar_tipo_num` no resto.
2. **Ano/boletim do nome do arquivo** (`BS-012-2025` → boletim 12/2025, ano 2025) —
   sem frontmatter.
3. **Data de circulação** só do conteúdo: `CIRCULAÇÃO: DD/MM/AAAA` (páginas 2+) ou
   capa `SEGUNDA-FEIRA, DD DE MÊS DE AAAA`.
4. **Página**: sem `<!-- pág N -->` → rastrear por contagem de `<!-- image -->`, ou
   deixar 0/desconhecido (não é crítico para busca).
5. **Tipo por seção**: `## PORTARIAS`→PORTARIA, `## DECISÕES/DECISÃO`→DECISÃO, etc.
6. **Órgão/assinatura**: headings `## O PROCURADOR-GERAL...` e `## RESOLVE :`.
7. **Ementa**: primeiras linhas após o heading do ato, ignorando headings/subheadings.

## Verificação de fidelidade (as 5 perguntas de referência)

Os arquivos docling PRESERVAM o conteúdo que as perguntas validadoras esperam
(confirmado em 23/08/2026):
- **Q1/Q2** (BS-012-2025): `## Nº 56` + tabela com `| Chefe de Gabinete | CC-4 |` ✓
- **Q3** (BS-144-2025): `Nº 1124` + ementa "SPARKS"/desfazimento ✓
- **Q5** (BS-145-2026): "ARIANNE" presente (também em ~50 outros boletins) ✓
Valide a migração rodando as 5 perguntas contra a nova base.

## Decisões estratégicas deste trabalho (registro)

- **#42**: usuário DESISTIU da pesquisa via `atos.db`/catálogo SQL. A busca passa a
  usar docling como base. Arquivos a remover/arquivar: `catalogar_atos.py`,
  `exportar_atos_formatos.py`, `indexar_boletins_prt14.py`, `data/atos.db`,
  `data/curadoria_atos.json`, `data/indices/atos_normativos.csv`, e a etapa de
  regeneração em `baixar_boletins_novos.py`.
- **Estratégia #41 (em andamento)**: regenerar o CSV a partir do docling (em vez de
  MD plano), **segmentar** cada base com **um script separado**, e migrar o full-text
  para docling.
- **Preferência do usuário**: trabalhar **um script por vez, interativo, com
  confirmação antes de editar**; sempre que precisar regenerar conteúdo (ex.: CSV),
  partir de `boletins_docling/`.
