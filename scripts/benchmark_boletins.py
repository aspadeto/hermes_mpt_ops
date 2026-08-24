#!/usr/bin/env python3
"""
benchmark_boletins.py — Benchmark das ferramentas de pesquisa de boletins.

Roda as perguntas validadoras em cada ferramenta de pesquisa e avalia o acerto,
gerando uma tabela consolidada.

Ferramentas (4):
  1. pesquisar_boletins_csv.py      — factual (índice CSV docling)
  2. pesquisar_boletins_fulltext.py — full-text no corpus docling
  3. pesquisar_boletins.py          — full-text no corpus antigo (MD plano)
  4. pesquisar_docling.py           — POC estruturado docling (referência)

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
# 10 perguntas: 5 factuais + 5 conteúdo
# ------------------------------------------------------------
QUESTIONS = [
    # ---- FACTUAIS (5) ----
    {
        "id": "F1", "tipo": "factual",
        "pergunta": "qual a portaria que altera a estrutura organizacional da PRT10",
        "expected": ["56", "012", "12/2025"],
        "boletim_esperado": "012",
        "label": "Portaria 56/2025 - estrutura PRT10",
    },
    {
        "id": "F2", "tipo": "factual",
        "pergunta": "em qual boletim foi publicada a comissão SPARKS",
        "expected": ["1124", "144", "144/2025"],
        "boletim_esperado": "144",
        "label": "Comissão SPARKS - Portaria 1124/2025",
    },
    {
        "id": "F3", "tipo": "factual",
        "pergunta": "qual ato designa ARIANNE CASTRO DE ARAÚJO MIRANDA para o 26º Ofício da PRT10",
        "expected": ["ARIANNE", "142", "142/2026"],
        "boletim_esperado": "142",
        "label": "Designação ARIANNE - 26º Ofício PRT10",
    },
    {
        "id": "F4", "tipo": "factual",
        "pergunta": "qual a portaria que dispensa a servidora Ana Paula Alves Dubieux",
        "expected": ["332", "001/2026"],
        "boletim_esperado": "001",
        "label": "Portaria 332/2025 - dispensa Ana Paula",
    },
    {
        "id": "F5", "tipo": "factual",
        "pergunta": "qual a portaria 1 do boletim 002/2026 da PRT1",
        "expected": ["1", "002/2026"],
        "boletim_esperado": "002",
        "label": "Portaria 1/2026 PRT1 - BS-002",
    },
    # ---- CONTEÚDO (5) ----
    {
        "id": "C1", "tipo": "conteudo",
        "pergunta": "qual a gratificação do Chefe de Gabinete da portaria de estrutura organizacional da PRT10",
        "expected": ["CC-4", "CHEFE DE GABINETE"],
        "boletim_esperado": "012",
        "label": "Gratificação Chefe de Gabinete = CC-4",
    },
    {
        "id": "C2", "tipo": "conteudo",
        "pergunta": "sobre o que versa a portaria 26 da PRT18",
        "expected": ["Luziânia", "inventariar", "regularizar"],
        "boletim_esperado": "050",
        "label": "Portaria 26/2025 PRT18 - inventário PTM Luziânia",
    },
    {
        "id": "C3", "tipo": "conteudo",
        "pergunta": "qual portaria anula a portaria 1564.2025 do PGEA 20.02.0001",
        "expected": ["2152", "1564", "ANULAR"],
        "boletim_esperado": "001",
        "label": "Portaria 2152 anula 1564 (PGEA 20.02.0001)",
    },
    {
        "id": "C4", "tipo": "conteudo",
        "pergunta": "sobre o que versa a portaria 332 de 30 de dezembro de 2025",
        "expected": ["332", "Dispensar", "Ana Paula"],
        "boletim_esperado": "001",
        "label": "Portaria 332 - dispensa Ana Paula",
    },
    {
        "id": "C5", "tipo": "conteudo",
        "pergunta": "qual portaria designa Daniel Gemignani para o 58º Ofício",
        "expected": ["13", "Daniel", "58"],
        "boletim_esperado": "004",
        "label": "Portaria 13 - designa Daniel 58º Ofício",
    },
]

TOOLS = [
    {"nome": "csv_factual",     "script": "pesquisar_boletins_csv.py"},
    {"nome": "fulltext_docling","script": "pesquisar_boletins_fulltext.py"},
    {"nome": "fulltext_plano",  "script": "pesquisar_boletins.py"},
    {"nome": "docling_poc",     "script": "pesquisar_docling.py"},
]


def rodar_ferramenta(script: str, pergunta: str) -> dict:
    t0 = time.time()
    try:
        r = subprocess.run(
            [PYTHON, str(OPS_SCRIPTS / script), pergunta, "--formato", "json"],
            capture_output=True, text=True, timeout=180,
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
        return {"ok": False, "resposta": "TIMEOUT (>180s)", "tempo_ms": round((time.time() - t0) * 1000, 1)}
    except Exception as e:
        return {"ok": False, "resposta": f"EXCEÇÃO: {e}", "tempo_ms": round((time.time() - t0) * 1000, 1)}


def avaliar(q: dict, resposta: str) -> tuple[bool, list[str]]:
    r_upper = resposta.upper()
    encontrados = [t for t in q["expected"] if t.upper() in r_upper]
    acerto = bool(q["boletim_esperado"] in r_upper) and bool(encontrados)
    return acerto, encontrados


def main():
    ap = argparse.ArgumentParser(description="Benchmark das ferramentas de pesquisa de boletins")
    ap.add_argument("--formato", choices=["texto", "json"], default="texto")
    ap.add_argument("--dest", default=str(OPS_SCRIPTS.parent / "data" / "benchmark"))
    args = ap.parse_args()

    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    resultados = []
    for tool in TOOLS:
        for q in QUESTIONS:
            r = rodar_ferramenta(tool["script"], q["pergunta"])
            acerto, encontrados = avaliar(q, r.get("resposta", ""))
            resultados.append({
                "ferramenta": tool["nome"],
                "pergunta": q["id"],
                "tipo": q["tipo"],
                "label": q["label"],
                "acerto": acerto,
                "resposta": r.get("resposta", ""),
                "tempo_ms": r.get("tempo_ms"),
                "erro": not r.get("ok", False),
            })
            print(f"  [{tool['nome']}] {q['id']}: {'✅' if acerto else '❌'} "
                  f"{r.get('tempo_ms')}ms | {r.get('resposta','')[:90]}")

    json_path = dest / "benchmark_resultado.json"
    json_path.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")

    # Tabela consolidada
    print("\n" + "=" * 70)
    print("BENCHMARK — ACERTO POR FERRAMENTA × PERGUNTA (10 perguntas)")
    print("=" * 70)
    cab = f"{'Ferramenta':<20}" + "".join(f"{q['id']:>5}" for q in QUESTIONS) + f"{'Total':>7}{'%':>6}"
    print(cab)
    print("-" * len(cab))
    for tool in TOOLS:
        linha = f"{tool['nome']:<20}"
        total = 0
        for q in QUESTIONS:
            r = next(x for x in resultados if x["ferramenta"] == tool["nome"] and x["pergunta"] == q["id"])
            linha += f"{'✅' if r['acerto'] else '✗':>5}"
            total += 1 if r["acerto"] else 0
        pct = round(total / len(QUESTIONS) * 100)
        linha += f"{total:>7}{pct:>5}%"
        print(linha)
    print("-" * len(cab))

    # Por tipo
    print("\nACERTO POR TIPO:")
    for tipo in ("factual", "conteudo"):
        qs = [q for q in QUESTIONS if q["tipo"] == tipo]
        print(f"\n  {tipo.upper()}:")
        for tool in TOOLS:
            acertos = sum(1 for q in qs for x in resultados
                          if x["ferramenta"] == tool["nome"] and x["pergunta"] == q["id"] and x["acerto"])
            pct = round(acertos / len(qs) * 100)
            print(f"    {tool['nome']:<20} {acertos}/{len(qs)} ({pct}%)")

    print(f"\n📄 Resultado salvo em: {json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
