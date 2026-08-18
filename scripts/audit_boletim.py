#!/usr/bin/env python3
"""audit_boletim.py — Auditoria de Boletins de Serviço do MPT.

Uso:
    audit_boletim.py <BS.pdf> [--saida DIR]
    audit_boletim.py <BS.pdf> --json   (saída JSON compacta)

Saída:
    auditoria_<BS>.md — relatório markdown

Estrutura do BS:
  Pág 1: Capa (título, data)
  Pág 2: Expediente (autoridades)
  Págs 3+: Seções PROCURADORIA-GERAL / PROCURADORIAS REGIONAIS
  Dentro de cada seção: subseções e atos (PORTARIA, DECISÃO, LICENÇA)
  Última pág: Fecho
"""
import pymupdf, re, sys, json
from pathlib import Path

SECAO_RE = re.compile(r"^(PROCURADORIA[- ]GERAL|PROCURADORIAS?\s+REGIONAIS?\s*)", re.I)

def analisar(pdf_path):
    doc = pymupdf.open(pdf_path)
    TOTAL = doc.page_count
    capa = doc[0].get_text().strip()

    meta = {"paginas": TOTAL, "vazias": 0, "secoes": [], "total_atos": 0}
    m = re.search(r"BOLETIM\s+DE\s+SERVIÇO\s+ELETR[OÔ]NICO\s+(\d+(?:\.\d+)?)/(\d{4})", capa, re.I)
    if m: meta["bs"] = f"{m.group(1)}/{m.group(2)}"
    m = re.search(r"(\d{2}/\d{2}/\d{4})", capa)
    if m: meta["data"] = m.group(1)

    secoes = []
    atual = None
    for i in range(1, TOTAL):
        txt = doc[i].get_text().strip()
        if not txt: continue
        if len(txt) < 50: meta["vazias"] += 1

        lines = [l.strip() for l in txt.split('\n') if l.strip()]
        if not lines: continue

        secao = None
        for l in lines[:2]:
            m = SECAO_RE.match(l)
            if m: secao = m.group(1).strip().upper(); break

        if secao != atual:
            if atual is not None:
                secoes[-1]["fim"] = i
            secoes.append({"nome": secao or "?","inicio": i+1, "fim": i+1, "subsecoes": [], "atos": 0})
            atual = secao

        # Detectar subseção / categoria de ato
        for l in lines[:3]:
            ml = re.match(r"^(ATOS?\s+(?:DO|DA)|PORTARIAS?|LICENÇA[- ]PR[ÊE]MIO|DESPACHOS?|DECISÃO)", l, re.I)
            if ml:
                nome = ml.group(1).strip()
                if not secoes[-1]["subsecoes"] or secoes[-1]["subsecoes"][-1]["nome"] != nome:
                    secoes[-1]["subsecoes"].append({"nome": nome, "inicio": i+1, "atos": 0})

        # Contar linhas que parecem conter atos (começam com N°, Art., número, etc.)
        if re.match(r"^(N[°º]\s*\d+|Art\.|\d+[°º])", lines[0], re.I):
            secoes[-1]["atos"] += 1
            if secoes[-1]["subsecoes"]:
                secoes[-1]["subsecoes"][-1]["atos"] += 1

    if secoes:
        secoes[-1]["fim"] = TOTAL

    doc.close()
    meta["secoes"] = secoes
    meta["total_atos"] = sum(s["atos"] for s in secoes)
    return meta


def main():
    if len(sys.argv) < 2:
        print("Uso: audit_boletim.py <BS.pdf> [--saida DIR] [--json]"); sys.exit(1)
    pdf = Path(sys.argv[1])
    if not pdf.exists(): print(f"❌ Não encontrado: {pdf}"); sys.exit(1)
    outdir = Path.cwd()
    saida_json = False
    for a in sys.argv[1:]:
        if a.startswith("--saida"):
            idx = sys.argv.index(a)
            if idx + 1 < len(sys.argv):
                outdir = Path(sys.argv[idx + 1])
        elif a == "--json": saida_json = True

    meta = analisar(pdf)
    if saida_json:
        print(json.dumps(meta, indent=2, ensure_ascii=False))
        return

    outdir.mkdir(parents=True, exist_ok=True)
    rel = [f"# 🔍 Auditoria — {pdf.stem}\n"]
    rel.append("## 📊 Camada 1 — Visão Geral\n")
    rel.append(f"- **Arquivo:** {pdf.name}  \n- **Páginas:** {meta['paginas']}")
    if meta.get("bs"): rel.append(f"- **BS:** {meta['bs']} · **Data:** {meta.get('data','?')}")
    rel.append(f"- **Páginas vazias/escaneadas:** {meta['vazias']} {'✅' if meta['vazias']==0 else '⚠️'}")

    rel.append("\n## 📑 Camada 2 — Estrutura\n")
    rel.append(f"- **Seções:** {len(meta['secoes'])}  \n- **Atos detectados:** {meta['total_atos']}\n")
    for s in meta["secoes"]:
        sub_info = ""
        if s["subsecoes"]:
            cats = {}
            for sub in s["subsecoes"]:
                cats[sub["nome"]] = cats.get(sub["nome"], 0) + sub["atos"]
            sub_info = " · " + ", ".join(f"{k}: {v}" for k, v in cats.items())
        rel.append(f"### 🏢 {s['nome']} (págs {s['inicio']}–{s['fim']}, {s['atos']} atos){sub_info}")

    print(f"✅ {pdf.name}: {meta['paginas']} págs, {len(meta['secoes'])} seções, {meta['total_atos']} atos")
    out = outdir / f"auditoria_{pdf.stem}.md"
    out.write_text("\n".join(rel))
    for l in rel: print(l)


if __name__ == "__main__":
    main()
