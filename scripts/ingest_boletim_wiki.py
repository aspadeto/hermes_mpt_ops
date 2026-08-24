#!/usr/bin/env python3
"""
ingest_boletim_wiki.py — Ingestão de um boletim docling para o wiki do KB.

Gera uma página entities/bs-xxx-yyyy.md a partir de boletins_docling/BS-XXX-YYYY.md,
seguindo o SCHEMA.md do wiki.
"""

import argparse
import re
import sys
from pathlib import Path

DEFAULT_KB = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb")
DEFAULT_DOCLING = DEFAULT_KB / "boletins_docling"
DEFAULT_ENTITIES = DEFAULT_KB / "entities"
DEFAULT_INDEX = DEFAULT_KB / "index.md"
DEFAULT_LOG = DEFAULT_KB / "log.md"
DEFAULT_RAW = DEFAULT_KB / "raw/boletins"


def extract_boletim_fields(md_text: str) -> dict:
    data = {
        "numero": "",
        "ano": "",
        "data": "",
        "ementa": "",
        "regionais": [],
        "atos": [],
        "tipo": "boletim",
    }

    # número/ano do heading principal (case-insensitive, sem depender de ^#)
    m = re.search(r"BOLETIM\s+DE\s+SERVI[ÇC]O[^\n]*?0*(\d+)/(\d{4})", md_text, re.I)
    if m:
        data["numero"] = m.group(1).zfill(3)
        data["ano"] = m.group(2)

    # data: janela após o heading do boletim → "SEXTA-FEIRA, 17 DE JANEIRO DE 2025"
    if m:
        window = md_text[m.start():m.start() + 220]
        m_date = re.search(r"(\d{1,2})\s+DE\s+([A-ZÇÃÕÁÉÍÓÚ]+)\s+DE\s+(\d{4})", window)
        if m_date:
            dia = m_date.group(1).zfill(2)
            mes = {
                "JANEIRO": "01", "FEVEREIRO": "02", "MARÇO": "03", "ABRIL": "04",
                "MAIO": "05", "JUNHO": "06", "JULHO": "07", "AGOSTO": "08",
                "SETEMBRO": "09", "OUTUBRO": "10", "NOVEMBRO": "11", "DEZEMBRO": "12",
            }.get(m_date.group(2).upper(), "")
            if mes:
                data["data"] = f"{dia}/{mes}/{m_date.group(3)}"

    regionais = sorted(set(re.findall(r"PRT-?\d+[ªº]", md_text)))
    data["regionais"] = regionais

    # ajuste 2: parar ementa em headings internos também
    heading_interno = re.compile(r"^#{1,6}\s+#")
    atos = []
    current = None
    current_ementa = []
    for line in md_text.splitlines():
        if re.match(r"^(#{1,6}\s+)?N[º°]\s*\d+", line):
            if current is not None and current_ementa:
                current["ementa"] = " ".join(current_ementa)
                atos.append(current)
            m_num = re.search(r"N[º°]\s*(\d+[^\n]*)", line)
            current = {"numero": m_num.group(1).strip() if m_num else ""}
            current_ementa = []
            continue
        if current is None:
            continue
        s = line.strip()
        if not s or s.startswith("<!--") or s.startswith("|"):
            continue
        if heading_interno.match(s):
            continue
        current_ementa.append(s)
    if current is not None and current_ementa:
        current["ementa"] = " ".join(current_ementa)
        atos.append(current)

    cleaned = []
    for a in atos:
        e = a.get("ementa", "")
        # ajuste 3: normalizar número de ato e remover ruído
        e = re.sub(r"\s+", " ", e).strip()
        e = re.sub(r"N[º°]\s*\d+,\s*DE\s+\d{1,2}\s+DE\s+[A-ZÇÃÕÁÉÍÓÚ]+\s+DE\s+\.?\d{4}", "", e, flags=re.I)
        e = re.sub(r"N[º°]\s*\d+,\s*DE\s+\.?\d{4}", "", e, flags=re.I)
        e = re.sub(r"N[º°]\s*\d+\s+DE\s+\.?\d{4}", "", e, flags=re.I)
        e = re.sub(r"\s+", " ", e).strip()
        e = e[:180]
        if not e:
            continue
        cleaned.append({"numero": a.get("numero", ""), "ementa": e})
    data["atos"] = cleaned[:8]
    return data


