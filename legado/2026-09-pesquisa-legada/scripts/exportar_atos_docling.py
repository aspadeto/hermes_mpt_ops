#!/usr/bin/env python3
"""exportar_atos_docling.py — Gera atos_normativos.csv a partir dos .md docling.

Lê os markdown estruturados do Docling (hermes_mpt_kb/boletins_docling/),
detecta os atos com detectar_atos_docling.py e escreve o CSV (e opcionalmente
md/tsv/toml) com as MESMAS colunas do antigo atos_normativos, mas a partir do
corpus docling (canônico, decisão #35).

Colunas:
    boletim_data, boletim_numero, tipo, numero, ano, orgao,
    data_ato, pagina, secao, ementa, relevante(=0)

O boletim_data (data de circulação) é extraído do cabeçalho do boletim
("SEGUNDA-FEIRA, DD DE MÊS DE AAAA" ou "CIRCULAÇÃO: DD/MM/AAAA"); o ano vem do
nome do arquivo.

Uso:
    python3 exportar_atos_docling.py [--raiz DIR] [--dest DIR] [--formato csv md ...]
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# Importa config de caminhos e o parser docling
from ops_paths import KB_BOLETINS_DOCLING, OPS_PATH, OPS_DATA
sys.path.insert(0, str(OPS_PATH / "scripts"))
import detectar_atos_docling as dad

MESES = {
    "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
    "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
    "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12",
}


def data_circulacao(md: Path) -> str | None:
    """Extrai a data de circulação do cabeçalho do boletim docling."""
    txt = md.read_text(encoding="utf-8")
    # padrão 1: CIRCULAÇÃO: DD/MM/AAAA
    m = re.search(r"CIRCULA[ÇC][ÃA]O\s*[:.]?\s*(\d{1,2})/(\d{1,2})/(\d{4})", txt, re.IGNORECASE)
    if m:
        try:
            return f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
        except ValueError:
            pass
    # padrão 2: "SEGUNDA-FEIRA, DD DE MÊS DE AAAA" (capa)
    m = re.search(
        r"\b(\d{1,2})\s+DE\s+([A-ZÇÃÊÓÍÀ-Ú]+)\s+DE\s+(\d{4})\b",
        txt, re.IGNORECASE)
    if m:
        mes = MESES.get(m.group(2).lower())
        if mes:
            try:
                return f"{int(m.group(3)):04d}-{mes}-{int(m.group(1)):02d}"
            except ValueError:
                pass
    return None


def coletar_atos(raiz: Path) -> list[dict]:
    atos = []
    for md in sorted(raiz.glob("BS-*.md")):
        boletim_data = data_circulacao(md)
        boletim_numero = dad.numero_boletim(md)
        ano_bs = dad.ano_do_arquivo(md)
        for a in dad.atos_por_arquivo_docling(md):
            # data_ato já vem normalizada do parser (YYYY-MM-DD) ou None
            atos.append({
                "boletim_data": boletim_data,
                "boletim_numero": boletim_numero,
                "tipo": a.get("tipo"),
                "numero": a.get("numero"),
                "ano": a.get("ano") or ano_bs,
                "orgao": a.get("orgao"),
                "data_ato": a.get("data"),
                "pagina": a.get("pagina"),
                "secao": a.get("secao"),
                "ementa": (a.get("ementa") or "").replace("\n", " ").strip(),
                "relevante": 0,
            })
    return atos


def colunas() -> list[str]:
    return ["boletim_data", "boletim_numero", "tipo", "numero", "ano",
            "orgao", "data_ato", "pagina", "secao", "ementa", "relevante"]


def escrever_csv(atos, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        w.writerow(colunas())
        for a in atos:
            w.writerow([a.get(c, "") for c in colunas()])


def escrever_md(atos, path):
    def esc(v):
        return str(v).replace("|", "\\|").replace("\n", " ").strip()
    cols = colunas()
    linhas = ["| " + " | ".join(cols) + " |",
              "|" + "|".join(["---"] * len(cols)) + "|"]
    for a in atos:
        linhas.append("| " + " | ".join(esc(a.get(c, "")) for c in cols) + " |")
    path.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def escrever_tsv(atos, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        w.writerow(colunas())
        for a in atos:
            w.writerow([a.get(c, "") for c in colunas()])


def escrever_toml(atos, path):
    def toml_str(v):
        v = str(v).replace("\\", "\\\\").replace('"', '\\"')
        return f'"{v}"' if isinstance(v, str) else v
    partes = ["# atos_normativos gerados do corpus docling", "",
              f"# Total: {len(atos)} atos", ""]
    for a in atos:
        partes.append("[[atos]]")
        for c in colunas():
            v = a.get(c)
            if v is None:
                continue
            partes.append(f"{c} = {toml_str(v)}")
        partes.append("")
    path.write_text("\n".join(partes), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Gera atos_normativos a partir dos MDs docling")
    ap.add_argument("--raiz", default=str(KB_BOLETINS_DOCLING))
    ap.add_argument("--base", default="atos_normativos")
    ap.add_argument("--dest", default=str(OPS_DATA / "indices"))
    ap.add_argument("--formato", nargs="+", default=["csv"],
                    choices=["csv", "md", "tsv", "toml"])
    args = ap.parse_args()

    raiz = Path(args.raiz)
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    print(f"Coletando atos de {raiz} ...")
    atos = coletar_atos(raiz)
    n_md = len(list(raiz.glob("BS-*.md")))
    print(f"  → {len(atos)} atos detectados em {n_md} MDs docling")

    if "csv" in args.formato:
        escrever_csv(atos, dest / f"{args.base}.csv")
    if "md" in args.formato:
        escrever_md(atos, dest / f"{args.base}.md")
    if "tsv" in args.formato:
        escrever_tsv(atos, dest / f"{args.base}.tsv")
    if "toml" in args.formato:
        escrever_toml(atos, dest / f"{args.base}.toml")

    for ext in args.formato:
        p = dest / f"{args.base}.{ext}"
        if p.exists():
            print(f"  ✅ {p.name}: {p.stat().st_size:,} bytes")

    print("\n✅ Exportação concluída em:", dest)


if __name__ == "__main__":
    main()
