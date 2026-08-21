#!/usr/bin/env python3
"""
Importa relatório de execução por item de demanda (ODS) para o SQLite.
Uso: python3 scripts/importar-execucao.py
"""

import sqlite3
import zipfile
import xml.etree.ElementTree as ET
import os
import re
from datetime import datetime
from pathlib import Path

# Importa configuração centralizada de caminhos
from ops_paths import OPS_PATH, KB_PATH, OPS_DATA

DB_PATH = OPS_DATA / "regional-orcamento.db"
ODS_DIR = KB_PATH / "raw" / "to-process"

def parse_valor(v):
    """Converte string brasileira R$ 1.234,56 para float."""
    if not v or v == 'None' or v.strip() == '':
        return 0.0
    v = v.strip().replace('R$', '').replace(' ', '')
    v = v.replace('.', '').replace(',', '.')
    try:
        return float(v)
    except:
        return 0.0

def extrair_ods(path):
    """Extrai dados de um arquivo ODS."""
    ns = {'table': 'urn:oasis:names:tc:opendocument:xmlns:table:1.0',
          'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0'}
    
    with zipfile.ZipFile(path, 'r') as z:
        content = z.read('content.xml')
        root = ET.fromstring(content)
        
        tables = root.findall('.//table:table', ns)
        items = []
        
        for table in tables:
            rows = table.findall('.//table:table-row', ns)
            for r_idx, row in enumerate(rows):
                cells = row.findall('.//table:table-cell', ns)
                vals = []
                for c in cells:
                    p = c.find('.//text:p', ns)
                    vals.append(p.text.strip() if p is not None and p.text else '')
                if any(v for v in vals):
                    items.append(vals)
        
        return items

def importar():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Adiciona colunas se não existirem
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS itens_demanda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demanda_id INTEGER,
            item TEXT,
            descricao_item TEXT,
            lotacao TEXT,
            planejado REAL DEFAULT 0,
            provisionado REAL DEFAULT 0,
            empenhado REAL DEFAULT 0,
            dif_planejado_empenhado REAL DEFAULT 0,
            atestado_pago REAL DEFAULT 0,
            dif_planejado_atestado REAL DEFAULT 0,
            FOREIGN KEY (demanda_id) REFERENCES demandas(id_sga)
        );
        
        CREATE TABLE IF NOT EXISTS itens_avulsos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empenho TEXT,
            item TEXT,
            descricao TEXT
        );
    ''')
    
    # Processar parte 1
    path1 = os.path.join(ODS_DIR,
        'Planejamento - Relatório de Execução por Item de Demanda - parte 1.ods')
    dados1 = extrair_ods(path1)
    
    inseridos = 0
    for row in dados1[1:]:  # Pula cabeçalho
        if len(row) < 11:
            continue
        
        demanda_id = row[0] if row[0].isdigit() else None
        if not demanda_id or demanda_id == 'None':
            continue
        
        cursor.execute('''
            INSERT OR REPLACE INTO itens_demanda
            (demanda_id, item, descricao_item, lotacao,
             planejado, provisionado, empenhado,
             dif_planejado_empenhado, atestado_pago, dif_planejado_atestado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            int(demanda_id),
            row[2] if len(row) > 2 else '',
            row[3] if len(row) > 3 else '',
            row[4] if len(row) > 4 else '',
            parse_valor(row[5]) if len(row) > 5 else 0,
            parse_valor(row[6]) if len(row) > 6 else 0,
            parse_valor(row[7]) if len(row) > 7 else 0,
            parse_valor(row[8]) if len(row) > 8 else 0,
            parse_valor(row[9]) if len(row) > 9 else 0,
            parse_valor(row[10]) if len(row) > 10 else 0,
        ))
        inseridos += 1
    
    # Processar parte 2 (itens avulsos)
    path2 = os.path.join(ODS_DIR,
        'Planejamento - Relatório de Execução por Item de Demanda - parte 2.ods')
    dados2 = extrair_ods(path2)
    
    avulsos = 0
    for row in dados2[2:]:  # Pula cabeçalho
        if len(row) < 3:
            continue
        cursor.execute('''
            INSERT INTO itens_avulsos (empenho, item, descricao)
            VALUES (?, ?, ?)
        ''', (row[0], row[1], ' | '.join(row[2:])))
        avulsos += 1
    
    conn.commit()
    
    # Estatísticas
    cursor.execute("SELECT COUNT(*), SUM(planejado), SUM(empenhado), SUM(atestado_pago) FROM itens_demanda")
    qtd, plan, emp, pago = cursor.fetchone()
    
    print(f"Itens de demanda importados: {inseridos}")
    print(f"Itens avulsos (sem demanda): {avulsos}")
    print(f"Total planejado: R$ {plan:,.2f}" if plan else "")
    print(f"Total empenhado: R$ {emp:,.2f}" if emp else "")
    print(f"Total atestado/pago: R$ {pago:,.2f}" if pago else "")
    
    if plan and plan > 0:
        print(f"Execução orçamentária: {emp/plan*100:.1f}% empenhado, {pago/plan*100:.1f}% pago")
    
    conn.close()

if __name__ == '__main__':
    importar()
