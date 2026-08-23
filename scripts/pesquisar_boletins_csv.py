#!/usr/bin/env python3
"""
pesquisar_boletins_csv.py — Busca FACTUAL em atos de boletins (nível 1: índice CSV).

Consulta o atos_normativos.csv (gerado do corpus DOCLING por exportar_atos_docling.py)
por fatos diretos: número, ano, tipo, órgão, boletim. Responde perguntas do tipo
"qual a portaria Nº X?", "em qual boletim foi publicada?", "qual órgão emitiu?".

Diferente do pesquisar_boletins_fulltext.py (que busca CONTEÚDO/ementa nos .md
docling), este é o nível factual/estruturado.

Uso:
    python3 pesquisar_boletins_csv.py "pergunta"
    python3 pesquisar_boletins_csv.py --arquivo perguntas.txt
    python3 pesquisar_boletins_csv.py --formato json "portaria 56/2025"
"""

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path

# Configuração de caminhos (via ops_paths, com fallback para caminho canônico)
try:
    from ops_paths import OPS_DATA
except ImportError:
    OPS_DATA = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/data")

ARQ_INDICE_CSV = OPS_DATA / "indices" / "atos_normativos.csv"

_CACHE = None


def carregar_indice():
    """Carrega o CSV docling (indexado em memória)."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not ARQ_INDICE_CSV.exists():
        print(f"ERRO: índice não encontrado em {ARQ_INDICE_CSV}", file=sys.stderr)
        return []
    with open(ARQ_INDICE_CSV, encoding="utf-8") as f:
        _CACHE = list(csv.DictReader(f))
    return _CACHE


# ------------------------------------------------------------
# Extração de entidades da pergunta
# ------------------------------------------------------------
def extrair_entidades(pergunta: str) -> dict:
    ent = {}
    p = pergunta
    # numero/ano explícito: "56/2025" ou "portaria 56/2025"
    m = re.search(r"\b(\d+(?:\.\d+)?)\s*/\s*(\d{4})\b", p)
    if m:
        ent["numero"], ent["ano"] = m.group(1), m.group(2)
    if "numero" not in ent:
        m = re.search(r"[Nn][º°]\s*(\d+(?:\.\d+)?)\b", p)
        if m:
            ent["numero"] = m.group(1)
    if "ano" not in ent:
        m = re.search(r"\b(20\d{2})\b", p)
        if m:
            ent["ano"] = m.group()
    # tipo de ato
    m = re.search(r"\b(portaria|portarias|edital|editais|resolução|resoluções|"
                  r"decisão|decisões|despacho|despachos|aviso|avisos|ofício|ofícios|"
                  r"parecer|pareceres|instrução normativa)\b", p, re.IGNORECASE)
    if m:
        ent["tipo"] = m.group(1).upper()
    # PRT / regional
    m = re.search(r"\bPRT[-]?(\d{1,2})[ªa]?\b|\bPRT\s*(\d{1,2})\b", p, re.IGNORECASE)
    if m:
        num = (m.group(1) or m.group(2) or "").replace("ª", "").replace("a", "")
        if num:
            ent["prt"] = num
    ent["low"] = p.lower()
    return ent


def buscar_no_indice(ent: dict, pergunta: str) -> list:
    indice = carregar_indice()
    if not indice:
        return []
    low = pergunta.lower()
    resultados = []
    for row in indice:
        score = 0
        num_r = (row.get("numero") or "").strip()
        ano_r = (row.get("ano") or "").strip()
        if ent.get("numero") and ent.get("ano"):
            if num_r == ent["numero"] and ano_r == ent["ano"]:
                score += 1000
            elif num_r == ent["numero"]:
                score += 600
            elif ano_r == ent["ano"]:
                score += 100
        elif ent.get("numero"):
            if num_r == ent["numero"]:
                score += 800
        if ent.get("tipo") and (row.get("tipo") or "").upper() == ent["tipo"]:
            score += 60
        orgao = (row.get("orgao") or "").upper()
        if ent.get("prt"):
            if re.search(rf"\b{ent['prt']}ª\b|\b{ent['prt']}a\b", orgao) or \
               f"PRT{ent['prt']}" in orgao.replace(" ", ""):
                score += 200
        ementa = (row.get("ementa") or "").lower()
        for kw in ["estrutura organizacional", "chefe de gabinete", "desfazimento",
                   "sparks", "inventariar", "bens patrimoniais", "arianne"]:
            if kw in low and kw in ementa:
                score += 50
        if "arianne" in low and "arianne" in ementa:
            score += 150
        if score > 0:
            row["_score"] = score
            resultados.append(row)
    resultados.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return resultados[:8]


def responder(pergunta: str) -> dict:
    ent = extrair_entidades(pergunta)
    hits = buscar_no_indice(ent, pergunta)
    res = {"pergunta": pergunta, "modo": "csv_factual"}

    if not hits:
        res["resposta"] = "Nenhum resultado encontrado no índice (CSV docling)."
        res["hits"] = []
        return res

    top = hits[0]
    res["resposta"] = (f"{top.get('tipo','')} Nº {top.get('numero','')}/{top.get('ano','')} "
                       f"- BS-{top.get('boletim_numero','')} ({top.get('boletim_data','')})")
    if top.get("orgao"):
        res["resposta"] += f" | {top.get('orgao','')}"
    res["hits"] = hits
    return res


def main():
    ap = argparse.ArgumentParser(description="Busca factual em atos de boletins (CSV docling)")
    ap.add_argument("pergunta", nargs="?", help="Pergunta")
    ap.add_argument("--arquivo", help="Arquivo com perguntas (uma por linha)")
    ap.add_argument("--formato", choices=["json", "texto"], default="texto")
    args = ap.parse_args()

    if args.arquivo:
        perguntas = [l.strip() for l in Path(args.arquivo).read_text(encoding="utf-8").splitlines() if l.strip()]
    elif args.pergunta:
        perguntas = [args.pergunta]
    else:
        ap.print_help()
        return 1

    resultados = []
    for p in perguntas:
        t0 = time.time()
        r = responder(p)
        r["tempo_ms"] = round((time.time() - t0) * 1000, 1)
        resultados.append(r)

    if args.formato == "json":
        print(json.dumps(resultados, ensure_ascii=False, indent=2))
    else:
        for r in resultados:
            print(f"\n{'='*60}")
            print(f"PERGUNTA: {r['pergunta']}")
            print(f"RESPOSTA: {r.get('resposta','N/A')}")
            print(f"TEMPO: {r.get('tempo_ms')}ms")
            if r.get("hits"):
                print("  TOP:")
                for h in r["hits"][:3]:
                    print(f"    - {h.get('tipo','')} Nº{h.get('numero','')}/{h.get('ano','')} "
                          f"| BS-{h.get('boletim_numero','')} | score {h.get('_score',0)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
