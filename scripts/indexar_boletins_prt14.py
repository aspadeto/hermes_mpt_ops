#!/usr/bin/env python3
"""indexar_boletins_prt14.py — Indexa atos de Boletins de Serviço do MPT.

Varre os MDs extraídos (audit_boletim.py) e registra num SQLite os atos
relevantes à PRT14 (Procuradoria Regional do Trabalho da 14ª Região).

O MD extraído tem cada ato como um header Markdown:
    ## PORTARIA Nº 132          ← título do ato (tipo + número)
    <!-- pág N -->              ← conteúdo do ato até o próximo ##

Uso:
    indexar_boletins_prt14.py /tmp/md-out2025/ [--db boletins_idx.db]

Saída: SQLite com tabela `atos`:
    boletim, data_bs, tipo, numero, titulo, resumo, relevante
"""

import argparse
import re
import sqlite3
import sys
from pathlib import Path

# Cabeçalho do BS na capa: "BOLETIM DE SERVIÇO ELETRÔNICO \n184/2025 \nQUARTA-FEIRA, 1 DE OUTUBRO"
BS_DATA_RE = re.compile(
    r"(\d{1,2})\s*DE\s+([A-ZÇÃÉÍÓÚÊ]+)\s*DE\s+(\d{4})",
    re.IGNORECASE,
)
MESES = {
    "JANEIRO": "01", "FEVEREIRO": "02", "MARÇO": "03", "MARCO": "03", "ABRIL": "04",
    "MAIO": "05", "JUNHO": "06", "JULHO": "07", "AGOSTO": "08", "SETEMBRO": "09",
    "OUTUBRO": "10", "NOVEMBRO": "11", "DEZEMBRO": "12",
}

# Marcadores de relevância PRT14 (procurados no TEXTO do ato)
PRT14_RE = re.compile(
    r"PRT-?14|PRT14|14[ªa]\s*REGI[ÃA]O|PROCURADORIA REGIONAL DO TRABALHO DA 14|"
    r"PORTO VELHO/RO|PROCURADOR-CHEFE DA PROCURADORIA REGIONAL DO TRABALHO DA 14|"
    r"ACRE|ROND[ÔO]NIA",
    re.IGNORECASE,
)


def extrair_atos(md: str) -> list[dict]:
    """Extrai atos dos headers '## TIPO Nº X' do MD."""
    atos = []
    # regex do header de ato: "## PORTARIA Nº 132" (ou "Nº 132/2025", "DESPACHO", etc.)
    header_re = re.compile(
        r"^##\s+(?P<tipo>PORTARIA|DESPACHO|AVISO|EXTRATO|ATA|DECISÃO|RESOLUÇÃO|"
        r"INSTRUÇÃO\s*NORMATIVA|EDITAL|COMUNICADO|RETIFICAÇÃO|ERRATA|ATO|"
        r"RECOMENDAÇÃO|NOTIFICAÇÃO|INTIMAÇÃO|CITAÇÃO|REQUERIMENTO|OFÍCIO|"
        r"MEMORANDO|PARECER|RELATÓRIO)(?:\s+N[º°]?\s*)?(?P<num>[\d.]+)?"
        r"(?:/(?P<ano>\d{4}))?",
        re.IGNORECASE | re.MULTILINE,
    )
    matches = list(header_re.finditer(md))
    for i, m in enumerate(matches):
        fim = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        corpo = md[m.end():fim]
        atos.append({
            "tipo": m.group("tipo").upper(),
            "numero": m.group("num") or "",
            "titulo": m.group(0).strip().lstrip("#").strip(),
            "corpo": corpo,
        })
    return atos


def data_do_boletim(md: str) -> str:
    """Extrai a data do BS da capa (1º 'DD DE MÊS DE AAAA' do cabeçalho)."""
    m = BS_DATA_RE.search(md)
    if not m:
        return ""
    mes = MESES.get(m.group(2).upper(), "??")
    return f"{m.group(3)}-{mes}-{int(m.group(1)):02d}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dir_md", help="diretório com os .md extraídos")
    ap.add_argument("--db", default="boletins_idx.db", help="arquivo SQLite de saída")
    args = ap.parse_args()

    d = Path(args.dir_md)
    mds = sorted(d.glob("BS-*.md"))
    if not mds:
        sys.exit(f"Nenhum BS-*.md em {d}")
    print(f"📂 {len(mds)} MDs em {d}")

    conn = sqlite3.connect(args.db)
    conn.execute("DROP TABLE IF EXISTS atos")
    conn.execute("""
        CREATE TABLE atos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            boletim TEXT NOT NULL,
            data_bs TEXT,
            tipo TEXT,
            numero TEXT,
            titulo TEXT,
            relevante INTEGER DEFAULT 0,
            resumo TEXT
        )
    """)

    total = 0
    relevantes = 0
    for md_path in mds:
        md = md_path.read_text(encoding="utf-8")
        data_bs = data_do_boletim(md)
        for ato in extrair_atos(md):
            rel = 1 if PRT14_RE.search(ato["corpo"]) else 0
            conn.execute(
                "INSERT INTO atos (boletim, data_bs, tipo, numero, titulo, relevante, resumo) "
                "VALUES (?,?,?,?,?,?,?)",
                (md_path.stem, data_bs, ato["tipo"], ato["numero"], ato["titulo"],
                 rel, re.sub(r"\s+", " ", ato["corpo"])[:500]),
            )
            total += 1
            relevantes += rel

    conn.commit()
    print(f"✅ {total} atos indexados, {relevantes} relevantes à PRT14")
    print(f"   Banco: {args.db}")
    conn.close()


if __name__ == "__main__":
    main()
