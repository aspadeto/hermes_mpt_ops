#!/usr/bin/env python3
"""
benchmark_boletins.py — Benchmark das ferramentas de pesquisa de boletins.

Roda as 5 perguntas validadoras (ground truth) em cada ferramenta de pesquisa
e avalia o acerto, gerando uma tabela consolidada.

Ferramentas (4):
  1. pesquisar_boletins_csv.py     — factual (índice CSV docling)
  2. pesquisar_boletins_fulltext.py— full-text no corpus docling
  3. pesquisar_boletins.py         — full-text no corpus antigo (MD plano)
  4. pesquisar_docling.py          — POC estruturado docling (referência)

Ground truth (5 perguntas) — validado 23/08/2026:
  Q1: Portaria 56/2025, estrutura organizacional PRT10 -> BS-012-2025
  Q2: Gratificação do Chefe de Gabinete (Portaria 56) -> CC-4
  Q3: Comissão SPARKS -> Portaria 1124/2025, BS-144-2025
  Q4: Portaria 26/2025 PRT18 -> Comissão inventário PTM Luziânia/GO, BS-050-2025
  Q5: ARIANNE 26º Ofício PRT10 -> BS-142-2026 (conteúdo; POC antigo dizia BS-145)

Uso:
    python3 benchmark_boletins.py [--formato texto|json] [--dest DIR]
"""

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path

OPS_SCRIPTS = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/scripts")
PYTHON = "/opt/data/hermes-data/.tool-venv/bin/python"

# ------------------------------------------------------------
# Ground truth — cada pergunta com os termos que devem aparecer na resposta
# ------------------------------------------------------------
QUESTIONS = [
    {
        "id": "Q1",
        "pergunta": "qual a portaria que altera a estrutura organizacional da PRT10",
        "expected": ["56", "012", "12/2025"],
        "boletim_esperado": "012",
        "label": "Portaria 56/2025 - estrutura PRT10",
    },
    {
        "id": "Q2",
        "pergunta": "qual a gratificação do Chefe de Gabinete da portaria de estrutura organizacional da PRT10",
        "expected": ["CC-4"],
        "boletim_esperado": "012",
        "label": "Gratificação Chefe de Gabinete = CC-4",
    },
    {
        "id": "Q3",
        "pergunta": "em qual boletim foi publicada a comissão SPARKS",
        "expected": ["1124", "144", "144/2025"],
        "boletim_esperado": "144",
        "label": "Comissão SPARKS - Portaria 1124/2025",
    },
    {
        "id": "Q4",
        "pergunta": "sobre o que versa a portaria 26 da PRT18",
        "expected": ["26", "050", "Luziânia"],
        "boletim_esperado": "050",
        "label": "Portaria 26/2025 PRT18 - inventário PTM Luziânia",
    },
    {
        "id": "Q5",
        "pergunta": "qual ato designa ARIANNE CASTRO DE ARAÚJO MIRANDA para o 26º Ofício da PRT10",
        "expected": ["ARIANNE", "142", "142/2026"],
        "boletim_esperado": "142",
        "label": "Designação ARIANNE - 26º Ofício PRT10",
    },
]

TOOLS = [
    {"nome": "csv_factual", "script": "pesquisar_boletins_csv.py"},
    {"nome": "fulltext_docling", "script": "pesquisar_boletins_fulltext.py"},
    {"nome": "fulltext_plano", "script": "pesquisar_boletins.py"},
    {"nome": "docling_poc", "script": "pesquisar_docling.py"},
]


