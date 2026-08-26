#!/usr/bin/env python3
"""Cria páginas prt-N.md para as 24 regionais."""

import os
import yaml
from datetime import datetime

ENTITIES_DIR = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/entities"

# Regionais PRT-1 a PRT-24
# Dados básicos: nome, sede, estados
REGIONALS = {
    1: {"nome": "PRT-1", "sede": "Brasília, DF", "estados": ["DF", "GO", "TO"]},
    2: {"nome": "PRT-2", "sede": "Salvador, BA", "estados": ["BA", "SE"]},
    3: {"nome": "PRT-3", "sede": "Recife, PE", "estados": ["PE", "PB", "RN", "AL"]},
    4: {"nome": "PRT-4", "sede": "Belém, PA", "estados": ["PA", "AP", "MA"]},
    5: {"nome": "PRT-5", "sede": "São Paulo, SP", "estados": ["SP", "MS"]},
    6: {"nome": "PRT-6", "sede": "Belo Horizonte, MG", "estados": ["MG"]},
    7: {"nome": "PRT-7", "sede": "Porto Alegre, RS", "estados": ["RS", "SC"]},
    8: {"nome": "PRT-8", "sede": "Curitiba, PR", "estados": ["PR"]},
    9: {"nome": "PRT-9", "sede": "Manaus, AM", "estados": ["AM", "RR", "AC", "RO"]},
    10: {"nome": "PRT-10", "sede": "Rio de Janeiro, RJ", "estados": ["RJ", "ES"]},
    11: {"nome": "PRT-11", "sede": "Fortaleza, CE", "estados": ["CE", "PI"]},
    12: {"nome": "PRT-12", "sede": "São Luís, MA", "estados": ["MA"]},
    13: {"nome": "PRT-13", "sede": "Florianópolis, SC", "estados": ["SC"]},
    14: {"nome": "PRT-14", "sede": "Porto Velho, RO", "estados": ["RO", "AC"]},
    15: {"nome": "PRT-15", "sede": "Campo Grande, MS", "estados": ["MS"]},
    16: {"nome": "PRT-16", "sede": "Cuiabá, MT", "estados": ["MT"]},
    17: {"nome": "PRT-17", "sede": "Teresina, PI", "estados": ["PI"]},
    18: {"nome": "PRT-18", "sede": "João Pessoa, PB", "estados": ["PB"]},
    19: {"nome": "PRT-19", "sede": "Aracaju, SE", "estados": ["SE"]},
    20: {"nome": "PRT-20", "sede": "Maceió, AL", "estados": ["AL"]},
    21: {"nome": "PRT-21", "sede": "Natal, RN", "estados": ["RN"]},
    22: {"nome": "PRT-22", "sede": "Palmas, TO", "estados": ["TO"]},
    23: {"nome": "PRT-23", "sede": "Rio Branco, AC", "estados": ["AC"]},
    24: {"nome": "PRT-24", "sede": "Boa Vista, RR", "estados": ["RR"]},
}

def main():
    created = 0
    for num, info in REGIONALS.items():
        filename = f"prt-{num}.md"
        filepath = os.path.join(ENTITIES_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"  Existe: {filename}")
            continue
        
        fm = {
            'title': f"Procuradoria Regional do Trabalho da {num}ª Região ({info['nome']})",
            'created': datetime.now().strftime('%Y-%m-%d'),
            'updated': datetime.now().strftime('%Y-%m-%d'),
            'type': 'entidade',
            'tags': ['prt', f'prt-{num}', 'regional', 'institucional'],
            'fontes': [
                'raw/legislation/ria-mpt-599-2026-completo.txt',
                'raw/articles/organograma-prt14-2026.md'
            ],
            'confianca': 'alta',
            'regiao': info['estados'],
            'sede': info['sede'],
        }
        
        content = f"""---
{yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)}---
# {info['nome']} - {info['sede']}

Procuradoria Regional do Trabalho da **{num}ª Região**.

## Jurisdição
Estados: {', '.join(info['estados'])}

## Sede
{info['sede']}

## Referência Normativa
- [[ria-mpt-599-2026]] — Regimento Interno Administrativo (arts. 439-440)

## Ver também
- [[prt14]] — PRT-14 (exemplo de estrutura)
- [[divisao-administracao-regimento]] — Estrutura administrativa padrão
"""
        
        filepath = os.path.join(ENTITIES_DIR, f"prt-{num}.md")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Criado: prt-{num}.md")

if __name__ == '__main__':
    main()