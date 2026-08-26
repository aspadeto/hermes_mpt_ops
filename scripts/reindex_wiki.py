#!/usr/bin/env python3
"""
reindex_wiki.py — Reorganiza a seção ## Entidades do index.md.
Lê slugs dos arquivos entities/bs-*.md, agrupa por ano, ordena numericamente,
e reescreve apenas o bloco ## Entidades, preservando as demais seções.

Uso:
    python scripts/reindex_wiki.py --kb /path/to/kb [--dry-run]
"""

import argparse
import re
import shutil
import sys
from pathlib import Path
from typing import List, Tuple


def parse_slug(slug: str) -> Tuple[int, int, int]:
    """
    Retorna chave de ordenação (ano, parte_int, parte_dec).
    bs-98-2026   → (2026, 98,  0)
    bs-8.1-2025  → (2025,  8,  1)
    bs-98.2-2026 → (2026, 98,  2)
    bs-98.1-2026 → (2026, 98,  1)
    """
    m = re.match(r"bs-(\d+)(?:\.(\d+))?-(\d{4})$", slug)
    if not m:
        return (9999, 9999, 9999)  # fallback para slugs malformados
    ano = int(m.group(3))
    parte_int = int(m.group(1))
    parte_dec = int(m.group(2)) if m.group(2) else 0
    return (ano, parte_int, parte_dec)


def build_index_block(slugs: List[str]) -> str:
    """Gera o bloco ## Entidades ordenado e agrupado por ano."""
    # Agrupa e ordena
    slugs_by_year: dict[int, List[str]] = {}
    for slug in slugs:
        ano, *_ = parse_slug(slug)
        slugs_by_year.setdefault(ano, []).append(slug)

    for year in slugs_by_year:
        slugs_by_year[year].sort(key=lambda s: parse_slug(s))

    lines = ["## Entidades"]
    # Anos em ordem decrescente
    for year in sorted(slugs_by_year.keys(), reverse=True):
        lines.append(f"")
        lines.append(f"### {year}")
        for slug in slugs_by_year[year]:
            # Reconstrói title: "BS-{numero}/{ano}"
            m = re.match(r"bs-(\d+(?:\.\d+)?)-(\d{4})", slug)
            if m:
                title = f"BS-{m.group(1)}/{m.group(2)}"
            else:
                title = slug.replace("-", "/").upper()
            lines.append(f"- [[{slug}]] — {title}")

    lines.append("")  # linha em branco final
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Reorganiza index.md por ano")
    parser.add_argument("--kb", required=True, help="Caminho da KB (ex: /path/hermes_mpt_kb)")
    parser.add_argument("--dry-run", action="store_true", help="Gera saída em /tmp sem alterar index.md")
    args = parser.parse_args()

    kb = Path(args.kb)
    entities_dir = kb / "entities"
    index_path = kb / "index.md"

    if not index_path.exists():
        print(f"Erro: {index_path} não encontrado", file=sys.stderr)
        return 1

    # 1. Lê slugs do disco (entities/bs-*.md)
    slugs = []
    patterns = ["bs-*.md"]
    for p in patterns:
        for f in sorted(entities_dir.glob(p)):
            stem = f.stem  # bs-98-2026
            if re.match(r"bs-\d+(?:\.\d+)?-\d{4}$", stem):
                slugs.append(stem)

    slugs = sorted(set(slugs))
    print(f"Slugs encontrados no disco: {len(slugs)}", file=sys.stderr)

    # 2. Gera novo bloco
    new_block = build_index_block(slugs)

    # 3. Lê index atual e preserva seções extra
    current = index_path.read_text(encoding="utf-8")

    # Divide: antes de ## Entidades, o bloco ## Entidades, depois
    partes = re.split(r"^## Entidades\n", current, maxsplit=1, flags=re.MULTILINE)
    if len(partes) < 2:
        print("Erro: seção ## Entidades não encontrada no index.md", file=sys.stderr)
        return 1

    # Tudo antes de ## Entidades
    antes = partes[0]
    # Tudo depois do bloco ## Entidades (próximo ## ou EOF)
    depois_match = re.search(r"\n## ", partes[1])
    if depois_match:
        depois = partes[1][depois_match.start():]  # inclui "\n## " no início
    else:
        depois = ""

    novo = antes + new_block + "\n" + depois.lstrip("\n")

    if args.dry_run:
        tmp = Path("/tmp/index_reindexed.md")
        tmp.write_text(novo, encoding="utf-8")
        print(f"\n=== Dry-run: amostra (primeiros 30 linhas) ===")
        for i, line in enumerate(tmp.read_text(encoding="utf-8").splitlines()[:30], 1):
            print(f"{i:>4}|{line}")
        print(f"\n--- Total de linhas: {novo.count(chr(10))} → {tmp}")
        print(f"--- Entradas [[bs-: {novo.count('[[')}")
        return 0

    # Backup
    bak = index_path.with_suffix(".md.bak")
    shutil.copy2(index_path, bak)
    print(f"Backup: {bak}", file=sys.stderr)

    # Aplica
    index_path.write_text(novo, encoding="utf-8")
    print(f"Index reescrito: {index_path}", file=sys.stderr)

    # Verificações: conta só as entradas dentro de ## Entidades
    texto = index_path.read_text(encoding="utf-8")
    # Extrai o bloco entre ## Entidades e o próximo ##
    m_ent = re.search(r"^## Entidades\n(.*?)(?=\n## |\Z)", texto, re.MULTILINE | re.DOTALL)
    if m_ent:
        qtd = sum(1 for line in m_ent.group(1).splitlines() if line.startswith("- [["))
    else:
        qtd = 0
    print(f"Entradas no bloco ## Entidades: {qtd}", file=sys.stderr)
    if qtd != len(slugs):
        print(f"⚠ Atenção: {qtd} entradas no bloco, esperado {len(slugs)}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())