#!/usr/bin/env python3
"""
pesquisar_boletins.py — Busca FULL-TEXT no conjunto de boletins ANTIGO (MD plano).

Este script busca por CONTEÚDO/ementa/nome próprio nos MDs PLANOS de
hermes_mpt_kb/boletins/ (formato legado, com frontmatter `data:`).

> NOTA (23/08/2026): antes era híbrido (índice CSV + full-text). Foi reduzido a
> FULL-TEXT APENAS sobre o conjunto antigo, para servir como ferramenta de
> benchmark. O índice factual (CSV docling) vive em pesquisar_boletins_csv.py;
> o full-text do corpus docling vive em pesquisar_boletins_fulltext.py.

Uso:
    python3 pesquisar_boletins.py "pergunta"
    python3 pesquisar_boletins.py --arquivo perguntas.txt
    python3 pesquisar_boletins.py --formato json "sobre o que versa..."
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

# ------------------------------------------------------------
# Configuração
# ------------------------------------------------------------
DIR_MDS = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/boletins")

_INDICE_MD_CACHE = None  # indice invertido: numero -> [ {arquivo, cabecalho, ementa, trecho, ano} ]


def get_indice_md():
    """Indice invertido dos cabecalhos de ato nos MDs planos (cacheado em disco)."""
    global _INDICE_MD_CACHE
    if _INDICE_MD_CACHE is not None:
        return _INDICE_MD_CACHE

    cab_pat = re.compile(
        r"([A-ZÇÃÊÓÍÀ-Ú ]+?)?\s*N[º°]\s*(\d+(?:\.\d+)?)\s*,\s*DE\s+\d{1,2}\s+DE\s+"
        r"[A-ZÇÃÊÓÍÀ-Ú]+\s+DE\s+(\d{4})", re.IGNORECASE)
    _INDICE_MD_CACHE = {}
    for arq in DIR_MDS.glob("*.md"):
        try:
            txt = arq.read_text(encoding="utf-8")
        except Exception:
            continue
        fm = parse_frontmatter(arq)
        for m in cab_pat.finditer(txt):
            num = m.group(2)
            ano = m.group(3)
            cab = m.group(0).strip()
            ini = m.end()
            trecho = txt[ini:ini + 600]
            ementa = re.sub(r"(<!-- pag \d+ -->|PROCURADORIA|BSE \d+/\d+|CIRCULAÇÃO:\s*[\d/]+|\d+)", "", trecho)
            ementa = re.sub(r"\s+", " ", ementa).strip()[:220]
            _INDICE_MD_CACHE.setdefault(num, []).append({
                "arquivo": arq.name,
                "boletim_data": fm.get("data"),
                "numero": num,
                "ano": ano,
                "cabecalho": cab,
                "ementa": ementa,
                "trecho": trecho,
            })
    return _INDICE_MD_CACHE


# ------------------------------------------------------------
# Extração de entidades
# ------------------------------------------------------------
def extrair_entidades(pergunta: str) -> dict:
    ent = {}
    p = pergunta
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
    m = re.search(r"\bPRT[-]?(\d{1,2})[ªa]?\b|\bPRT\s*(\d{1,2})\b", p, re.IGNORECASE)
    if m:
        num = (m.group(1) or m.group(2) or "").replace("ª", "").replace("a", "")
        if num:
            ent["prt"] = num
    # nome proprio em MAIUSCULAS (>=5 chars) -> forte sinal de busca fulltext
    tipos = {"PORTARIA", "EDITAL", "RESOLUÇÃO", "DECISÃO", "DESPACHO", "AVISO",
             "OFÍCIO", "PARECER", "REQUERIMENTO", "ATA", "COMUNICADO", "RETIFICAÇÃO"}
    nomes = []
    for n in re.findall(r"\b[A-ZÀ-ÚÇ]{5,}(?:\s+[A-ZÀ-ÚÇ]{2,})*\b", p):
        if n not in tipos and not n.startswith("PRT"):
            nomes.append(n)
    ent["nomes"] = nomes
    ent["low"] = p.lower()
    return ent


# ------------------------------------------------------------
# Full-text nos MDs planos
# ------------------------------------------------------------
def buscar_no_md(ent: dict, pergunta: str) -> list:
    """Busca por nome proprio ou termos no indice invertido de MDs planos."""
    low = pergunta.lower()
    nomes = ent.get("nomes", [])
    idx = get_indice_md()
    res = []
    if nomes:
        for num, candidatos in idx.items():
            for c in candidatos:
                trecho_upper = (c["cabecalho"] + c["trecho"]).upper()
                if all(n.upper() in trecho_upper for n in nomes[:2]):
                    res.append({k: c[k] for k in ("arquivo", "boletim_data", "numero", "cabecalho", "ementa")})
                    break
    return res[:8]


def extrair_bloco_ato(txt: str, linhas_txt: list, linhas_hit: list, ent: dict) -> dict:
    """Dado um MD, extrai o cabecalho 'Nº X, DE DD DE MES DE AAAA' + ementa."""
    resultado = {"numero": None, "cabecalho": "", "ementa": ""}
    cab_pat = re.compile(
        r"([A-ZÇÃÊÓÍÀ-Ú ]+?)?\s*N[º°]\s*(\d+(?:\.\d+)?)\s*,\s*DE\s+\d{1,2}\s+DE\s+"
        r"[A-ZÇÃÊÓÍÀ-Ú]+\s+DE\s+(\d{4})", re.IGNORECASE)
    candidatos = []
    for m in cab_pat.finditer(txt):
        cab = m.group(0).strip()
        num = m.group(2)
        ini = m.end()
        trecho = txt[ini:ini + 400]
        relevante = any(
            (ent.get("numero") and num == ent["numero"]) or
            t.lower() in trecho.lower()
            for t in (ent.get("nomes", []) + ["PRT" + (ent.get("prt") or "99")])
        )
        if relevante or True:
            candidatos.append((m.start(), cab, num, trecho))
    if not candidatos:
        return resultado

    def peso(c):
        _, cab, num, trecho = c
        w = 0
        if ent.get("numero") and num == ent["numero"]:
            w += 1000
        if ent.get("prt") and (f"PRT{ent['prt']}" in (cab + trecho).upper() or f"{ent['prt']}ª" in (cab + trecho).upper()):
            w += 50
        if ent.get("nomes"):
            for n in ent["nomes"]:
                if n.lower() in trecho.lower() or n.lower() in cab.lower():
                    w += 40
        if ent.get("low") and "desfazimento" in ent["low"] and "desfazimento" in trecho.lower():
            w += 40
        return w
    candidatos.sort(key=peso, reverse=True)
    _, cab, num, trecho = candidatos[0]
    resultado["numero"] = num
    resultado["cabecalho"] = cab
    trecho_limpo = re.sub(r"(<!-- pag \d+ -->|PROCURADORIA|BSE \d+/\d+|CIRCULAÇÃO:\s*[\d/]+|\d+)", "", trecho)
    trecho_limpo = re.sub(r"\s+", " ", trecho_limpo).strip()
    resultado["ementa"] = trecho_limpo[:220]
    return resultado


def parse_frontmatter(md: Path) -> dict:
    try:
        txt = md.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---\n", txt, re.DOTALL)
        if not m:
            return {}
        fm = {}
        for linha in m.group(1).splitlines():
            if ":" in linha:
                k, _, v = linha.partition(":")
                fm[k.strip()] = v.strip().strip('"').strip("'")
        return fm
    except Exception:
        return {}


def achar_md_por_numero_regiao(ent: dict) -> dict | None:
    """Usa o indice invertido: procura ato com numero, ano e regional."""
    num = ent.get("numero")
    prt = ent.get("prt")
    ano = ent.get("ano")
    if not num:
        return None
    idx = get_indice_md()
    candidatos = idx.get(num, [])
    if ano:
        candidatos = [c for c in candidatos if c["ano"] == ano]
    if prt:
        def tem_regiao(c):
            return bool(re.search(rf"\b{prt}ª\b|\b{prt}a\b|PRT\s*{prt}\b",
                                  (c["cabecalho"] + c["trecho"]).upper()))
        candidatos = [c for c in candidatos if tem_regiao(c)]
    if not candidatos:
        return None
    c = candidatos[0]
    return {k: c[k] for k in ("arquivo", "boletim_data", "numero", "cabecalho", "ementa")}


# ------------------------------------------------------------
# Orquestracao (full-text apenas)
# ------------------------------------------------------------
def responder(pergunta: str) -> dict:
    ent = extrair_entidades(pergunta)
    low = pergunta.lower()

    hits_md = buscar_no_md(ent, pergunta)
    res = {"pergunta": pergunta, "modo": "fulltext_plano"}

    # P4: "sobre o que versa Portaria 26/2025 PRT18" -> fulltext direcionado
    if ent.get("numero") and (ent.get("prt") or ent.get("ano")):
        md = achar_md_por_numero_regiao(ent)
        if md:
            res["fulltext"] = md
            res["resposta"] = (f"Encontrado em {md['arquivo']}: Nº {md.get('numero') or '?'} — "
                               f"{md.get('ementa','')[:180]}")
            return res

    if hits_md:
        res["fulltext"] = hits_md[0]
        m = hits_md[0]
        res["resposta"] = (f"Encontrado em {m['arquivo']}: "
                           f"{m['cabecalho']} {m['ementa'][:120]}")
        return res

    res["resposta"] = "Nenhum resultado encontrado no full-text (boletins planos)."
    return res


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Busca full-text em boletins (MDs planos)")
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
            if r.get("fulltext"):
                f = r["fulltext"]
                print(f"  -> MD: {f['arquivo']} | Nº {f.get('numero','?')} | {f.get('ementa','')[:100]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
