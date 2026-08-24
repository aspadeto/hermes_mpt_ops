# Estratégia de Boletins no KB — Papéis e Consolidação

> Decisão #35 (23/08/2026): manter 3 pastas por ora e documentar papéis. A
> migração para docling é evolutiva; scripts legados só são alterados após
> confirmação do usuário.

## Pastas e papéis

| Pasta | Conteúdo | Papel |
|-------|----------|-------|
| `raw/boletins/` | 512 PDFs originais | fonte imutável, **nunca editar** |
| `boletins_docling/` | 512 `.md` estruturados (docling) | representação pesquisável de referência |
| `boletins/` | 512 `.md` planos (legado) | legado em desuso; só remover após migrar todos os consumidores |

## Regras

- **Corpus canônico para busca/extração:** `boletins_docling/`.
- **Regenerar índices/CSVs:** sempre a partir de `boletins_docling/`, nunca de `boletins/`.
- **Remoção de `boletins/`:** só após migrar todos os scripts que ainda leem essa pasta + validação do benchmark.
- **Novo script de pesquisa:** começar apontando para docling; scripts legados só são alterados um por um, com confirmação.

## Histórico

- 21/08/2026: conversão docling concluída (512/512, 0 erros).
- 23/08/2026: decisão #35 documentada; CSV `atos_normativos.csv` regenerado do docling (11.856 atos).
