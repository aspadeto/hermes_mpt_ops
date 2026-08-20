# Metodologia de Teste: 5 Perguntas + Ground Truth

## Contexto

Desenvolvido em ago/2026 para validar a qualidade da indexação dos atos normativos dos Boletins de Serviço do MPT. O usuário forneceu 5 perguntas com respostas esperadas (ground truth) e pediu para testar a recuperação nos 4 formatos exportados (.md, .csv, .tsv, .toml) até atingir 100% de acerto.

## Perguntas e Respostas Esperadas (Ground Truth)

| # | Pergunta | Resposta Esperada | Localização nos Dados |
|---|----------|-------------------|----------------------|
| 1 | Qual a portaria que altera a estrutura organizacional da PRT10 e em qual boletim? | **Nº 56, de 15/01/2025** — BS-012-2025 | BS-012-2025.md, L332 |
| 2 | Qual a gratificação do Chefe de Gabinete nessa portaria? | **CC-4** | BS-012-2025.md, L455-456 |
| 3 | No boletim de 05/08/2026, alterou-se o Regimento Interno de qual coordenadoria/regional? | Altera Portaria PRT7 nº 56/2025 (Regimento Interno da Coord. 2º Grau da PRT 7ª) | BS-078-2025.md (29/04/2025) — **nota: a resposta manual cita 05/08/2026, mas o trecho está em 29/04/2025** |
| 4 | O que trata a Portaria 10/2026 da PRT10? | "Designar servidores p/ gestores, fiscais adm. e fiscais técnicos" | **Nota: a portaria com esse conteúdo é Nº 10 de 28/01/2025 (BS-020-2025, PRT10). Em 2026, a Nº 10 é de 08/01/2026 e trata de Suprimento de Fundos.** |
| 5 | Qual ato designa ARIANNE CASTRO DE ARAÚJO MIRANDA para o 26º Ofício Geral da PRT10? | **Portaria PRT10 N° 240/2026, de 07/08/2026** (Art. 4°) | BS-145-2026.md, L692-693 |

## Inconsistências Detectadas

| Perg | Divergência | Decisão |
|------|-------------|---------|
| 3 | Pergunta cita 05/08/2026, mas trecho está em 29/04/2025 | Validar resposta pelo **conteúdo correto** (Opção A) |
| 4 | Pergunta cita 2026, mas portaria com esse conteúdo é 2025 | Validar resposta pelo **conteúdo correto** (Opção A) |

**Decisão do usuário**: Opção A — validar pelo **conteúdo correto** (a pergunta é apenas contexto).

## Metodologia de Teste

### 1. Preparar Ground Truth no Índice
- Carregar os 11.350 atos dos 4 formatos exportados
- Para cada pergunta, definir o **resultado esperado exato** (string/registro)

### 2. Executar Consultas nos 4 Formatos
Para cada formato (.md, .csv, .tsv, .toml) e cada pergunta:

```bash
# Exemplo: buscar portaria 56/2025
grep -i "56/2025" atos_normativos.csv
grep -i "56/2025" atos_normativos.tsv
grep -i "56/2025" atos_normativos.md
grep -i "56/2025" atos_normativos.toml
```

### 3. Métricas por Formato

| Métrica | Como medir |
|---------|------------|
| **Tempo** | `timeit` (100 iterações, mediana) |
| **Acerto (Precision)** | Resultado contém exatamente o ground truth? (S/N) |
| **Recall** | % do ground truth recuperado (0-100%) |
| **F1** | Harmônica de precision/recall |

### 4. Critério de Sucesso

**100% de acerto nas 5 perguntas** em todos os 4 formatos antes de considerar o índice "pronto para uso".

## Script de Teste Automatizado

```python
#!/usr/bin/env python3
# test_queries.py
import subprocess, time, csv, json
from pathlib import Path

FORMATS = ["md", "csv", "tsv", "toml"]
QUESTIONS = [
    {"id": 1, "query": "56/2025", "expected": "Nº 56, DE 15 DE JANEIRO DE 2025"},
    {"id": 2, "query": "Chefe de Gabinete", "expected": "CC-4"},
    {"id": 3, "query": "PRT7.*56/2025", "expected": "Altera a Portaria PRT7 nº 56/2025"},
    {"id": 4, "query": "gestores, fiscais administrativos", "expected": "Designar os servidores abaixo para exercerem os encargos de gestores, fiscais administrativos e fiscais técnicos"},
    {"id": 5, "query": "ARIANNE CASTRO.*240/2026", "expected": "PORTARIA PRT10 N° 240/2026"},
]

def run_query(fmt, query):
    if fmt == "toml":
        # TOML precisa de parsing, não grep simples
        import toml
        data = toml.load(f"atos_normativos.{fmt}")
        results = []
        for ato in data.get("atos", []):
            if query.lower() in str(ato).lower():
                results.append(ato)
        return results
    else:
        cmd = ["grep", "-i", query, f"atos_normativos.{fmt}"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.stdout.splitlines()

# Medir tempo + acerto
for fmt in ["md", "csv", "tsv", "toml"]:
    for q in QUESTIONS:
        start = time.perf_counter()
        results = run_query(fmt, q["query"])
        elapsed = time.perf_counter() - start
        hit = any(q["expected"].lower() in str(r).lower() for r in results)
        print(f"{fmt} | Q{q['id']} | {elapsed*1000:.1f}ms | {'✅' if hit else '❌'} | {len(results)} resultados")
```

## Resultados Esperados (a validar)

| Formato | Q1 | Q2 | Q3 | Q4 | Q5 | Tempo médio |
|---------|----|----|----|----|----|-------------|
| CSV     | ✅ | ✅ | ✅ | ✅ | ✅ | ~ms |
| TSV     | ✅ | ✅ | ✅ | ✅ | ✅ | ~ms |
| MD      | ✅ | ✅ | ✅ | ✅ | ✅ | ~ms |
| TOML    | ✅ | ✅ | ✅ | ✅ | ✅ | ~ms |

## Critério de Parada

Quando **todos os 4 formatos** atingirem **5/5 acertos** nas 5 perguntas → índice validado.

## Próximos Passos

1. Rodar script acima nos 4 formatos exportados em `/opt/data/hermes-data/_tmp_benchmark_atos/`
2. Se algum formato falhar → refinar regex/parser até 100%
3. Documentar tempo médio por formato
4. Decidir formato padrão para índices de busca futuros