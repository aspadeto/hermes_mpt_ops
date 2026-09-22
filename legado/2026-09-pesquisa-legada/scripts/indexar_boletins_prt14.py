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

def _subbloco_prt14(corpo: str) -> str | None:
    """Isola o sub-bloco da PRT14 dentro do corpo do ato.

    O corpo de um ato pode conter várias regionais ("PRT-8ª REGIÃO",
    "PRT-11ª REGIÃO", "PRT-14ª REGIÃO"... na mesma página). Divide pelos
    cabeçalhos de regional e retorna só o trecho da 14ª (ou None).
    """
    # cabeçalhos de seção: "PRT-8ª REGIÃO", "PRT-11ª REGIÃO", etc.
    cab = re.compile(
        r"PRT-?\s*(\d{1,2})[ªa]\s*REGI[ÃA]O(?:\s*[–-]\s*[A-ZÇÃÉÍÓÚÊ /]+)?",
        re.IGNORECASE,
    )
    partes = []
    ultimo = None
    ultimo_fim = 0
    for m in cab.finditer(corpo):
        if ultimo is not None:
            partes.append((ultimo, corpo[ultimo_fim:m.start()]))
        ultimo = m.group(1)
        ultimo_fim = m.end()
    if ultimo is not None:
        partes.append((ultimo, corpo[ultimo_fim:]))
    for num, texto in partes:
        if num == "14":
            return texto
    return None


# Marcadores de relevância PRT14 (procurados no TEXTO do ato)
# Nível 2 = ato DA PRT14: tem cabeçalho de seção "PRT-14ª REGIÃO" e o sub-bloco
# da 14ª contém assinatura/verbos de ato (não é só uma citação isolada)
PRT14_FORTE_RE = re.compile(
    r"PROCURADOR-CHEFE DA PROCURADORIA REGIONAL DO TRABALHO DA 14[ªa]|"
    r"(?:no uso de suas atribuições|resolve|designar|RESOLVE|CONSIDERANDO)",
    re.IGNORECASE,
)
# Nível 1 = menciona a 14ª Região / RO / AC no corpo (decisões da PG que afetam a PRT14)
PRT14_MENCAO_RE = re.compile(
    r"14[ªa]\s*REGI[ÃA]O|PORTO VELHO/RO|ROND[ÔO]NIA|ACRE|PRT\s*-?\s*14",
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
    # número no corpo: primeiro "N° 132, DE 1º DE OUTUBRO DE 2025" APÓS o
    # cabeçalho de seção (PRT-14ª REGIÃO / PROCURADORIA...) — ignora citações
    # internas como "Portaria PGT nº 1728"
    num_corpo_re = re.compile(
        r"N[º°]\s*(\d[\d.]*)\s*,\s*DE\s+\d{1,2}[º°]?\s*DE\s+[A-ZÇÃÉÍÓÚÊ]+\s*DE\s+\d{4}",
        re.IGNORECASE,
    )
    matches = list(header_re.finditer(md))
    for i, m in enumerate(matches):
        fim = matches[i + 1].start() if i + 1 < len(matches) else len(md)
        corpo = md[m.end():fim]
        numero = m.group("num") or ""
        if not numero:
            mc = num_corpo_re.search(corpo)
            if mc:
                numero = mc.group(1)
        atos.append({
            "tipo": m.group("tipo").upper(),
            "numero": numero,
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


def _ementa(sub: str) -> str:
    """Extrai a ementa do sub-bloco da PRT14 (texto entre número/data e assinatura)."""
    m = re.search(
        r"N[º°]\s*([\d.]+),\s*DE\s+\d{1,2}[º°]?\s*DE\s+[A-ZÇÃÉÍÓÚÊ]+\s*DE\s+(\d{4})",
        sub,
        re.IGNORECASE,
    )
    if m:
        depois = sub[m.end():]
    else:
        depois = sub[80:]
    ementa = depois.split("O PROCURADOR")[0]
    ementa = ementa.split("RESOLVE")[0].split("Considerando")[0]
    return re.sub(r"\s+", " ", ementa).strip(" -–")


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
            corpo = re.sub(r"\s+", " ", ato["corpo"])
            sub = _subbloco_prt14(corpo)
            rel = 2 if (sub and PRT14_FORTE_RE.search(sub)) else (1 if PRT14_MENCAO_RE.search(corpo) else 0)
            numero = ato["numero"]
            ementa = ""
            if sub:
                mc = re.search(r"N[º°]\s*([\d.]+),\s*DE\s+\d{1,2}[º°]?\s*DE", sub, re.IGNORECASE)
                if mc:
                    numero = mc.group(1)
                ementa = _ementa(sub)
            conn.execute(
                "INSERT INTO atos (boletim, data_bs, tipo, numero, titulo, relevante, resumo) "
                "VALUES (?,?,?,?,?,?,?)",
                (md_path.stem, data_bs, ato["tipo"], numero, ato["titulo"],
                 rel, ementa or corpo[:500]),
            )
            total += 1
            relevantes += rel

    conn.commit()
    print(f"✅ {total} atos indexados, {relevantes} relevantes à PRT14")
    print(f"   Banco: {args.db}")
    conn.close()


if __name__ == "__main__":
    main()
