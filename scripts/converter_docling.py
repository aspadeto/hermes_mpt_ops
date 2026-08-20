#!/usr/bin/env python3
"""
converter_docling.py — Converte PDFs de boletins com Docling para markdown estruturado.

Usa o Docling (IBM) para extrair a ESTRUTURA em árvore dos PDFs (headings,
seções, tabelas, ordem de leitura) — diferentemente do PyMuPDF que achata.

Saída por boletim (em hermes_mpt_kb/boletins_docling/):
    <nome>.md → markdown estruturado (export_to_markdown)

Com paralelismo (multiprocessing) e opção de gerar também JSON (árvore).

Uso:
    python3 converter_docling.py [--pdf BS-012-2025.pdf ...]
    python3 converter_docling.py --todos         # todos os PDFs de raw/boletins
    python3 converter_docling.py --todos --json  # inclui JSON lossless
    python3 converter_docling.py --todos --jobs 4  # paralelismo
"""

import argparse
import json
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

# Import lazy (dentro do worker) para multiprocessing
RAIZ_PDF = Path("/opt/data/hermes-data/hermes_mpt_kb/raw/boletins")
DEST_DEFAULT = Path("/opt/data/hermes-data/hermes_mpt_kb/boletins_docling")


def converter_um(pdf_path_str: str, dest_str: str, gerar_json: bool) -> tuple:
    """Converte um PDF com Docling (worker de multiprocessing). Retorna (nome, tempo, erro)."""
    import docling  # noqa
    from docling.document_converter import DocumentConverter

    pdf_path = Path(pdf_path_str)
    dest = Path(dest_str)
    dest.mkdir(parents=True, exist_ok=True)
    nome = pdf_path.stem
    t0 = time.time()
    try:
        converter = DocumentConverter()
        result = converter.convert(str(pdf_path))
        doc = result.document
        dt = time.time() - t0
        # Markdown estruturado
        md = doc.export_to_markdown()
        (dest / f"{nome}.md").write_text(md, encoding="utf-8")
        # JSON (opcional)
        if gerar_json:
            (dest / f"{nome}.json").write_text(
                json.dumps(doc.export_to_dict(), ensure_ascii=False), encoding="utf-8")
        return nome, dt, None
    except Exception as e:
        return nome, time.time() - t0, str(e)


def main():
    ap = argparse.ArgumentParser(description="Converte boletins PDF com Docling para MD estruturado")
    ap.add_argument("--pdf", nargs="+", help="Nomes dos PDFs a converter")
    ap.add_argument("--todos", action="store_true", help="Converte todos os PDFs de raw/boletins")
    ap.add_argument("--json", action="store_true", help="Também gera JSON lossless (árvore)")
    ap.add_argument("--dest", default=str(DEST_DEFAULT), help="Pasta de saída")
    ap.add_argument("--jobs", type=int, default=1, help="Nº de processos paralelos (default: 1)")
    args = ap.parse_args()

    if args.todos:
        pdfs = sorted(RAIZ_PDF.glob("*.pdf"))
    elif args.pdf:
        pdfs = [RAIZ_PDF / p for p in args.pdf]
    else:
        pdfs = [RAIZ_PDF / p for p in
                ["BS-012-2025.pdf", "BS-144-2025.pdf", "BS-050-2025.pdf", "BS-145-2026.pdf"]]

    pdfs = [p for p in pdfs if p.exists()]
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    print(f"Convertendo {len(pdfs)} PDFs com Docling → {dest}")
    print(f"  jobs={args.jobs} | gerar_json={args.json}")

    t_ini = time.time()
    resultados = []

    if args.jobs > 1:
        # paralelo
        pool = mp.Pool(args.jobs)
        args_lista = [(str(p), str(dest), args.json) for p in pdfs]
        resultados = pool.starmap(converter_um, args_lista)
        pool.close()
        pool.join()
    else:
        # sequencial
        for p in pdfs:
            resultados.append(converter_um(str(p), str(dest), args.json))

    t_total = time.time() - t_ini

    ok = 0
    erros = []
    for nome, dt, err in resultados:
        if err:
            erros.append((nome, err))
        else:
            ok += 1
        print(f"  {'✅' if not err else '❌'} {nome}: {dt:.1f}s" + (f" | ERRO: {err[:80]}" if err else ""))

    print(f"\n✅ {ok}/{len(pdfs)} convertidos em {t_total:.1f}s ({t_total/60:.1f} min) → {dest}")
    if erros:
        print(f"❌ {len(erros)} erros:")
        for nome, err in erros[:10]:
            print(f"   {nome}: {err}")
    return 1 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
