#!/usr/bin/env python3
"""
pesquisar_boletins_fulltext.py — Busca por CONTEÚDO em boletins (nível 2: full-text docling).

Consulta os .md ESTRUTURADOS do Docling (hermes_mpt_kb/boletins_docling/) por
conteúdo/ementa/nome próprio. Responde perguntas do tipo "sobre o que versa",
"designa quem para onde", "qual ato menciona X".

Fonte: boletins_docling/*.md (canônico — decisão #35). O ano e o número do
boletim vêm do NOME do arquivo (BS-012-2025), pois o docling não tem frontmatter.

Diferente do pesquisar_boletins_csv.py (que busca fatos no atos_normativos.csv),
este busca o CONTEÚDO nos markdown docling.

Uso:
    python3 pesquisar_boletins_fulltext.py "pergunta"
    python3 pesquisar_boletins_fulltext.py --arquivo perguntas.txt
    python3 pesquisar_boletins_fulltext.py --formato json "sobre o que versa a portaria 26"
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

try:
    from ops_paths import KB_BOLETINS_DOCLING
except ImportError:
    KB_BOLETINS_DOCLING = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/boletins_docling")

_DIR_MDS = KB_BOLETINS_DOCLING
_CACHE = None  # índice invertido: numero -> [ {arquivo, boletim_data, numero, ano, cabecalho, ementa, trecho} ]

# Nomes de tipos de ato (para excluir da detecção de nome próprio)
TIPOS = {"PORTARIA", "EDITAL", "RESOLUÇÃO", "DECISÃO", "DESPACHO", "AVISO",
         "OFÍCIO", "PARECER", "REQUERIMENTO", "ATA", "COMUNICADO", "RETIFICAÇÃO"}


def _ano_boletim(md: Path) -> str:
    m = re.search(r"(\d{4})\.md$", md.name)
    return m.group(1) if m else ""


def _numero_boletim(md: Path) -> str:
    m = re.match(r"BS-(\d+(?:\.\d+)*)-(\d{4})", md.stem, re.IGNORECASE)
    return f"{m.group(1)}/{m.group(2)}" if m else md.stem


def get_indice_md():
    """Índice invertido dos cabeçalhos de ato nos .md docling (cacheado em memória).

    Regex aceita Nº/N° e heading '## Nº X, DE DD DE MÊS DE AAAA' ou linha solta.
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    cab_pat = re.compile(
        r"#{0,6}\s*N[º°]\s*(\d+(?:\.\d+)?[A-Za-z]?)\s*,?\s*DE\s+"
        r"(?:\d{1,2})[º°]?\s+DE\s+[A-ZÇÃÊÓÍÀ-Ú]+\s+DE\s+(\d{4})",
        re.IGNORECASE)
    _CACHE = {}
    for arq in _DIR_MDS.glob("BS-*.md"):
        try:
            txt = arq.read_text(encoding="utf-8")
        except Exception:
            continue
        ano = _ano_boletim(arq)
        for m in cab_pat.finditer(txt):
            num = m.group(1)
            ano_ato = m.group(2) or ano
            ini = m.end()
            trecho = txt[ini:ini + 600]
            ementa = re.sub(r"<!-- image -->|<!-- pág \d+ -->|\||PROCURADORIA|CIRCULAÇÃO:?\s*[\d/]+", "", trecho)
            ementa = re.sub(r"\s+", " ", ementa).strip()[:250]
            _CACHE.setdefault(num, []).append({
                "arquivo": arq.name,
                "boletim_data": "",  # docling sem frontmatter
                "numero": num,
                "ano": ano_ato,
                "cabecalho": m.group(0).strip(),
                "ementa": ementa,
                "trecho": trecho,
            })
    return _CACHE


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
    # nome próprio em MAIÚSCULAS (>=5 chars), excluindo tipos de ato
    nomes = []
    for n in re.findall(r"\b[A-ZÀ-ÚÇ]{5,}(?:\s+[A-ZÀ-ÚÇ]{2,})*\b", p):
        if n not in TIPOS and not n.startswith("PRT"):
            nomes.append(n)
    ent["nomes"] = nomes
    ent["low"] = p.lower()
    return ent


