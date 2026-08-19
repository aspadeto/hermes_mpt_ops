#!/usr/bin/env python3
"""extrair_md_boletins.py — Converte PDFs de boletins em Markdown plano (frontmatter + páginas).

Lê os PDFs de uma origem (default: hermes_mpt_kb/raw/boletins/) e gera, para cada
PDF, un arquivo .md PLANO no destino (default: hermes_mpt_kb/boletins/), replicando
o formato de boletín já usado na base:

    ---
    title: "BS 071-2025"
    data: 2025-04-14
    created: 2025-04-14
    updated: 2025-04-14
    type: boletim-servico
    tags: [boletim, mpt, 2025-04]
    ---

    # BS-071-2025

    > 16 paginas

    ## Capa

    <!-- pag 1 -->
    <texto página 1>
    <!-- pag 2 -->
    ...

Objetivo: padronizar o almacenamiento dos boletins MD na raíz de
hermes_mpt_kb/boletins/ (SEM subcarpetas por mês), de forma reproducible e
versionada (estrutura plana, un arquivo por boletín).

Uso:
    python3 extrair_md_boletins.py [--orig DIR] [--dest DIR] [--filtro GLOB]

Sem argumentos usa os defaults. --dest permite testear numa carpeta separada
(hoxe no real).
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("Erro: PyMuPDF não instalado. Use: uv venv .venv && uv pip install pymupdf")

# Época do MPT em Espanhol (nome do môdulo en português)
MESES = {
    "ENERO": "01", "FEVEREIRO": "02", "MARÇO": "03", "ABRIL": "04",
    "MAIO": "05", "JUNHO": "06", "JULHO": "07", "AGOSTO": "08",
    "SETEMBRO": "09", "OUTUBRO": "10", "NOVEMBRO": "11", "DEZEMBRO": "12",
}


def _fmt(ano: int, mes: str, dia: int) -> str:
    """Formata ano-mês-dia já com mes normalizado a 2 dígitos ('04')."""
    return f"{ano:04d}-{mes}-{dia:02d}"


def detectar_data(pagina: str) -> str | None:
    """Extrae a data do boletín (prioridade: CIRCULAÇÃO → cabeçalho DD de MÊS de AAAA).

    Retorna 'YYYY-MM-DD' ou None.
    """
    # 1) CIRCULAÇÃO: DD/MM/AAAA  (aparece nas páginas 2+)
    m = re.search(r"CIRCULA[CÓO]?[A-Z]*\s*:\s*(\d{1,2})/(\d{1,2})/(\d{4})", pagina, re.IGNORECASE)
    if m:
        dia, mes, ano = int(m.group(1)), m.group(2), int(m.group(3))
        if 1 <= int(mes) <= 12 and 1 <= dia <= 31:
            return _fmt(ano, mes.rjust(2, "0"), dia)

    # 2) cabeçalho capa: "... SEGUNDA-FEIRA, 14 DE ABRIL DE 2025" o "... 14/04/2025"
    m = re.search(r"(\d{1,2})\s+DE\s+([A-ZÇÃÊÓÍÀ-Ú]+)\s+DE\s+(\d{4})", pagina, re.IGNORECASE)
    if m:
        dia, mes_nome, ano = int(m.group(1)), m.group(2).upper(), int(m.group(3))
        mes = MESES.get(mes_nome)
        if mes and 1 <= dia <= 31:
            return _fmt(ano, mes, dia)

    m = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", pagina)
    if m:
        dia, mes, ano = int(m.group(1)), m.group(2), int(m.group(3))
        if 1 <= int(mes) <= 12 and 1 <= dia <= 31:
            return _fmt(ano, mes.rjust(2, "0"), dia)

    return None


def nome_bolet(pdf: Path) -> str:
    """Nome base do boletín sin extensión: 'BS-071-2025'."""
    return pdf.stem


def titulo_frontmatter(pdf: Path) -> str:
    """'BS-071-2025' → 'BS 071-2025' (formato do título já usado)."""
    return pdf.stem.replace("-", " ", 1)


def converter_pdf(pdf: Path) -> str:
    """Convierte un PDF de boletín a farkdown con frontmatter + <!-- pag N -->."""
    doc = fitz.open(pdf)
    total = len(doc)

    # Data de referência: de CIRCULAÇÃO na página 1, senão primera con fecha
    data_ref = None
    for i in range(min(total, 3)):
        data_ref = detectar_data(doc[i].get_text())
        if data_ref:
            break
    doc.close()

    # Abre de novo p/ re-leer (melora do que guardar doc)
    doc = fitz.open(pdf)
    data_boletim = data_ref or None
    mes_etiqueta = ""
    if data_boletim:
        mes_etiqueta = data_boletim[:7]  # YYYY-MM
    else:
        # fallback: mês a partir del nombre do arquivo (BS-001-2026 → 2026)
        import re
        m = re.search(r"-(\d{4})(?:\.[01])?\.pdf$", pdf.name)
        if m:
            mes_etiqueta = m.group(1) + "-01"

    # Frontmatter YAML
    hoy = date.today().isoformat()
    title = titulo_frontmatter(pdf)
    nombre = nome_bolet(pdf)
    if data_boletim:
        created = data_boletim
    else:
        created = hoy

    partes = [
        "---",
        f'title: "{title}"',
    ]
    if data_boletim:
        partes.append(f"data: {data_boletim}")
    partes.extend([
        f"created: {created}",
        f"updated: {created}",
        "type: boletim-servico",
        f"tags: [boletim, mpt, {mes_etiqueta}]",
        "---",
        "",
        f"# {nombre}",
        "",
        f"> {total} paginas",
        "",
        "## Capa",
        "",
    ])

    # Páginas: <!-- pag N --> + texto
    for i in range(total):
        page = doc[i]
        num = i + 1
        texto = page.get_text("text").strip()
        partes.append(f"<!-- pag {num} -->")
        if texto:
            partes.append(texto)
        else:
            partes.append("*[Página sem texto extraíble — revisar PDF escaneado]*")

    doc.close()
    return "\n".join(partes)


def main():
    ap = argparse.ArgumentParser(description="Convierte PDFs de boletines a Markdown plano en hermes_mpt_kb/boletins")
    ap.add_argument("--orig", default="/opt/data/hermes-data/hermes_mpt_kb/raw/boletins",
                    help="Carpeta con PDFs de boletines (default: KB/raw/boletins)")
    ap.add_argument("--dest", default="/opt/data/hermes-data/hermes_mpt_kb/boletins",
                    help="Carpeta de salida para MDs planos (default: KB/boletins)")
    ap.add_argument("--filtro", default="*.pdf",
                    help="Glob de filtro (default: *.pdf)")
    args = ap.parse_args()

    orig = Path(args.orig)
    dest = Path(args.dest)
    if not orig.is_dir():
        sys.exit(f"❌ Origen no encontrado: {orig}")
    dest.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(orig.glob(args.filtro))
    if not pdfs:
        sys.exit(f"❌ No se encontraron PDFs en {orig} con filtro '{args.filtro}'")

    ok = 0
    errores = []
    for pdf in pdfs:
        try:
            md = converter_pdf(pdf)
            out = dest / f"{pdf.stem}.md"
            out.write_text(md, encoding="utf-8")
            ok += 1
        except Exception as e:
            errores.append((pdf.name, str(e)))

    print(f"✅ {ok}/{len(pdfs)} boletines convertidos a MD plano en {dest}")
    if errores:
        print("❌ Errores:")
        for nombre, err in errores[:20]:
            print(f"   {nombre}: {err}")

    return 0


if __name__ == "__main__":
    sys.exit(main())