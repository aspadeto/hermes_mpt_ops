#!/usr/bin/env python3
"""Remove links quebrados para raw/boletins/*.pdf e boletins_docling/*.md das entidades de boletim."""

import os
import re

ENTITIES_DIR = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/entities"

# Pattern para boletins: bs-NNN-YYYY.md ou bs-NNN.N-YYYY.md
BOLETIM_PATTERN = re.compile(r'bs-\d+(?:\.\d+)?-\d{4}\.md$')

def main():
    removed_raw = 0
    removed_docling = 0
    processed = 0
    
    for filename in os.listdir(ENTITIES_DIR):
        if not BOLETIM_PATTERN.match(filename):
            continue
        
        filepath = os.path.join(ENTITIES_DIR, filename)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Remove [[raw/boletins/BS-*.pdf]]
        content = re.sub(r'\[\[raw/boletins/[^\]]+\]\]', '', content)
        
        # Remove [[boletins_docling/BS-*.md]]
        content = re.sub(r'\[\[boletins_docling/[^\]]+\]\]', '', content)
        
        # Clean up extra blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Count what was removed
            raw_count = len(re.findall(r'\[\[raw/boletins/[^\]]+\]\]', original))
            docling_count = len(re.findall(r'\[\[boletins_docling/[^\]]+\]\]', original))
            
            if raw_count > 0:
                removed_raw += raw_count
            if docling_count > 0:
                removed_docling += docling_count
            
            processed += 1
    
    print(f"Processados: {processed} boletins")
    print(f"Links raw/boletins removidos: {removed_raw}")
    print(f"Links boletins_docling removidos: {removed_docling}")
    print(f"Total links removidos: {removed_raw + removed_docling}")

if __name__ == '__main__':
    main()