def buscar_no_md(ent: dict, pergunta: str) -> list:
    """Busca por nome próprio OU termos-chave no conteúdo dos .md docling.

    1) Nome próprio em MAIÚSCULAS → procurar nos trechos + arquivo inteiro.
    2) Termos-chave (sem stopwords) → varrer os arquivos docling e rankear
       os que contêm mais termos na proximidade.
    """
    low = pergunta.lower()
    nomes = ent.get("nomes", [])
    idx = get_indice_md()
    res = []

    # --- 1) nome próprio ---
    if nomes:
        for num, candidatos in idx.items():
            for c in candidatos:
                bloco = (c["cabecalho"] + c["trecho"]).upper()
                if all(n.upper() in bloco for n in nomes[:2]):
                    res.append({k: c[k] for k in ("arquivo", "boletim_data", "numero", "cabecalho", "ementa")})
                    break
        if not res:
            for arq in _DIR_MDS.glob("BS-*.md"):
                try:
                    txt = arq.read_text(encoding="utf-8")
                except Exception:
                    continue
                up = txt.upper()
                if all(n.upper() in up for n in nomes[:2]):
                    m = re.search(r"#{0,6}\s*N[º°]\s*(\d+(?:\.\d+)?)[^#]{0,400}", txt, re.DOTALL)
                    pos = up.find(nomes[0].upper())
                    res.append({
                        "arquivo": arq.name, "boletim_data": "",
                        "numero": m.group(1) if m else "?",
                        "cabecalho": m.group(0)[:120].strip() if m else "",
                        "ementa": re.sub(r"\s+", " ", txt[max(0,pos-200):pos+200]).strip()[:250],
                    })
                    break
        return res[:8]

    # --- 2) termos-chave do conteúdo ---
    termos = _termos_chave(low)
    if not termos:
        return []
    melhores = []
    for arq in _DIR_MDS.glob("BS-*.md"):
        try:
            txt = arq.read_text(encoding="utf-8")
        except Exception:
            continue
        tlow = txt.lower()
        score = sum(1 for t in termos if t in tlow)
        if score >= 2:  # precisa casar pelo menos 2 termos para ser relevante
            # acha o trecho com maior densidade
            pos = min(tlow.find(t) for t in termos if t in tlow)
            melhores.append({
                "arquivo": arq.name, "boletim_data": "",
                "numero": "?", "cabecalho": "",
                "ementa": re.sub(r"\s+", " ", txt[max(0,pos-150):pos+250]).strip()[:250],
                "_score": score,
            })
    melhores.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return melhores[:8]


_STOPWORDS = {
    "qual", "quais", "a", "o", "as", "os", "de", "do", "da", "dos", "das",
    "em", "para", "com", "por", "que", "e", "na", "no", "se", "um", "uma",
    "sobre", "versa", "portaria", "designa", "foi", "publicada", "publicado",
    "qual", "onde", "como", "ato", "atos", "não", "nesta", "deste", "foi",
}


def _termos_chave(low: str) -> list:
    """Extrai termos-chave da pergunta (remove stopwords) para busca full-text."""
    tokens = re.findall(r"[a-zà-ú]{4,}", low)
    termos = [t for t in tokens if t not in _STOPWORDS and not t.isdigit()]
    # remove duplicados preservando ordem
    vistos = set()
    unicos = []
    for t in termos:
        if t not in vistos:
            vistos.add(t)
            unicos.append(t)
    return unicos[:6]


def achar_md_por_numero_regiao(ent: dict) -> dict | None:
    """Procura ato com numero=ent.numero, ano=ent.ano e regional=ent.prt nos docling."""
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


def responder(pergunta: str) -> dict:
    ent = extrair_entidades(pergunta)
    low = pergunta.lower()
    res = {"pergunta": pergunta, "modo": "fulltext_docling"}

    # Pergunta de conteúdo/nome próprio → full-text
    hits = buscar_no_md(ent, pergunta)

    if ent.get("numero") and (ent.get("prt") or ent.get("ano")):
        md = achar_md_por_numero_regiao(ent)
        if md and not hits:
            res["fulltext"] = md
            res["resposta"] = (f"Encontrado em {md['arquivo']}: Nº {md.get('numero','?')} — "
                               f"{md.get('ementa','')[:150]}")
            return res

    if hits:
        res["fulltext"] = hits[0]
        h = hits[0]
        res["resposta"] = (f"Encontrado em {h['arquivo']}: Nº {h.get('numero','?')} — "
                           f"{h.get('ementa','')[:150]}")
        return res

    res["resposta"] = "Nenhum resultado encontrado no full-text docling."
    return res


def main():
    ap = argparse.ArgumentParser(description="Busca por conteúdo em boletins (full-text docling)")
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
    return 0


if __name__ == "__main__":
    sys.exit(main())
