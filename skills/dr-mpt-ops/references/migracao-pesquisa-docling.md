# Migração da pesquisa de boletins para o corpus docling (ago/2026)

Estratégia acordada (pendências #35 e #41): os boletins DOCLING
(`hermes_mpt_kb/boletins_docling/`) são o corpus canônico de referência. Toda
nova geração de dados/índice deve partir deles. Os `.md` planos (`boletins/`,
com frontmatter) são legado em desuso e serão descartados quando os consumidores
migrarem.

## Papéis das 3 pastas (decisão #35)
- `raw/boletins/` — PDFs, fonte imutável.
- `boletins_docling/` — MD estruturado, referência pesquisável (canônico).
- `boletins/` — MD plano legado, em desuso (a descartar).

Documento canônico: `hermes_mpt_ops/docs/BOLETINS-PAPEIS-E-ESTRATEGIA.md`.

## Scripts criados nesta migração
- `scripts/detectar_atos_docling.py` — parser de atos em `.md` docling.
  `atos_por_arquivo_docling(md)` detecta atos por heading `## Nº X, DE...` OU
  linha solta `Nº X, DE...`, captura seção corrente, órgão, ementa; infere o
  tipo quando a seção é genérica (`_inferir_tipo_de_trecho`).
- `scripts/exportar_atos_docling.py` — gera `atos_normativos.{csv,md,tsv,toml}`
  a partir de `boletins_docling/`. Colunas idênticas ao antigo CSV.
- `scripts/pesquisar_boletins_csv.py` — busca FACTUAL (nível 1) no
  `atos_normativos.csv` docling: por nº/ano/tipo/órgão/boletim.
- `scripts/pesquisar_boletins_fulltext.py` — busca por CONTEÚDO (nível 2) nos
  `.md` docling: nome próprio em maiúsculas + termos-chave (com stopwords).

O `pesquisar_boletins.py` híbrido antigo (que lia `boletins/` plano) ficou
intacto por enquanto; migrar depois.

## Estrutura do docling — diferenças CRÍTICAS vs. MD plano
1. **Sem frontmatter.** Ano e número do boletim vêm do NOME do arquivo
   (`BS-012-2025` → boletim `12/2025`, ano 2025). Funções `_ano_boletim`/
   `numero_boletim`.
2. **Atos podem ser heading `## Nº 56, DE...` OU linha solta `Nº 1124, DE...`**
   (no BS-144 o `Nº 1124` é linha solta). O parser precisa aceitar os dois.
3. **A ementa do ato vem ANTES do heading `Nº`** (o docling coloca o corpo do
   ato/ementa/tabela e só depois o `## Nº XX`). NO REVERSO do MD plano (que é
   número primeiro, ementa depois). Consequência: inferir tipo/ementa a partir
   do trecho SEGUINTE ao heading falha (ex: Nº56 do BS-012 vira "ATO" em vez de
   PORTARIA, porque a tabela vem antes). Melhorar no benchmark.
4. **Sem `<!-- pág N -->`** — o docling usa `<!-- image -->`. O parser conta
   imagens como proxy de página.
5. **Números repetem por regional** e a mesma numeração aparece em vários
   boletins. Pior: às vezes o ato de uma regional NÃO tem heading `Nº` associado
   (ex: Portaria 26/2025 PRT18 no BS-050 — o `Nº 26` na linha 770 é da PRT-17
   Vitória; o ato da PRT18 é identificado só por `## PRT-18ª REGIÃO` + conteúdo
   "PTM de Luziânia"). Desambiguar por regional + conteúdo, não só número.
6. **Tabelas Markdown preservadas** (`| Chefe de Gabinete | CC-4 |`) — essencial
   para perguntas de gratificação/código (Q2), mas o full-text atual não extrai
   resposta de tabela.

## Achados do teste (baseline nas 5 perguntas)
| Pergunta | CSV (factual) | Full-text (conteúdo) |
|----------|--------------|----------------------|
| Q1 Port.56 PRT10 | ✅ `012/2025` (tipo sai "ATO") | ⚠️ erra (BS-179) |
| Q2 CC-4 (tabela) | — | ⚠️ não extrai de tabela |
| Q3 SPARKS 1124 | ✅ `144/2025` | — |
| Q4 Port.26 PRT18 | ⚠️ | ⚠️ exige regional+conteúdo (sem heading Nº) |
| Q5 ARIANNE | ✅ | ✅ `BS-142-2026` (conteúdo correto; POC antigo dizia BS-145, ERRADO) |

Conclusão: cada ferramenta é boa em tipos diferentes de pergunta (factual vs
conteúdo). Nenhuma sozinha acerta Q2 (tabela) nem Q4 (regional sem número no
docling). Relevância por termos (presença no arquivo inteiro) pega arquivos com
termos espalhados — precisa de densidade/proximidade, não só presença.

## Workflow do usuário (importante)
Para mudanças em scripts do OPS: **um script por vez, interativo, com
confirmação** antes de aplicar. O usuário prefere decisões de desenho
explicitadas e aprovadas (via `clarify`) do que implementação silenciosa.

## Relação com a pendência #42
O usuário DESISTIU da pesquisa via `atos.db`/catálogo SQL. `catalogar_atos.py`,
`exportar_atos_formatos.py`, `indexar_boletins_prt14.py` e os dados
(`atos.db`, `curadoria_atos.json`, CSV antigo) estão na fila de remoção. O
`atos_normativos.csv` CONTINUA sendo usado, mas agora regenerado do docling.
