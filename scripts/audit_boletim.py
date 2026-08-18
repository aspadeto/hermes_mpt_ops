#!/usr/bin/env python3
"""audit_boletim.py — Auditoria de extração de Boletins de Serviço do MPT.

Estrutura de um BS:
  1. Capa: "BOLETIM DE SERVIÇO ELETRÔNICO NNN/AAAA - DD/MM/AAAA"
  2. Expediente: lista de autoridades (PGT, VPGT, etc.)
  3. Seções por unidade (PROCURADORIA-GERAL, PROCURADORIAS REGIONAIS)
     Cada seção: cabeçalho + "ATOS DO/A [CARGO]" + atos individuais
  4. Atos: PORTARIA N° XXXX, DECISÃO N° XXXX.AAAA, LICENÇA-PRÊMIO, etc.
  5. Fecho

Uso:
    audit_boletim.py <BS.pdf>
    audit_boletim.py <BS.pdf> [--saida DIR]

Saída:
    auditoria_<BS>.md   — relatório de auditoria

Referência: audit_pgea.py. Adaptado para boletins em 18/08/2026.
"""
import fitz, re, sys
from pathlib import Path

WD = Path("/opt/data/hermes-data/hermes_mpt_ops/scripts").resolve()

# Regex para detectar seção/unidade organizacional
SECAO_RE = re.compile(
    r"^(PROCURADORIA[-\s]*(?:GERAL|REGIONA?I?S?)|"
    r"PROCURADORIA\s+(?:DO\s+)?TRABALHO\s+(?:NO\s+)?MUNIC[ÍI]PIO|"
    r"PTM\s|PRT[-\s]\d+[ªa]\s+REGI[ÃA]O|"
    r"CÂMARA\s+(?:DE\s+)?(?:COORDENAÇÃO|REVISÃO)|"
    r"CORREGEDORIA|OUVIDORIA|"
    r"DIRETORIA\s+(?:DE\s+)?(?:ADMINISTRAÇÃO|GESTÃO|DOCUMENTAÇÃO)|"
    r"SECRETARIA\s+(?:EXECUTIVA|GERAL)|"
    r"GABINETE|"
    r"COORDENADORIA)\b",
    re.IGNORECASE,
)

# Regex para títulos de atos
ATO_RE = re.compile(
    r"^(?P<tipo>PORTARIA|DECISÃO|LICENÇA[-\s]PR[ÊE]MIO|"
    r"ATO\s+(?:DO|DA)|DESPACHO|AVISO|EXTRATO|EDITAL|COMUNICADO|"
    r"RETIFICAÇÃO|ERRATA|RESOLUÇÃO|INSTRUÇÃO\s+NORMATIVA|"
    r"RECOMENDAÇÃO|NOTIFICAÇÃO|INTIMAÇÃO)\s*"
    r"(?:N[°ºª]\s*)?(?P<num>\d+(?:\.\d+)?(?:\.[A-Z])?)\s*(?:,?\s*DE\s+\d+)?",
    re.IGNORECASE,
)

# Regex para subtítulos de atos (ex: "PORTARIAS", "ATOS DO PROCURADOR-GERAL")
SUBATO_RE = re.compile(
    r"^(ATOS?\s+(?:DO|DA)\s+|PORTARIAS?|DESPACHOS?|LICENÇAS?[-\s]PR[ÊE]MIO|"
    r"DECISÕES?|AVISOS?|EXTRATOS?|EDITAIS?|RESOLUÇÕES?)",
    re.IGNORECASE,
)


def detectar_secao(linha):
    m = SECAO_RE.match(linha.strip())
    return m.group(1).strip().upper() if m else None


def detectar_ato(linha):
    m = ATO_RE.match(linha.strip())
    if m:
        tipo = m.group("tipo").strip()
        num = m.group("num")
        return f"{tipo} N° {num}"
    return None


def detectar_subato(linha):
    m = SUBATO_RE.match(linha.strip())
    return m.group(1).strip() if m else None


def camada1(doc):
    """Metadados + páginas vazias."""
    chars = {i + 1: len(doc[i].get_text().strip()) for i in range(doc.page_count)}
    vazias = [p for p, c in chars.items() if p > 1 and c < 50]
    meta = {}
    primeira = doc[0].get_text().strip()
    m = re.search(r"BOLETIM\s+DE\s+SERVIÇO\s+ELETR[OÔ]NICO\s+(\d+(?:\.\d+)?)/(\d{4})", primeira, re.I)
    if m:
        meta["bs_numero"] = m.group(1)
        meta["bs_ano"] = m.group(2)
    m = re.search(r"(\d{2}/\d{2}/\d{4})", primeira)
    if m:
        meta["bs_data"] = m.group(1)
    return meta, vazias, chars


