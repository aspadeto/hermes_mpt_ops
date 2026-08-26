#!/usr/bin/env python3
"""Migração: Separa entidades de referência (regimento) das reais (PRT14)"""

import os
import re
import shutil
import yaml
from pathlib import Path

WIKI = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb"
ENTITIES_DIR = os.path.join(WIKI, "entities")

# Mapeamento: arquivo atual -> (referencia, real)
MIGRATION_MAP = {
    # Divisões principais
    "divisao-administracao.md": (
        "divisao-administracao-regimento.md",
        "prt14-divisao-administracao.md"
    ),
    "divisao-gestao-pessoas.md": (
        "divisao-gestao-pessoas-regimento.md",
        "prt14-divisao-gestao-pessoas.md"
    ),
    "divisao-orcamento-financas.md": (
        "divisao-orcamento-financas-regimento.md",
        "prt14-divisao-orcamento-financas.md"
    ),
    "divisao-ti.md": (
        "divisao-ti-regimento.md",
        "prt14-divisao-ti.md"
    ),
    "divisao-regional-policia-mpt.md": (
        "divisao-regional-policia-mpt-regimento.md",
        "prt14-divisao-regional-policia-mpt.md"
    ),
    # Cargos/Entidades
    "procurador-chefe-prt14.md": (
        "procurador-chefe-regimento.md",
        "prt14-procurador-chefe.md"
    ),
    "diretor-regional.md": (
        "diretor-regional-regimento.md",
        "prt14-diretor-regional.md"
    ),
    "diretoria-regional.md": (
        "diretoria-regional-regimento.md",
        "prt14-diretoria-regional.md"
    ),
    "vice-procurador-chefe.md": (
        "vice-procurador-chefe-regimento.md",
        "prt14-vice-procurador-chefe.md"
    ),
    "chefia-de-gabinete.md": (
        "chefia-de-gabinete-regimento.md",
        "prt14-chefia-de-gabinete.md"
    ),
    "assessoria-comunicacao-social.md": (
        "assessoria-comunicacao-social-regimento.md",
        "prt14-assessoria-comunicacao-social.md"
    ),
    "assessoria-juridica.md": (
        "assessoria-juridica-regimento.md",
        "prt14-assessoria-juridica.md"
    ),
    "assessoria-planejamento-gestao-estrategica.md": (
        "assessoria-planejamento-gestao-estrategica-regimento.md",
        "prt14-assessoria-planejamento-gestao-estrategica.md"
    ),
}

ENTITIES_DIR = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/entities"

