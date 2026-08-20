#!/usr/bin/env python3
"""
converter_docling.py — Converte PDFs de boletins com Docling para o PoC.

Usa o Docling (IBM) para extrair a ESTRUTURA em árvore dos PDFs (headings,
seções, tabelas, ordem de leitura) — diferentemente do PyMuPDF que achata.

Saída por boletim (em _poc_docling/):
    <nome>.md        → markdown estruturado (export_to_markdown)
    <nome>.json      → DoclingDocument (lossless JSON, árvore completa)
    <nome>.text.txt  → texto simples (para debug)

Uso:
    python3 converter_docling.py [--pdf BS-012-2025.pdf BS-144-2025.pdf ...]
    python3 converter_docling.py --todos   # converte todos os PDFs de raw/boletins
"""

import argparse
import json
import sys
import time
from pathlib import Path

from docling.document_converter import DocumentConverter

RAIZ_PDF = Path("/opt/data/hermes-data/hermes_mpt_kb/raw/boletins")
DEST = Path("/opt/data/hermes-data/_poc_docling")


def converter(pdf_path: Path, dest: Path):
    """Converte um PDF com Docling e salva md/json/text."""
    dest.mkdir(parents=True, exist_ok=True)
    nome = pdf_path.stem

    t0 = time.time()
    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))
    doc = result.document
    dt = time.time() - t0

    # Markdown estruturado
    md = doc.export_to_markdown()
    (dest / f"{nome}.md").write_text(md, encoding="utf-8")

    # JSON lossless (árvore completa)
    (dest / f"{nome}.json").write_text(
        json.dumps(doc.export_to_dict(), ensure_ascii=False), encoding="utf-8")

    # Texto simples
    (dest / f"{nome}.text.txt").write_text(doc.export_to_text(), encoding="utf-8")

    print(f"  ✅ {nome}: {dt:.1f}s | md={len(md)} chars")
    return nome, dt


def main():
    ap = argparse.ArgumentParser(description="Converte boletins PDF com Docling")
    ap.add_argument("--pdf", nargs="+", help="Nomes dos PDFs a converter")
    ap.add_argument("--todos", action="store_true", help="Converte todos os PDFs")
    args = ap.parse_args()

    if args.todos:
        pdfs = sorted(RAIZ_PDF.glob("*.pdf"))
    elif args.pdf:
        pdfs = [RAIZ_PDF / p for p in args.pdf]
    else:
        # default: os 4 boletins relevantes da PoC
        pdfs = [RAIZ_PDF / p for p in
                ["BS-012-2025.pdf", "BS-144-2025.pdf", "BS-050-2025.pdf", "BS-145-2026.pdf"]]

    # garantir que existem
    pdfs = [p for p in pdfs if p.exists()]
    print(f"Convertendo {len(pdfs)} PDFs com Docling → {DEST}")
    total = 0
    for p in pdfs:
        nome, dt = converter(p, DEST)
        total += dt
    print(f"\n✅ {len(pdfs)} convertidos em {total:.1f}s → {DEST}")


if __name__ == "__main__":
    sys.exit(main())