def camada2(doc):
    """Extrai estrutura: seções, atos, sumário."""
    secoes, atos_atual, pags_sem = [], [], []
    pag_atual_secao = {}
    sumario_linhas = []
    expediente = []

    for i in range(doc.page_count):
        txt = doc[i].get_text().strip()
        if not txt:
            continue
        lines = txt.split('\n')
        if i == 0:
            continue

        # Expediente na página 1 (índice 0)
        if i == 1 and "PROCURADOR-GERAL" in txt:
            expediente = [l.strip() for l in lines if l.strip() and len(l.strip()) > 3][:15]

        # Detectar seção
        secao = None
        for linha in lines[:5]:
            s = detectar_secao(linha)
            if s:
                secao = s
                break

        # Detectar ato
        ato = None
        for linha in lines[:3]:
            a = detectar_ato(linha)
            if a:
                ato = a
                break

        subato = None
        if not ato:
            for linha in lines[:3]:
                s = detectar_subato(linha)
                if s:
                    subato = s
                    break

        if secao:
            if not secoes or secoes[-1]["nome"] != secao:
                secoes.append({"nome": secao, "pags": [], "atos": []})
            pag_atual_secao[i + 1] = secao

        if secoes:
            secoes[-1]["pags"].append(i + 1)

        if ato and secoes:
            if ato not in [a["nome"] for a in secoes[-1]["atos"]]:
                secoes[-1]["atos"].append({"nome": ato, "pag": i + 1})
            atos_atual.append((i + 1, ato))

    # Páginas sem seção (capa, expediente, fecho)
    pags_com_secao = set()
    for s in secoes:
        pags_com_secao.update(s["pags"])
    pags_sem = [p for p in range(1, doc.page_count + 1) if p not in pags_com_secao and p > 1]

    return secoes, expediente, pags_sem


def main():
    if len(sys.argv) < 2:
        print("Uso: audit_boletim.py <BS.pdf> [--saida DIR]")
        sys.exit(1)
    pdf = Path(sys.argv[1])
    if not pdf.exists():
        print(f"❌ Arquivo não encontrado: {pdf}"); sys.exit(1)
    outdir = Path(sys.argv[sys.argv.index("--saida") + 1]) if "--saida" in sys.argv else WD
    outdir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf)
    TOTAL = doc.page_count
    titulo = pdf.stem
    meta, vazias, chars = camada1(doc)
    secoes, expediente, pags_sem = camada2(doc)

    rel = [f"# 🔍 Auditoria — {titulo}\n"]
    rel.append("## 📊 Camada 1 — Pré-visão\n")
    rel.append(f"- **Arquivo:** {pdf.name}")
    rel.append(f"- **Páginas:** {TOTAL}")
    if meta.get("bs_numero"):
        rel.append(f"- **BS:** {meta.get('bs_numero')}/{meta.get('bs_ano')} · **Data:** {meta.get('bs_data')}")
    rel.append(f"- **Páginas vazias:** {len(vazias)} — {'✅' if not vazias else '⚠️ OCR?'}")

    rel.append("\n## 📑 Camada 2 — Estrutura\n")
    total_atos = sum(len(s["atos"]) for s in secoes)
    rel.append(f"- **Seções (unidades):** {len(secoes)}")
    rel.append(f"- **Atos identificados:** {total_atos}")
    rel.append(f"- **Páginas sem seção (expediente/fecho):** {len(pags_sem)}\n")

    for s in secoes:
        atos_str = ", ".join([a["nome"] for a in s["atos"]]) if s["atos"] else "(sem atos detectados)"
        rel.append(f"### {s['nome']}")
        rel.append(f"- Páginas: {s['pags'][0]}–{s['pags'][-1]}")
        rel.append(f"- Atos ({len(s['atos'])}): {atos_str}\n")

    if expediente:
        rel.append("### 👤 Expediente (autoridades)")
        for e in expediente[:10]:
            rel.append(f"- {e}")
        if len(expediente) > 10:
            rel.append(f"  ... mais {len(expediente) - 10}")

    # Estatísticas de atos
    print(f"✅ {len(secoes)} seções, {total_atos} atos, {len(vazias)} vazias")
    doc.close()

    out = outdir / f"auditoria_{pdf.stem}.md"
    out.write_text("\n".join(rel), encoding="utf-8")
    print(f"📄 Relatório: {out}")
    print(f"📋 Preview:\n" + "\n".join(rel))


if __name__ == "__main__":
    main()