def process_file(filename):
    """Processa um arquivo: renomeia para -regimento.md e cria versão real PRT14."""
    filepath = os.path.join(ENTITIES_DIR, filename)
    
    if not os.path.exists(filepath):
        return False, f"NOT FOUND: {filename}"
    
    ref_name, real_name = MIGRATION_MAP[os.path.basename(filepath)]
    
    # Read original content
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return False, f"Sem frontmatter"
    
    fm_text = fm_match.group(1)
    try:
        fm = yaml.safe_load(fm_match.group(1))
        if fm is None:
            fm = {}
    except:
        return False, "Erro YAML"
    
    # Backup original
    shutil.copy2(os.path.join(ENTITIES_DIR, filename), 
                 os.path.join(ENTITIES_DIR, filename + '.bak'))
    
    # Load original FM
    fm = yaml.safe_load(re.match(r'^---\n(.*?)\n---', open(os.path.join(ENTITIES_DIR, filename)).read(), re.DOTALL).group(1))
    
    # ==========================================
    # 1. CREATE REFERENCE ENTITY (regimento)
    # ==========================================
    ref_fm = dict(fm)  # copy
    
    # Update reference entity frontmatter
    ref_fm['type'] = 'normativo'  # tipo de referência
    tags = set(fm.get('tags', []))
    ref_tags = tags | {'regimento', 'referencia', 'normativo'}
    ref_fm['tags'] = sorted(ref_tags)
    
    # Add reference to real entity
    ref_fm['instancia_real'] = f"prt14-{os.path.basename(filepath)}"
    ref_fm['referencia_para'] = f"prt14-{os.path.basename(filepath)}"
    
    # Add tags
    ref_fm['tags'] = sorted(set(fm.get('tags', [])) | {'regimento', 'referencia', 'normativo'})
    
    # Update content for reference entity
    ref_content = re.sub(
        r'^---\n.*?\n---',
        '---\n' + yaml.dump(ref_fm, default_flow_style=False, allow_unicode=True, sort_keys=False).rstrip() + '\n---',
        open(os.path.join(ENTITIES_DIR, filename)).read(),
        count=1,
        flags=re.DOTALL
    )
    
    # Write reference entity (-regimento.md)
    ref_filename = filename.replace('.md', '-regimento.md')
    ref_path = os.path.join(os.path.dirname(os.path.join(ENTITIES_DIR, os.path.basename(filepath))), 
                           os.path.basename(filename).replace('.md', '-regimento.md'))
    
    # Rename original to -regimento.md
    original_path = os.path.join(ENTITIES_DIR, filename)
    ref_path = os.path.join(os.path.dirname(os.path.join(ENTITIES_DIR, os.path.basename(filename))), 
                           filename.replace('.md', '-regimento.md'))
    
    shutil.move(
        os.path.join(ENTITIES_DIR, filename),
        os.path.join(os.path.dirname(os.path.join(ENTITIES_DIR, filename)), 
                     filename.replace('.md', '-regimento.md'))
    )
    
    # ==========================================
    # 2. CREATE REAL ENTITY (PRT14)
    # ==========================================
    real_fm = dict(fm)  # copy
    
    # Update real entity frontmatter
    real_fm['type'] = 'entidade'
    real_tags = set(fm.get('tags', []))
    real_tags.update({'prt14', 'unidade-real', 'instancia'})
    real_fm['tags'] = sorted(real_tags)
    
    # Add reference to regimento
    real_fm['referencia'] = filename.replace('.md', '-regimento.md')
    
    # Add real entity tags
    real_fm['tags'] = sorted(set(fm.get('tags', [])) | {'prt14', 'unidade-real', 'instancia'})
    
    # Add real entity specific fields
    real_fm['referencia'] = os.path.basename(os.path.join(os.path.dirname(os.path.join(ENTITIES_DIR, filename)), 
                                                      filename.replace('.md', '-regimento.md')))
    
    # Write real entity
    real_filename = f"prt14-{os.path.basename(filepath)}"
    real_path = os.path.join(ENTITIES_DIR, os.path.basename(filepath).replace('.md', '-real.md'))
    # Actually, we want prt14- prefix
    real_filename = f"prt14-{os.path.basename(filepath)}"
    real_path = os.path.join(os.path.dirname(filepath), f"prt14-{os.path.basename(filename)}")
    
    # Create real entity content
    real_fm = {
        'title': fm.get('title', '').replace(' (Regimento)', '').replace(' (Regimento)', ''),
        'created': datetime.now().strftime('%Y-%m-%d'),
        'updated': datetime.now().strftime('%Y-%m-%d'),
        'type': 'entidade',
        'tags': sorted(set(fm.get('tags', [])) | {'prt14', 'unidade-real', 'instancia'}),
        'referencia': os.path.basename(filepath).replace('.md', '-regimento.md'),
        'fontes': [
            f"raw/legislation/ria-mpt-599-2026-completo.txt",
            f"raw/articles/organograma-prt14-2026.md"
        ],
        'confianca': 'alta'
    }
    
    # Write real entity file
    real_filename = f"prt14-{os.path.basename(filepath)}"
    real_path = os.path.join(ENTITIES_DIR, f"prt14-{os.path.basename(filename)}")
    
    return True, f"Processed: {os.path.basename(filepath)}"