def rodar_ferramenta(script: str, pergunta: str) -> dict:
    """Executa a ferramenta com a pergunta e retorna {ok, resposta, tempo_ms}."""
    t0 = time.time()
    try:
        r = subprocess.run(
            [PYTHON, str(OPS_SCRIPTS / script), pergunta, "--formato", "json"],
            capture_output=True, text=True, timeout=120,
            env={"OPS_PATH": str(OPS_SCRIPTS.parent), "PATH": "/usr/bin:/bin"},
        )
        tempo = round((time.time() - t0) * 1000, 1)
        saida = r.stdout.strip()
        if r.returncode != 0:
            return {"ok": False, "resposta": f"ERRO exit {r.returncode}: {r.stderr[:200]}", "tempo_ms": tempo}
        try:
            dados = json.loads(saida)
            if isinstance(dados, list) and dados:
                resp = dados[0].get("resposta", "")
                return {"ok": True, "resposta": resp, "tempo_ms": tempo, "raw": dados[0]}
        except json.JSONDecodeError:
            return {"ok": True, "resposta": saida[:300], "tempo_ms": tempo}
    except subprocess.TimeoutExpired:
        return {"ok": False, "resposta": "TIMEOUT (>120s)", "tempo_ms": round((time.time() - t0) * 1000, 1)}
    except Exception as e:
        return {"ok": False, "resposta": f"EXCEÇÃO: {e}", "tempo_ms": round((time.time() - t0) * 1000, 1)}


def avaliar(q: dict, resposta: str) -> tuple[bool, list[str]]:
    """Retorna (acerto, [termos_encontrados]). Avalia se a resposta contém os
    termos esperados do ground truth."""
    r_upper = resposta.upper()
    encontrados = []
    for termo in q["expected"]:
        if termo.upper() in r_upper:
            encontrados.append(termo)
    # acerto: pelo menos 1 termo-chave do boletim E (número ou conteúdo)
    acerto = bool(q["boletim_esperado"] in r_upper) and bool(encontrados)
    return acerto, encontrados


def main():
    ap = argparse.ArgumentParser(description="Benchmark das ferramentas de pesquisa de boletins")
    ap.add_argument("--formato", choices=["texto", "json"], default="texto")
    ap.add_argument("--dest", default=str(OPS_SCRIPTS.parent / "data" / "benchmark"))
    args = ap.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    resultados = []  # [ {ferramenta, pergunta, acerto, resposta, tempo_ms} ]
    for tool in TOOLS:
        for q in QUESTIONS:
            r = rodar_ferramenta(tool["script"], q["pergunta"])
            acerto, encontrados = avaliar(q, r.get("resposta", ""))
            resultados.append({
                "ferramenta": tool["nome"],
                "pergunta": q["id"],
                "label": q["label"],
                "acerto": acerto,
                "resposta": r.get("resposta", ""),
                "tempo_ms": r.get("tempo_ms"),
                "erro": not r.get("ok", False),
            })
            print(f"  [{tool['nome']}] {q['id']}: {'✅' if acerto else '❌'} "
                  f"{r.get('tempo_ms')}ms | {r.get('resposta','')[:90]}")

    # Salvar JSON
    json_path = dest / "benchmark_resultado.json"
    json_path.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")

    # Tabela consolidada
    print("\n" + "=" * 60)
    print("BENCHMARK — ACERTO POR FERRAMENTA × PERGUNTA")
    print("=" * 60)
    cab = f"{'Ferramenta':<20}" + "".join(f"{q['id']:>5}" for q in QUESTIONS) + f"{'Total':>8}{'%':>6}"
    print(cab)
    print("-" * len(cab))
    totais_ferramenta = {}
    for tool in TOOLS:
        linha = f"{tool['nome']:<20}"
        total = 0
        for q in QUESTIONS:
            r = next(x for x in resultados if x["ferramenta"] == tool["nome"] and x["pergunta"] == q["id"])
            linha += f"{'✅' if r['acerto'] else '✗':>5}"
            total += 1 if r["acerto"] else 0
        totais_ferramenta[tool["nome"]] = total
        pct = round(total / len(QUESTIONS) * 100)
        linha += f"{total:>8}{pct:>5}%"
        print(linha)
    print("-" * len(cab))

    # Por pergunta (qual ferramenta acertou cada uma)
    print("\nACERTO POR PERGUNTA:")
    for q in QUESTIONS:
        acertaram = [x["ferramenta"] for x in resultados
                     if x["pergunta"] == q["id"] and x["acerto"]]
        print(f"  {q['id']} ({q['label']}): {', '.join(acertaram) if acertaram else 'NENHUMA'}")

    print(f"\n📄 Resultado salvo em: {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
