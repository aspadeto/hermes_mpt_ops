#!/usr/bin/env python3
"""Adiciona wikilinks das entidades -regimento.md para as prt14-*.md correspondentes."""

import os
import re

ENTITIES_DIR = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/entities"

# Mapeamento: arquivo -regimento.md -> arquivo prt14-*.md
REGIMENTO_TO_REAL = {
    'divisao-administracao-regimento.md': 'prt14-divisao-administracao.md',
    'divisao-gestao-pessoas-regimento.md': 'prt14-divisao-gestao-pessoas.md',
    'divisao-orcamento-financas-regimento.md': 'prt14-divisao-orcamento-financas.md',
    'divisao-ti-regimento.md': 'prt14-divisao-ti.md',
    'divisao-regional-policia-mpt-regimento.md': 'prt14-divisao-regional-policia-mpt.md',
    'procurador-chefe-regimento.md': 'prt14-procurador-chefe.md',
    'diretor-regional-regimento.md': 'prt14-diretor-regional.md',
    'diretoria-regional-regimento.md': 'prt14-diretoria-regional.md',
    'vice-procurador-chefe-regimento.md': 'prt14-vice-procurador-chefe.md',
    'chefia-de-gabinete-regimento.md': 'prt14-chefia-de-gabinete.md',
    'assessoria-comunicacao-social-regimento.md': 'prt14-assessoria-comunicacao-social.md',
    'assessoria-juridica-regimento.md': 'prt14-assessoria-juridica.md',
    'assessoria-planejamento-gestao-estrategica-regimento.md': 'prt14-assessoria-planejamento-gestao-estrategica.md',
}

def main():
    added = 0
    
    for ref_file, real_file in REGIMENTO_TO_REAL.items():
        ref_path = os.path.join(ENTITIES_DIR, ref_file)
        real_path = os.path.join(ENTITIES_DIR, real_file)
        
        if not os.path.exists(ref_path):
            print(f"REF NOT FOUND: {ref_file}")
            continue
        if not os.path.exists(real_path):
            print(f"REAL NOT FOUND: {real_file}")
            continue
        
        # Read reference entity
        with open(ref_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if wikilink already exists
        wikilink = f"[[{real_file.replace('.md', '')}]]"
        if wikilink in content:
            print(f"  Already has link: {ref_file} -> {real_file}")
            continue
        
        # Add wikilink at the end of file (before any trailing whitespace)
        link_text = f"\n\n---\n\n**Instância real:** {wikilink}"
        new_content = content.rstrip() + link_text + "\n"
        
        with open(ref_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        added += 1
        print(f"  Added: {ref_file} -> {real_file}")
    
    print(f"\nTotal wikilinks adicionados: {added}")

if __name__ == '__main__':
    main()