def main():
    entities_dir = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/entities"
    
    for filename in MIGRATION_MAP:
        filepath = os.path.join(ENTITIES_DIR, filename)
        if not os.path.exists(filepath):
            print(f"NOT FOUND: {filename}")
            continue
        
        print(f"Processing: {filename}")
        
        # Read original
        with open(os.path.join(entities_dir, filename), 'r') as f:
            content = f.read()
        
        # Backup
        shutil.copy2(os.path.join(entities_dir, filename), 
                     os.path.join(entities_dir, filename + '.bak'))
        
        # 1. Rename original to -regimento.md
        ref_name = filename.replace('.md', '-regimento.md')
        os.rename(
            os.path.join(entities_dir, filename),
            os.path.join(entities_dir, filename.replace('.md', '-regimento.md'))
        )
        
        # Read the reference entity we just created
        ref_path = os.path.join(entities_dir, filename.replace('.md', '-regimento.md'))
        with open(ref_path, 'r') as f:
            ref_content = f.read()
        
        # Update reference entity frontmatter
        ref_fm_match = re.match(r'^---\n(.*?)\n---', open(ref_path).read(), re.DOTALL)
        if ref_fm_match:
            ref_fm = yaml.safe_load(ref_fm_match.group(1))
            ref_fm['type'] = 'normativo'
            ref_fm['tags'] = sorted(set(ref_fm.get('tags', [])) | {'regimento', 'referencia', 'normativo'})
            ref_fm['instancia_real'] = f"prt14-{os.path.basename(ref_path).replace('-regimento.md', '')}"
            
            # Update reference file
            ref_content = re.sub(r'^---\n.*?\n---', 
                               '---\n' + yaml.dump(yaml.safe_load(ref_content.split('---')[1]), default_flow_style=False, allow_unicode=True).rstrip() + '\n---',
                               open(ref_path).read(), count=1, flags=re.DOTALL)
            with open(ref_path, 'w') as f:
                f.write(ref_content)
        
        # Create real entity
        real_fm = {
            'title': f"PRT14 - {ref_fm.get('title', '').replace(' (Regimento)', '')}",
            'created': datetime.now().strftime('%Y-%m-%d'),
            'updated': datetime.now().strftime('%Y-%m-%d'),
            'type': 'entidade',
            'tags': ['prt14', 'unidade-real', 'instancia'],
            'referencia': f"{os.path.basename(ref_path)}",
            'fontes': [
                'raw/legislation/ria-mpt-599-2026-completo.txt',
                'raw/articles/organograma-prt14-2026.md'
            ],
            'confianca': 'alta'
        }
        
        real_filename = f"prt14-{os.path.basename(ref_path).replace('-regimento.md', '.md')}"
        real_path = os.path.join(os.path.dirname(ref_path), f"prt14-{os.path.basename(ref_path).replace('-regimento.md', '.md')}")
        
        real_content = f"""---
{yaml.dump({
    'title': f"PRT14 - {ref_fm.get('title', '')}",
    'created': datetime.now().strftime('%Y-%m-%d'),
    'updated': datetime.now().strftime('%Y-%m-%d'),
    'type': 'entidade',
    'tags': ['prt14', 'unidade-real', 'instancia'],
    'referencia': f"{os.path.basename(ref_path)}",
    'fontes': [
        'raw/legislation/ria-mpt-599-2026-completo.txt',
        'raw/articles/organograma-prt14-2026.md'
    ],
    'confianca': 'alta'
}, default_flow_style=False, allow_unicode=True, sort_keys=False)}---
"""
        with open(os.path.join(os.path.dirname(ref_path), f"prt14-{os.path.basename(ref_path).replace('-regimento.md', '.md')}"), 'w') as f:
            f.write(real_content)
        
        print(f"  OK: {os.path.basename(filepath)} -> ref + real")

if __name__ == '__main__':
    main()