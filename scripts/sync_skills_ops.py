#!/usr/bin/env python3
"""
sync_skills_ops.py — Sincroniza as skills do Hermes (~/.hermes/skills) para
a pasta skills/ do repositório hermes_mpt_ops (versionamento no git).

O ~/.hermes/skills NÃO é versionado em git. Este script copia as skills
LOCAIS (criadas/atualizadas pelo usuário/agente) para OPS_PATH/skills/,
onde participam do controle de versão e do auto-commit.

O que é copiado por skill:
    SKILL.md
    scripts/    (arquivos .py/.sh)
    references/ (arquivos .md)

O que NÃO é copiado:
    __pycache__/, *.pyc  (lixo)
    .archive/            (skills arquivadas — não são ativas)
    .curator_*/.bundled_*/.git (metadados internos do Hermes)
    assets/ binários grandes (se houver, decidir caso a caso)

Uso:
    python3 sync_skills_ops.py [--dry-run]
"""

import argparse
import shutil
import sys
from pathlib import Path

# Importa configuração centralizada de caminhos
from ops_paths import OPS_PATH, OPS_SKILLS

SKILLS_SRC = Path.home() / ".hermes" / "skills"
SKILLS_DEST = OPS_SKILLS

# ------------------------------------------------------------------
# Skills customizadas do ambiente MPT/DR que devem ser versionadas.
# AO CRIAR UMA SKILL NOVA, ADICIONAR AQUI.
# (Decisão do usuário 20/08/2026: somente skills customizadas, não bundled.)
# ------------------------------------------------------------------
CUSTOM_SKILLS = {
    # --- Conhecimento MPT/DR (definitivas) ---
    "dr-mpt-ops",
    "pesquisa-boletins-inteligente",
    "boletim-servico-mpt",
    "analise-pgea",
    "catalogar-atos-boletins",
    "compreensao-pgea",
    "ingestao-pdf-wiki",
    "documentos-mpt",
    # --- Infra/automação do ambiente (custom) ---
    "hermes-cron-automation",
    "browser-infrastructure",
    "container-host-ssh",
    "selfhosted-remote-access",
    "tailscale-remote-access",
    # --- Docling (conversão estruturada de PDFs) ---
    "docling-documentos",
}

# Extensões a copiar dentro de scripts/ e references/
EXTS = {".py", ".sh", ".bash", ".md", ".txt", ".toml", ".json", ".yaml", ".yml"}


def iterar_skills():
    """Itera APENAS as skills customizadas (CUSTOM_SKILLS) locais ativas.
    Estrutura: ~/.hermes/skills/<categoria>/<skill>/SKILL.md
    Também suporta skills diretas: ~/.hermes/skills/<skill>/SKILL.md"""
    if not SKILLS_SRC.is_dir():
        return
    for d in SKILLS_SRC.iterdir():
        if not d.is_dir() or d.name.startswith("."):
            continue
        # skill direta
        if (d / "SKILL.md").exists():
            if d.name in CUSTOM_SKILLS:
                yield d
            continue
        # categoria -> skills dentro
        for sub in d.iterdir():
            if sub.is_dir() and not sub.name.startswith(".") and (sub / "SKILL.md").exists():
                if sub.name in CUSTOM_SKILLS:
                    yield sub


def copiar_skill(skill_dir: Path, dry_run: bool) -> int:
    """Copia uma skill para o destino. Retorna nº de arquivos copiados."""
    dest_skill = SKILLS_DEST / skill_dir.name
    n = 0
    # SKILL.md
    src_md = skill_dir / "SKILL.md"
    if src_md.exists():
        if not dry_run:
            dest_skill.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_md, dest_skill / "SKILL.md")
        n += 1

    # subpastas scripts/ e references/
    for sub in ("scripts", "references"):
        src_sub = skill_dir / sub
        if not src_sub.is_dir():
            continue
        dest_sub = dest_skill / sub
        for f in src_sub.rglob("*"):
            if f.is_dir():
                continue
            if f.name == "__pycache__" or f.suffix == ".pyc":
                continue
            if f.suffix in EXTS:
                if not dry_run:
                    dest_sub.mkdir(parents=True, exist_ok=True)
                    rel = f.relative_to(src_sub)
                    shutil.copy2(f, dest_sub / rel)
                n += 1
    return n


def main():
    ap = argparse.ArgumentParser(description="Sincroniza skills para hermes_mpt_ops/skills")
    ap.add_argument("--dry-run", action="store_true", help="Mostra o que seria copiado sem copiar")
    args = ap.parse_args()

    if not SKILLS_SRC.is_dir():
        sys.exit(f"❌ Pasta de skills não encontrada: {SKILLS_SRC}")
    SKILLS_DEST.mkdir(parents=True, exist_ok=True)

    total = 0
    skills = list(iterar_skills())
    print(f"Skills locais ativas: {len(skills)}")

    for skill in skills:
        n = copiar_skill(skill, args.dry_run)
        total += n
        acao = "[DRY]" if args.dry_run else "[OK ]"
        print(f"  {acao} {skill.name}: {n} arquivos")

    print(f"\n{'DRY-RUN — ' if args.dry_run else ''}Total: {total} arquivos em {SKILLS_DEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
