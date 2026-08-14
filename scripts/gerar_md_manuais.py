#!/usr/bin/env python3
"""Gera MDs manualmente para boletins .md ausentes (quando o auditor detecta 0 atos)."""
import fitz
from pathlib import Path

RAIZ = Path("/opt/data/hermes-data/boletins")


def gerar_md(pdf: Path):
    doc = fitz.open(pdf)
    md_l = [f"# {pdf.stem}\n"]
    for i in range(doc.page_count):
        txt = doc[i].get_text().strip()
        if txt:
            md_l.append(f"<!-- pág {i+1} -->\n{txt}")
    pdf.with_suffix(".md").write_text("\n\n".join(md_l), encoding="utf-8")
    print(f"OK {pdf.stem}: {doc.page_count} págs")


def main():
    alvos = list(RAIZ.glob("2024-12-*/*.pdf")) + list(RAIZ.glob("2025-0[1-5]-*/*.pdf"))
    faltantes = []
    for pdf in alvos:
        md = pdf.with_suffix(".md")
        if not md.exists():
            faltantes.append(pdf)
    for pdf in faltantes:
        gerar_md(pdf)
    print(f"Total MDs gerados manualmente: {len(faltantes)}")


if __name__ == "__main__":
    main()
