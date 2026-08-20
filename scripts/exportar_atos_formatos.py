#!/usr/bin/env python3
"""exportar_atos_formatos.py — Exporta o conteúdo da tabela atos_normativos
dos MDs planos de boletins em 4 formatos: .md, .csv, .tsv, .toml.

Lê os MDs planos de hermes_mpt_kb/boletins/*.md (frontmatter com `data:` de
circulação), detecta cada ato com a MESMA lógica do catalogar_atos.py
(função atos_por_arquivo) e escreve 4 arquivos com os MESMOS dados, cada um
na sua própria estrutura:

    atos_normativos.md    → tabela Markdown (1 linha por ato)
    atos_normativos.csv   → CSV separado por vírgula (com cabeçalho)
    atos_normativos.tsv   → TSV separado por tab (com cabeçalho)
    atos_normativos.toml  → [[atos]] array of tables

Colunas (todas deriváveis dos MDs):
    boletim_data, boletim_numero, tipo, numero, ano, orgao,
    data_ato, pagina, secao, ementa, relevante(=0 default)

Uso:
    python3 exportar_atos_formatos.py [--raiz DIR] [--dest DIR]
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

# Mesa de mês (printf correto de acentos)
MESES = {
    "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
    "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
    "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12",
}


def parse_frontmatter(md: Path) -> dict:
    """Extrai o frontmatter YAML simples (--- ... ---) do MD de boletim."""
    txt = md.read_text(encoding="utf-8")
    fm = {}
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.DOTALL)
    header = m.group(1) if m else ""
    for linha in header.splitlines():
        if ":" not in linha:
            continue
        chave, _, valor = linha.partition(":")
        chave = chave.strip()
        valor = valor.strip().strip('"').strip("'")
        # tags: [...] → mantém como string descritiva
        fm[chave] = valor
    return fm


def normalizar_data_ato(data: str | None) -> str | None:
    """Normaliza '30 DE OUTUBRO DE 2024' ou '2024-10-30' → 'YYYY-MM-DD'."""
    if not data or data.count("-") == 2:
        return data
    m = re.search(r"(\d{1,2})\s+DE\s+([A-ZÇÃÊÓÍÀ-Ú]+)\s+DE\s+(\d{4})", data, re.IGNORECASE)
    if m:
        dia, mes_nome, ano = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        mes = MESES.get(mes_nome)
        if mes:
            return f"{ano:04d}-{mes:02d}-{dia:02d}"
    return None


def coletar_atos(raiz: Path) -> list[dict]:
    """Varre os MDs planos em raiz/ e retorna a lista de atos detectados."""
    sys.path.insert(0, str(raiz.parent.parent / "hermes_mpt_ops" / "scripts"))
    try:
        import catalogar_atos as cat
    except ImportError:
        # fallback: caminho absoluto do repo
        import os
        repo = os.environ.get("OPS_PATH", "/opt/data/hermes-data/hermes_mpt_ops")
        sys.path.insert(0, repo + "/scripts")
        import catalogar_atos as cat

    atos = []
    for md in sorted(raiz.glob("*.md")):
        fm = parse_frontmatter(md)
        boletim_data = fm.get("data")
        # numero do boletim do frontmatter title: "BS 071-2025" → "71/2025"
        title = fm.get("title", md.stem)
        m = re.search(r"BS\s*([\d.]+)[-\s](\d{4})", title)
        boletim_numero = f"{m.group(1)}/{m.group(2)}" if m else md.stem

        for a in cat.atos_por_arquivo(md):
            atos.append({
                "boletim_data": boletim_data,
                "boletim_numero": boletim_numero,
                "tipo": a.get("tipo"),
                "numero": a.get("numero"),
                "ano": a.get("ano"),
                "orgao": a.get("orgao"),
                "data_ato": normalizar_data_ato(a.get("data")),
                "pagina": a.get("pagina"),
                "secao": a.get("secao"),
                "ementa": (a.get("ementa") or "").replace("\n", " ").strip(),
                "relevante": 0,
            })
    return atos


def colunas() -> list[str]:
    return ["boletim_data", "boletim_numero", "tipo", "numero", "ano",
            "orgao", "data_ato", "pagina", "secao", "ementa", "relevante"]


def sanitizar_md(v: str) -> str:
    """Escapa pipe e quebras para não quebrar a tabela Markdown."""
    return str(v).replace("|", "\\|").replace("\n", " ").strip()


def escrever_md(atos, path):
    cols = colunas()
    cab = "| " + " | ".join(cols) + " |"
    sep = "|" + "|".join(["---"] * len(cols)) + "|"
    linhas = [cab, sep]
    for a in atos:
        cel = [sanitizar_md(a.get(c, "")) for c in cols]
        linhas.append("| " + " | ".join(cel) + " |")
    path.write_text("\n".join(linhas) + "\n", encoding="utf-8")


def escrever_csv(atos, path):
    cols = colunas()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
        w.writerow(cols)
        for a in atos:
            w.writerow([a.get(c, "") for c in cols])


def escrever_tsv(atos, path):
    cols = colunas()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        w.writerow(cols)
        for a in atos:
            w.writerow([a.get(c, "") for c in cols])


def escrever_toml(atos, path):
    def toml_str(v):
        v = str(v).replace("\\", "\\\\").replace('"', '\\"')
        return f'"{v}"' if isinstance(v, str) else v

    partes = [
        "# Conteúdo da tabela atos_normativos (extraído dos MDs de boletins)",
        "",
        "# Total: {total} atos",
        "",
    ]
    for i, a in enumerate(atos):
        partes.append(f"[[atos]]")
        for c in colunas():
            v = a.get(c)
            if v is None:
                continue
            partes.append(f"{c} = {toml_str(v)}")
        partes.append("")
    path.write_text("\n".join(partes), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Exporta atos_normativos dos MDs em formatos")
    ap.add_argument("--raiz", default="/opt/data/hermes-data/hermes_mpt_kb/boletins")
    ap.add_argument("--base", default="atos_normativos")
    ap.add_argument("--dest", required=True, help="Pasta de saída (obrigatório)")
    ap.add_argument("--formato", nargs="+", default=["csv"],
                    choices=["csv", "md", "tsv", "toml"],
                    help="Formatos a gerar (default: csv — único usado na indexação)")
    args = ap.parse_args()

    raiz = Path(args.raiz)
    dest = Path(args.dest)
    dest.mkdir(parents=True, exist_ok=True)

    print(f"Coletando atos de {raiz} ...")
    atos = coletar_atos(raiz)
    print(f"  → {len(atos)} atos detectados em {len(list(raiz.glob('*.md')))} MDs")

    dest.mkdir(parents=True, exist_ok=True)
    if "md" in args.formato:
        escrever_md(atos, dest / f"{args.base}.md")
    if "csv" in args.formato:
        escrever_csv(atos, dest / f"{args.base}.csv")
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