def build_wiki_page(slug: str, fields: dict) -> str:
    numero = fields["numero"] or slug.split("-")[1]
    ano = fields["ano"] or slug.split("-")[2]
    data = fields["data"] or ""
    regionais = fields.get("regionais", [])
    atos = fields.get("atos", [])

    reg_links = ", ".join(f"[[{r.lower()}]]" for r in regionais[:6]) if regionais else "—"
    ato_lines = []
    for a in atos:
        num = a.get("numero", "").replace("Nº ", "").replace("N° ", "")
        ementa = a.get("ementa", "")[:140]
        ato_lines.append(f"- Ato {num} — {ementa}")
    atos_section = "\n".join(ato_lines) if ato_lines else "—"

    title = f"BS-{numero}/{ano}"
    return f"""---
title: {title}
created: {data or 's/d'}
updated: {data or 's/d'}
type: normativo
tags: [boletim, boletim-servico]
fontes: [raw/boletins/BS-{numero}-{ano}.pdf]
confianca: media
---

# {title}

- **Data:** {data}
- **Ano:** {ano}
- **Número:** {numero}
- **PDF:** [[raw/boletins/BS-{numero}-{ano}.pdf]]

## Atos principais

{atos_section}

## Regionais mencionadas

{reg_links}
"""


def append_index(slug: str, title: str) -> None:
    index_path = DEFAULT_INDEX
    entry = f"- [[{slug}]] — {title}\n"
    text = index_path.read_text(encoding="utf-8")
    if slug in text or title in text:
        return
    marker = "## Entidades\n"
    if marker in text:
        text = text.replace(marker, marker + "\n" + entry, 1)
        index_path.write_text(text, encoding="utf-8")


def append_log(date_str: str, title: str, ano: str = "") -> None:
    log_path = DEFAULT_LOG
    log_date = date_str.strip() or f"{ano}-01-01" if ano else "s/d"
    entry = f"## [{log_date}] ingest | Boletim {title}\n- Arquivo: entities/{title.lower()}.md\n\n"
    text = log_path.read_text(encoding="utf-8")
    if title in text:
        return
    text += "\n" + entry
    log_path.write_text(text, encoding="utf-8")


def ingest_one(bs_md: Path, dry_run: bool = False) -> Path | None:
    m = re.search(r"BS-(\d+)-(\d{4})\.md$", bs_md.name)
    if not m:
        return None
    numero, ano = m.group(1), m.group(2)
    slug = f"bs-{numero}-{ano}"
    text = bs_md.read_text(encoding="utf-8")
    fields = extract_boletim_fields(text)
    page = build_wiki_page(slug, fields)

    out = DEFAULT_ENTITIES / f"{slug}.md"
    if dry_run:
        print(f"[dry-run] {out}")
        return out
    out.write_text(page, encoding="utf-8")
    append_index(slug, f"BS-{numero}/{ano}")
    append_log(fields.get("data") or "", f"BS-{numero}/{ano}", fields.get("ano") or "")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingestão de boletim docling para wiki")
    parser.add_argument("boletim", nargs="?", help="Caminho do BS-XXX-YYYY.md")
    parser.add_argument("--kb", default=str(DEFAULT_KB))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    kb = Path(args.kb)
    docling = kb / "boletins_docling"

    if args.boletim:
        path = Path(args.boletim)
        if not path.exists():
            path = docling / Path(args.boletim).name
    else:
        paths = sorted(docling.glob("BS-*.md"))
        if not paths:
            print("Nenhum boletim docling encontrado.")
            return 1
        path = paths[0]
        print(f"Sem alvo: usando {path.name}")

    out = ingest_one(path, dry_run=args.dry_run)
    if out is None:
        print("Formato inválido.")
        return 1
    print(f"Página wiki criada: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
