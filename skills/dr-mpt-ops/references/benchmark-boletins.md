# Benchmark das Ferramentas de Pesquisa de Boletins

> Decisão/estado em 23/08/2026. Usar como referência ao melhorar busca ou avaliar
> novas ferramentas. As 4 ferramentas cobrem factual + conteúdo em 2 corpora.

## Arquitetura das ferramentas (Fase 2, pendência #41)

| Script | Motor | Fonte | Tipo de pergunta ideal |
|--------|-------|-------|------------------------|
| `pesquisar_boletins_csv.py` | factual (índice) | `atos_normativos.csv` (docling) | número/ano/tipo/órgão/boletim |
| `pesquisar_boletins_fulltext.py` | full-text | `boletins_docling/*.md` | nome próprio + conteúdo estruturado |
| `pesquisar_boletins.py` | full-text | `boletins/*.md` plano (legado) | nome próprio + conteúdo legado |
| `pesquisar_docling.py` | POC estruturado | `boletins_docling/*.md` | perguntas hardcoded (referência) |

## 10 perguntas validadoras (5 factuais + 5 conteúdo)

**Factuais:**
- F1: qual a portaria que altera a estrutura organizacional da PRT10 → Portaria 56/2025, BS-012/2025
- F2: em qual boletim foi publicada a comissão SPARKS → Portaria 1124/2025, BS-144/2025
- F3: qual ato designa ARIANNE CASTRO DE ARAÚJO MIRANDA para o 26º Ofício da PRT10 → BS-142/2026
- F4: qual a portaria que dispensa a servidora Ana Paula Alves Dubieux → Portaria 332/2025, BS-001/2026
- F5: qual a portaria 1 do boletim 002/2026 da PRT1 → Portaria 1/2026, BS-002/2026

**Conteúdo:**
- C1: qual a gratificação do Chefe de Gabinete da portaria de estrutura organizacional da PRT10 → CC-4
- C2: sobre o que versa a portaria 26 da PRT18 → inventário PTM Luziânia/GO, BS-050/2025
- C3: qual portaria anula a portaria 1564.2025 do PGEA 20.02.0001 → Portaria 2152/2025, BS-001/2026
- C4: sobre o que versa a portaria 332 de 30 de dezembro de 2025 → dispensa Ana Paula
- C5: qual portaria designa Daniel Gemignani para o 58º Ofício → Portaria 13/2026, BS-004/2026

## Resultado baseline (23/08/2026)

csv_factual: 4/10 factuais ok, 0/5 conteúdo ok.
fulltext_docling: 2/5 factuais ok, 0/5 conteúdo ok.
fulltext_plano: 1/5 factuais ok, 0/5 conteúdo ok.
docling_poc: 3/5 factuais ok, 1/5 conteúdo ok.

## Limitações conhecidas

- csv_factual depende de parser docling que coloca ementa ANTES do heading Nº → tipo pode ficar genérico (ex: Portaria 56 sai como ATO).
- fulltext_docling/fulltext_plano não desambiguam por regional quando o mesmo número existe em várias seções do boletim.
- fulltext por termos pega arquivos com termos espalhados → baixa precisão sem densidade/proximidade.

## Como rodar o benchmark

```bash
cd /opt/data/hermes-data/mpt_workspace/hermes_mpt_ops
OPS_PATH=/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops \
  /opt/data/hermes-data/.tool-venv/bin/python scripts/benchmark_boletins.py
```

Saída JSON: `data/benchmark/benchmark_resultado.json`.
