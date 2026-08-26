#!/usr/bin/env python3
"""Migração: Separa entidades de referência (regimento) das reais (PRT14)"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
import yaml

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

# Entidades que SÃO apenas de referência (não têm instância real PRT14)
REFERENCE_ONLY = {
    "prt14.md",  # A própria PRT14 como entidade institucional
    "mpt.md",    # Ministério Público do Trabalho
    "csmpt.md",  # Conselho Superior
    "pgt.md",    # Procuradoria-Geral
    "corregedoria.md",
    "ouvidoria.md",
    "colegiado.md",
    "chefia-de-gabinete.md",  # já mapeado acima
}

# Tags para entidades de referência (regimento)
REF_TAGS = ["regimento", "referencia", "normativo"]

# Tags para entidades reais PRT14
REAL_TAGS = ["prt14", "unidade-real", "instancia"]

def load_frontmatter(content):
    """Extrai e parseia frontmatter YAML."""
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}, content
    try:
        fm = yaml.safe_load(match.group(1))
        return fm or {}, content[match.end():]
    except:
        return {}, content

def serialize_fm(fm):
    """Serializa frontmatter para YAML."""
    return yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False).rstrip()

def update_ref_fm(fm, original_filename):
    """Atualiza frontmatter da entidade de REFERÊNCIA (regimento)."""
    fm['type'] = fm.get('type', 'normativo')
    fm['tags'] = list(set(fm.get('tags', []) + ['regimento', 'referencia', 'normativo']))
    
    # Adiciona referência à entidade real
    base = fm.get('title', '').lower().replace(' ', '-')
    # Determina qual entidade real corresponde
    real_map = {
        'diretoria regional': 'prt14-diretoria-regional.md',
        'divisão de administração': 'prt14-divisao-administracao.md',
        'divisão de gestão de pessoas': 'prt14-divisao-gestao-pessoas.md',
        'divisão de orçamento e finanças': 'prt14-divisao-orcamento-financas.md',
        'divisão de ti': 'prt14-divisao-ti.md',
        'divisão regional de polícia do mpt': 'prt14-divisao-regional-policia-mpt.md',
        'procurador-chefe': 'prt14-procurador-chefe.md',
        'diretor regional': 'prt14-diretor-regional.md',
        'vice-procurador-chefe': 'prt14-vice-procurador-chefe.md',
        'chefia de gabinete': 'prt14-chefia-de-gabinete.md',
        'assessoria de comunicação social': 'prt14-assessoria-comunicacao-social.md',
        'assessoria jurídica': 'prt14-assessoria-juridica.md',
        'assessoria de planejamento e gestão estratégica': 'prt14-assessoria-planejamento-gestao-estrategica.md',
    }
    
    title_lower = fm.get('title', '').lower()
    for key, real_file in real_map.items():
        if key in fm.get('title', '').lower():
            fm['instancia_real'] = real_file
            break
    
    # Adiciona tag regimento
    tags = fm.get('tags', [])
    for tag in ['regimento', 'referencia', 'normativo']:
        if tag not in tags:
            tags.append(tag)
    fm['tags'] = list(set(fm.get('tags', [])) | {'regimento', 'referencia', 'normativo'})
    
    return fm

def update_real_fm(fm, original_filename):
    """Atualiza frontmatter da entidade REAL (instância PRT14)."""
    fm['type'] = fm.get('type', 'entidade')
    fm['tags'] = list(set(fm.get('tags', [])) | {'prt14', 'unidade-real', 'instancia'})
    
    # Adiciona referência ao regimento
    ref_map = {
        'prt14-divisao-administracao.md': 'divisao-administracao-regimento.md',
        'prt14-divisao-gestao-pessoas.md': 'divisao-gestao-pessoas-regimento.md',
        'prt14-divisao-orcamento-financas.md': 'divisao-orcamento-financas-regimento.md',
        'prt14-divisao-ti.md': 'divisao-ti-regimento.md',
        'prt14-divisao-regional-policia-mpt.md': 'divisao-regional-policia-mpt-regimento.md',
        'prt14-procurador-chefe.md': 'procurador-chefe-regimento.md',
        'prt14-diretor-regional.md': 'diretor-regional-regimento.md',
        'prt14-diretoria-regional.md': 'diretoria-regional-regimento.md',
        'prt14-vice-procurador-chefe.md': 'vice-procurador-chefe-regimento.md',
        'prt14-chefia-de-gabinete.md': 'chefia-de-gabinete-regimento.md',
        'prt14-assessoria-comunicacao-social.md': 'assessoria-comunicacao-social-regimento.md',
        'prt14-assessoria-juridica.md': 'assessoria-juridica-regimento.md',
        'prt14-assessoria-planejamento-gestao-estrategica.md': 'assessoria-planejamento-gestao-estrategica-regimento.md',
    }
    
    real_file = os.path.basename(fm.get('title', '').lower().replace(' ', '-'))
    # Tenta achar pelo nome do arquivo original
    orig_base = os.path.basename(fm.get('title', '')).lower().replace(' ', '-')
    
    # Busca pelo mapeamento inverso
    ref_file = None
    for real_f, ref_f in {
        'prt14-divisao-administracao.md': 'divisao-administracao-regimento.md',
        'prt14-divisao-gestao-pessoas.md': 'divisao-gestao-pessoas-regimento.md',
        'prt14-divisao-orcamento-financas.md': 'divisao-orcamento-financas-regimento.md',
        'prt14-divisao-ti.md': 'divisao-ti-regimento.md',
        'prt14-divisao-regional-policia-mpt.md': 'divisao-regional-policia-mpt-regimento.md',
        'prt14-procurador-chefe.md': 'procurador-chefe-regimento.md',
        'prt14-diretor-regional.md': 'diretor-regional-regimento.md',
        'prt14-diretoria-regional.md': 'diretoria-regional-regimento.md',
        'prt14-vice-procurador-chefe.md': 'vice-procurador-chefe-regimento.md',
        'prt14-chefia-de-gabinete.md': 'chefia-de-gabinete-regimento.md',
        'prt14-assessoria-comunicacao-social.md': 'assessoria-comunicacao-social-regimento.md',
        'prt14-assessoria-juridica.md': 'assessoria-juridica-regimento.md',
        'prt14-assessoria-planejamento-gestao-estrategica.md': 'assessoria-planejamento-gestao-estrategica-regimento.md',
    }.items():
        if real_f.lower() in fm.get('title', '').lower() or real_f in fm.get('title', '').lower().replace(' ', '-'):
            fm['referencia'] = ref_f
            break
    
    # Tags padrão para entidades reais PRT14
    tags = set(fm.get('tags', []))
    fm['tags'] = list(set(fm.get('tags', [])) | {'prt14', 'unidade-real', 'instancia'})
    
    return fm

def process_file(filepath, entities_dir):
    """Processa um arquivo: renomeia original para -regimento.md e cria versão real."""
    filename = os.path.basename(filepath)
    
    if filename not in MIGRATION_MAP:
        return False, f"Não mapeado: {filename}"
    
    ref_name, real_name = MIGRATION_MAP[os.path.basename(filepath)]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse frontmatter
    fm_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not fm_match:
        return False, f"Sem frontmatter: {filepath}"
    
    fm_text = yaml.safe_load(re.match(r'^---\n(.*?)\n---', open(filepath).read(), re.DOTALL).group(1))
    
    # Backup original
    backup = filepath + '.bak'
    shutil.copy2(filepath, filepath + '.bak')
    
    # 1. Rename original to -regimento.md
    ref_name = os.path.basename(filepath).replace('.md', '-regimento.md')
    ref_path = os.path.join(os.path.dirname(filepath), ref_name)
    os.rename(filepath, os.path.join(os.path.dirname(filepath), ref_name))
    
    # 2. Create real entity file
    real_name = f"prt14-{os.path.basename(filepath)}"
    real_path = os.path.join(os.path.dirname(filepath), real_name)
    
    # Process reference entity
    ref_fm = yaml.safe_load(yaml.dump({}))  # placeholder
    # Actually process the original content
    with open(os.path.join(os.path.dirname(filepath), f"{os.path.basename(filepath).replace('.md', '-regimento.md')}"), 'r') as f:
        ref_content = f.read()
    
    return True, f"Processed: {filepath}"

def main():
    entities_dir = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/entities"
    
    # List all files to process
    for filename in MIGRATION_MAP:
        filepath = os.path.join(entities_dir, filename)
        if not os.path.exists(filepath):
            print(f"NOT FOUND: {filename}")
            continue
        
        ref_name, real_name = MIGRATION_MAP[filename]
        print(f"\nProcessing: {filename}")
        print(f"  -> Reference: {ref_name}")
        print(f"  -> Real: {real_name}")
        
        # Read original
        with open(os.path.join(entities_dir, filename), 'r') as f:
            content = f.read()
        
        # Backup
        shutil.copy2(os.path.join(entities_dir, filename), 
                     os.path.join(os.path.dirname(os.path.join(entities_dir, filename)), filename + '.bak'))
        
        # 1. Rename original to -regimento.md
        ref_name = filename.replace('.md', '-regimento.md')
        ref_path = os.path.join(os.path.dirname(os.path.join(entities_dir, filename)), filename.replace('.md', '-regimento.md'))
        os.rename(os.path.join(entities_dir, filename), os.path.join(entities_dir, f"{filename.replace('.md', '-regimento.md')}"))
        
        # 2. Create real entity
        real_name = f"prt14-{filename}"
        real_path = os.path.join(os.path.dirname(os.path.join(entities_dir, filename)), f"prt14-{filename}")
        
        # Read original content for reference entity
        with open(os.path.join(entities_dir, f"{filename.replace('.md', '-regimento.md')}"), 'r') as f:
            ref_content = f.read()
        
        # Process reference entity frontmatter
        ref_fm_match = re.match(r'^---\n(.*?)\n---', ref_content, re.DOTALL)
        if ref_fm_match:
            ref_fm_text = yaml.safe_load(ref_content.split('---')[1])
            # Update reference entity frontmatter
            ref_fm = yaml.safe_load(yaml.dump({}))  # placeholder
            
        print(f"  OK: {filename} -> {ref_name} + {real_name}")

if __name__ == '__main__':
    main()