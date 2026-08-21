# Exportação de atos_normativos em múltiplos formatos (benchmark)

## Contexto

Desenvolvido em ago/2026 para testar qual formato de arquivo (.md, .csv, .tsv, .toml) rende melhor performance em pesquisas via grep/ferramentas CLI sobre os 11.350 atos catalogados.

## Script

`hermes_mpt_ops/scripts/exportar_atos_formatos.py`

## Uso

```bash
cd /opt/data/hermes-data/hermes_mpt_ops
.venv-bol/bin/python scripts/exportar_atos_formatos.py \
  --raiz /opt/data/hermes-data/hermes_mpt_kb/boletins \
  --dest /opt/data/hermes-data/_tmp_benchmark_atos
```

## Fonte dos Dados

Lê os **MDs planos** de `hermes_mpt_kb/boletins/*.md` (508 arquivos, frontmatter com `data:` de circulação). Para cada MD:

1. Parseia o frontmatter YAML (simples, sem lib yaml)
2. Chama `catalogar_atos.atos_por_arquivo(md)` — **a mesma lógica do catálogo SQLite** — para detectar atos (PORTARIA, DECISÃO, RESOLUÇÃO, etc.)
2. Enriquece cada ato com:
   - `boletim_data` (do frontmatter `data:`)
   - `boletim_numero` (extraído do `title:` do frontmatter)
   - `data_ato` normalizada para `YYYY-MM-DD`
   - `relevante = 0` (default, aguardando curadoria)

## Formatos Gerados (4 arquivos, mesmos 11.350 registros)

| Arquivo | Tamanho | Estrutura |
|---------|---------|-----------|
| `atos_normativos.md` | 3,4 MB | Tabela Markdown (pipe-separated) |
| `atos_normativos.csv` | 3,1 MB | CSV (vírgula, aspas mínimas) |
| `atos_normativos.tsv` | 3,1 MB | TSV (tab, mesma lógica CSV) |
| `atos_normativos.toml` | 4,5 MB | `[[atos]]` array of tables |

## Colunas (11 campos)

```
boletim_data, boletim_numero, tipo, numero, ano,
orgao, data_ato, pagina, secao, ementa, relevante
```

## Validação

- **11.350 atos** detectados em 508 MDs
- CSV == TSV byte-a-byte
- TOML com 11.350 entradas `[[atos]]`
- MD: 11.350 linhas de tabela (excluindo cabeçalho/separador)

## Benchmark de Grep (metodologia)

Testar os 4 formatos com consultas representativas:

| Tipo de busca | Exemplo | Métrica |
|---------------|---------|---------|
| ID exato | `grep -F "2152"` | tempo, 1 registro esperado |
| Palavra-chave na ementa | `grep -i "PGEA"` | tempo, N registros |
| Tipo | `grep -w "PORTARIA"` | tempo, muitos registros |
| Coluna/órgão | `grep "PROCURADOR-GERAL"` | tempo, N registros |

### Métricas coletadas

- **Tempo**: `timeit` (N repetições, mediana)
- **Acertos**: precisão vs. ground-truth (consulta no SQLite como referência)
- **Recall**: % do ground-truth recuperado

## Script de Benchmark (a implementar)

```bash
#!/bin/bash
# benchmark_grep.sh
FORMATS=("md" "csv" "tsv" "toml")
QUERIES=("2152" "PGEA" "PORTARIA" "PROCURADOR-GERAL")

for fmt in "${FORMATS[@]}"; do
  for q in "${QUERIES[@]}"; do
    time -p grep -c "$q" atos_normativos.$fmt
  done
done
```

## Resultados Preliminares (a validar)

- **CSV/TSV**: mais rápidos para grep em colunas específicas (separador único)
- **MD**: mais lento (pipes escapados, linhas longas)
- **TOML**: mais lento (estrutura verbosa, array of tables)

## Próximos Passos

1. Implementar script de benchmark automatizado
2. Definir ground-truth (consultas SQL no `atos.db` como verdade)
3. Rodar 100 iterações por query/formato
4. Comparar latência (p50, p99) e acurácia
5. Decidir formato padrão para índices de busca