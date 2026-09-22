# Pesquisa em boletins — PoC híbrida (ago/2026)

Estratégia de busca inteligente nos Boletins de Serviço do MPT usando **2 níveis**
de dados. Validada com 5 perguntas de referência (100% de acerto).

## Arquitetura

| Nível | Fonte | Tipo de pergunta | Exemplo |
|-------|-------|------------------|---------|
| **1 — Índice** | `_tmp_benchmark_atos/atos_normativos.csv` (11.350 atos) | Fatos diretos: número/ano/tipo/PRT | "Qual a portaria Nº X?" "Em qual boletim?" |
| **2 — Full-text** | MDs planos `hermes_mpt_kb/boletins/*.md` (508) | Contexto/ementa/conteúdo | "Sobre o que versa?" "Designa quem para onde?" |

## Por que 2 níveis?

O `catalogar_atos.py` **omite ou extrai errado** alguns atos — a Portaria 26/2025
PRT18 e a designação da ARIANNE (Port. PRT10 240/2026) **só existiam no MD**, não
no CSV. Logo, perguntas que pedem conteúdo/designação exigem full-text.

## Scripts

- Skill: `pesquisa-boletins-inteligente` (SKILL.md + script)
- Script versionado: `hermes_mpt_ops/scripts/pesquisar_boletins.py`
- Cache do índice invertido: `_tmp_benchmark_atos/_indice_md.json` (~25 MB)

## Pitfalls críticos

1. **Validar número + ANO + regional emissora no cabeçalho.**
   Padrão de ato: `Nº X, DE DD DE MÊS DE AAAA`. Sem validar os três, "Nº 26"
   casa com portarias de outros anos/regionais (falso positivo). A `achar_md_por_numero_regiao`
   deve filtrar por `numero` + `ano` (do cabeçalho) + regional (`{prt}ª`/`PRT {prt}`) no trecho.

2. **Cache em disco do índice invertido é essencial.**
   Construir o índice (varrer 508 MDs + regex) custa ~44s. Sem cache, cada
   consulta paga isso → 68s/pergunta. Com `_indice_md.json` em disco → 220ms.
   **O JSON é regenerável e NÃO deve ir ao git.**

3. **Não usar `rg` re-scan por pergunta.** Para full-text eficiente, construir
   o índice invertido (`numero -> [{arquivo, cabecalho, ementa, trecho, ano}]`)
   UMA vez e consultar em memória.

4. **Nome próprio em MAIÚSCULAS = sinal de full-text.** Ex.: "ARIANNE CASTRO..."
   Forte indicador de pergunta de designação/contexto. Excluir tipos de ato
   ("PORTARIA", "EDITAL"...) da detecção de nomes.

5. **Ementa da full-text pode vir truncada** (regex de limpeza remove números/
   cabeçalhos de página). O número do ato + boletim são o ground-truth confiável;
   a ementa extraída é auxiliar.

## As 5 perguntas de referência (ground-truth)

| # | Pergunta | Resposta | Nível |
|---|----------|----------|-------|
| 1 | Qual a portaria que altera a estrutura organizacional da PRT10? | Port. Nº 56/2025, BS-012-2025 | Índice |
| 2 | Qual a gratificação do Chefe de Gabinete (dessa portaria)? | CC-4 | Índice + full-text (tabela) |
| 3 | Em qual boletim foi publicada a comissão SPARKS? | Port. Nº 1124/2025, BS-144-2025 | Índice |
| 4 | Sobre o que versa a Portaria 26/2025 da PRT18? | Comissão de inventário/regularização PTM Luziânia/GO (BS-050-2025) | Full-text |
| 5 | Qual ato designa ARIANNE para o 26º Ofício da PRT10? | Port. PRT10 Nº 240/2026 (BS-145-2026) | Full-text |

**OBS P3:** a pergunta original dizia "05/08/2026" mas o ato SPARKS está no
BS-144-**2025** (05/08/2025). Validar sempre o dado real, não a data da pergunta.
