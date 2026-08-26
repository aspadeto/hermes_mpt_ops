#!/usr/bin/env python3
"""Corrige single words malformados no bs-234-2024.md"""

import os
import re

ENTITIES_DIR = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/entities"

SINGLE_WORDS = ['vice', 'procuradora', 'região', 'atribuições', 'legais', 'republ', 'servidores', 'listados']

def main():
    filepath = os.path.join(ENTITIES_DIR, "bs-234-2024.md")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Remove the Temas section with single words
    # Pattern: ## Temas\n\n[[word]], [[word]], ...
    content = re.sub(
        r'## Temas\n\n(?:\[\[[^\]]+\]\],?\s*)+\n',
        '## Temas\n\n',  # Empty temas section
        content
    )
    
    # Also remove any remaining single-word wikilinks anywhere
    for word in ['vice', 'procuradora', 'região', 'atribuições', 'legais', 'republ', 'servidores', 'listados']:
        pattern = r'\$\$' + re.escape(word) + r'\$\$'
        content = re.sub(pattern, '', content)
        content = re.sub(r'\[\[ *' + re.escape(word) + r' *\]\]', '', content)
    
    # Clean up extra commas and blank lines
    content = re.sub(r',\s*,', ',', content)
    content = re.sub(r',\s*\n', '\n', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("  Corrigido: bs-234-2024.md (removidos single words)")
    else:
        print("  Nenhuma alteração necessária")

if __name__ == '__main__':
    main()