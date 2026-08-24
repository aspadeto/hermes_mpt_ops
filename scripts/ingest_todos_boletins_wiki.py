#!/usr/bin/env python3
"""
ingest_todos_boletins_wiki.py — Itera todos os boletins docling e aplica ingestão no wiki.

Uso:
  python scripts/ingest_todos_boletins_wiki.py
  python scripts/ingest_todos_boletins_wiki.py --dry-run
  python scripts/ingest_todos_boletins_wiki.py --limit 20
  python scripts/ingest_todos_boletins_wiki.py --only 012,050,001-2026
"""

import argparse
import sys
from pathlib import Path

DEFAULT_KB = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb")
DEFAULT_DOCLING = DEFAULT_KB / "boletins_docling"
DEFAULT_ENTITIES = DEFAULT_KB / "entities"

try:
    from ingest_boletim_wiki import ingest_one
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ingest_boletim_wiki import ingest_one


def parse_only(values: str):
    result = []
    for part in values.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part and not part.startswith("BS-"):
            parts = part.split("-")
            if len(parts) == 2 and parts[1].isdigit():
                result.append((parts[0], parts[1]))
                continue
        result.append((part, None))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingestão em lote de boletins docling no wiki")
    parser.add_argument("--kb", default=str(DEFAULT_KB))
    parser.add_argument("--docling", default=str(DEFAULT_DOCLING))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--only", type=str, default="")
    args = parser.parse_args()

    kb = Path(args.kb)
    docling = Path(args.docling)
    entities = kb / "entities"
    paths = sorted(docling.glob("BS-*.md"))
    if not paths:
        print("Nenhum boletim docling encontrado.")
        return 1

    targets = None
    if args.only:
        raw = parse_only(args.only)
        targets = set()
        for numero, ano in raw:
            if ano:
                targets.add(f"bs-{numero}-{ano}")
            else:
                for p in paths:
                    m = p.stem
                    if m == f"BS-{numero}":
                        targets.add(m.replace("BS-", "bs-"))
        if not targets:
            print("Nenhum alvo encontrado em --only.")
            return 1

    count = 0
    errors = []
    for path in paths:
        if targets and path.stem.lower().replace("bs-", "bs-") not in targets:
            continue
        try:
            out = ingest_one(path, dry_run=args.dry_run)
        except Exception as e:
            errors.append(f"{path.name}: {e}")
            continue
        if out is None:
            continue
        count += 1
        if args.limit and count >= args.limit:
            break

    print(f"Ingestão concluída: {count} boletins processados.")
    if errors:
        print(f"Erros: {len(errors)}")
        for e in errors[:20]:
            print(f" - {e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
