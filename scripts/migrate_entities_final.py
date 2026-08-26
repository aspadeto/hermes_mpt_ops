#!/usr/bin/env python3
"""Migração: Separa entidades de referência (regimento) das reais (PRT14)"""

import os
import re
import shutil
import yaml
from datetime import datetime

ENTITIES_DIR = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/entities"

# Mapeamento: arquivo atual -> (referencia, real)
MIGRATION_MAP = {
    "divisao-administracao.md": ("divisao-administracao-regimento.md", "prt14-divisao-administracao.md"),
    "divisao-gestao-pessoas.md": ("divisao-gestao-pessoas-regimento.md", "prt14-divisao-gestao-pessoas.md"),
    "divisao-orcamento-financas.md": ("divisao-orcamento-financas-regimento.md", "prt14-divisao-orcamento-financas.md"),
    "divisao-ti.md": ("divisao-ti-regimento.md", "prt14-divisao-ti.md"),
    "divisao-regional-policia-mpt.md": ("divisao-regional-policia-mpt-regimento.md", "prt14-divisao-regional-policia-mpt.md"),
    "procurador-chefe-prt14.md": ("procurador-chefe-regimento.md", "prt14-procurador-chefe.md"),
    "diretor-regional.md": ("diretor-regional-regimento.md", "prt14-diretor-regional.md"),
    "diretoria-regional.md": ("diretoria-regional-regimento.md", "prt14-diretoria-regional.md"),
    "vice-procurador-chefe.md": ("vice-procurador-chefe-regimento.md", "prt14-vice-procurador-chefe.md"),
    "chefia-de-gabinete.md": ("chefia-de-gabinete-regimento.md", "prt14-chefia-de-gabinete.md"),
    "assessoria-comunicacao-social.md": ("assessoria-comunicacao-social-regimento.md", "prt14-assessoria-comunicacao-social.md"),
    "assessoria-juridica.md": ("assessoria-juridica-regimento.md", "prt14-assessoria-juridica.md"),
    "assessoria-planejamento-gestao-estrategica.md": ("assessoria-planejamento-gestao-estrategica-regimento.md", "prt14-assessoria-planejamento-gestao-estrategica.md"),
}

ENTITIES_DIR = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/entities"

def main():
    for filename in sorted(MIGRATION_MAP.keys()):
        filepath = os.path.join(ENTITIES_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"NOT FOUND: {filename}")
            continue
        
        print(f"\nProcessing: {filename}")
        
        # Read original
        with open(os.path.join(ENTITIES_DIR, filename), 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse frontmatter
        fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not fm_match:
            print(f"  SKIP: No frontmatter")
            continue
        
        fm = yaml.safe_load(fm_match.group(1))
        if not fm:
            fm = {}
        
        # Backup
        shutil.copy2(os.path.join(ENTITIES_DIR, filename), 
                     os.path.join(ENTITIES_DIR, filename + '.bak'))
        
        ref_name, real_name = MIGRATION_MAP[filename]
        
        print(f"Processing: {filename}")
        print(f"  -> Ref: {filename.replace('.md', '-regimento.md')}")
        print(f"  -> Real: prt14-{filename}")
        
        # ==========================================
        # 1. RENAME ORIGINAL TO -regimento.md
        # ==========================================
        os.rename(
            os.path.join(ENTITIES_DIR, filename),
            os.path.join(ENTITIES_DIR, filename.replace('.md', '-regimento.md'))
        )
        
        # Read reference entity
        ref_path = os.path.join(ENTITIES_DIR, filename.replace('.md', '-regimento.md'))
        with open(ref_path, 'r', encoding='utf-8') as f:
            ref_content = f.read()
        
        # Parse reference frontmatter
        ref_fm_match = re.match(r'^---\n(.*?)\n---', open(ref_path).read(), re.DOTALL)
        ref_fm = yaml.safe_load(ref_fm_match.group(1)) if ref_fm_match else {}
        
        # Load original FM from backup
        with open(os.path.join(ENTITIES_DIR, filename + '.bak'), 'r') as f:
            orig_content = f.read()
        orig_fm_match = re.match(r'^---\n(.*?)\n---', open(os.path.join(ENTITIES_DIR, filename + '.bak')).read(), re.DOTALL)
        orig_fm = yaml.safe_load(orig_fm_match.group(1)) if orig_fm_match else {}
        
        # Build reference entity FM
        ref_fm = {
            'title': fm.get('title', ''),
            'created': fm.get('created', datetime.now().strftime('%Y-%m-%d')),
            'updated': datetime.now().strftime('%Y-%m-%d'),
            'type': 'normativo',
            'tags': sorted(set(fm.get('tags', [])) | {'regimento', 'referencia', 'normativo'}),
            'fontes': fm.get('fontes', []),
            'confianca': fm.get('confianca', 'alta'),
            'instancia_real': f"prt14-{os.path.basename(filepath).replace('.md', '.md')}",
        }
        
        # Write reference entity
        ref_content = f"""---
{yaml.dump(ref_fm, default_flow_style=False, allow_unicode=True, sort_keys=False)}---
"""
        with open(os.path.join(ENTITIES_DIR, os.path.basename(filename).replace('.md', '-regimento.md')), 'w') as f:
            f.write(ref_content)
        
        # ==========================================
        # 2. CREATE REAL ENTITY (PRT14)
        # ==========================================
        real_fm = {
            'title': f"PRT14 - {fm.get('title', '').replace(' (Regimento)', '').replace(' (Regimento)', '')}",
            'created': datetime.now().strftime('%Y-%m-%d'),
            'updated': datetime.now().strftime('%Y-%m-%d'),
            'type': 'entidade',
            'tags': ['prt14', 'unidade-real', 'instancia'],
            'referencia': f"{os.path.basename(filename).replace('.md', '-regimento.md')}",
            'fontes': [
                'raw/legislation/ria-mpt-599-2026-completo.txt',
                'raw/articles/organograma-prt14-2026.md'
            ],
            'confianca': 'alta'
        }
        
        # Inherit from original
        if 'title' in fm:
            real_fm['title'] = f"PRT14 - {fm.get('title', '').replace(' (Regimento)', '').replace(' (Regimento)', '')}"
        if 'fontes' in fm:
            real_fm['fontes'] = fm.get('fontes', [])
        
        real_fm['type'] = 'entidade'
        real_fm['referencia'] = f"{os.path.basename(filename).replace('.md', '-regimento.md')}"
        real_fm['fontes'] = [
            'raw/legislation/ria-mpt-599-2026-completo.txt',
            'raw/articles/organograma-prt14-2026.md'
        ]
        real_fm['confianca'] = 'alta'
        
        # Write real entity
        real_filename = f"prt14-{os.path.basename(filename)}"
        real_path = os.path.join(ENTITIES_DIR, f"prt14-{os.path.basename(filename)}")
        
        real_content = f"""---
{yaml.dump(real_fm, default_flow_style=False, allow_unicode=True, sort_keys=False)}---
"""
        with open(os.path.join(os.path.dirname(os.path.join(ENTITIES_DIR, filename)), f"prt14-{os.path.basename(filename)}"), 'w') as f:
            f.write(real_content)
        
        print(f"  OK: {os.path.basename(filename)} -> ref + real")

if __name__ == '__main__':
    main()