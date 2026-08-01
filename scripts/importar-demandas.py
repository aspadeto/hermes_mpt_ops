#!/usr/bin/env python3
"""
Importa demandas orçamentárias do SGA (HTML) para o banco SQLite.
Uso: python3 scripts/importar-demandas.py
      python3 scripts/importar-demandas.py --arquivo raw/articles/demandas-orcamento-regional-2026-todas.html.md
"""

import sqlite3
import re
import sys
import os

OPS_PATH = os.environ.get('OPS_PATH', '/opt/data/hermes-data/hermes_mpt_ops')
KB_PATH = os.environ.get('KB_PATH', '/opt/data/hermes-data/hermes_mpt_kb')
DB_PATH = os.path.join(OPS_PATH, 'data', 'regional-orcamento.db')

def extrair_demandas(html_path):
    """Extrai demandas do arquivo HTML do SGA."""
    with open(html_path, 'r') as f:
        html = f.read()
    
    rows = re.findall(r'<tr>(.*?)</tr>', html, re.DOTALL)
    demandas = []
    
    for row in rows[1:]:
        cells = re.findall(r'<td>(.*?)</td>', row, re.DOTALL)
        clean = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
        if len(clean) < 14:
            continue
        
        val_str = clean[12].replace('.', '').replace(',', '.')
        try:
            valor = float(val_str) if val_str else 0.0
        except ValueError:
            valor = 0.0
        
        demandas.append({
            'id_sga': int(clean[0]) if clean[0].isdigit() else None,
            'exercicio': int(clean[1]) if clean[1].isdigit() else 2026,
            'unidade': clean[2],
            'unidade_planejamento': clean[3],
            'descricao': clean[4].replace('\n', ' ').strip(),
            'categoria': clean[5],
            'subcategoria': clean[6],
            'prioridade': int(clean[7]) if clean[7].isdigit() else None,
            'necessita_contratacao': 'Sim' in clean[8],
            'evento': clean[9],
            'usuario': clean[10],
            'data_evento': clean[11],
            'valor': valor,
            'inativada': clean[13]
        })
    
    return demandas


def criar_banco():
    """Cria o banco e as tabelas."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS demandas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_sga INTEGER UNIQUE,
            exercicio INTEGER NOT NULL,
            unidade TEXT,
            unidade_planejamento TEXT,
            descricao TEXT,
            categoria TEXT,
            subcategoria TEXT,
            prioridade INTEGER,
            necessita_contratacao INTEGER DEFAULT 0,
            evento TEXT,
            usuario TEXT,
            data_evento TEXT,
            valor REAL,
            inativada TEXT
        );

        CREATE TABLE IF NOT EXISTS execucao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            demanda_id INTEGER NOT NULL,
            mes INTEGER,
            ano INTEGER,
            valor_empenhado REAL DEFAULT 0,
            valor_liquidado REAL DEFAULT 0,
            valor_pago REAL DEFAULT 0,
            observacao TEXT,
            FOREIGN KEY (demanda_id) REFERENCES demandas(id)
        );

        CREATE INDEX IF NOT EXISTS idx_demanda_unidade ON demandas(unidade_planejamento);
        CREATE INDEX IF NOT EXISTS idx_demanda_categoria ON demandas(categoria);
        CREATE INDEX IF NOT EXISTS idx_demanda_exercicio ON demandas(exercicio);
    ''')
    
    conn.commit()
    return conn


def importar(conn, demandas):
    """Importa as demandas para o banco."""
    cursor = conn.cursor()
    inseridos = 0
    ignorados = 0
    
    for d in demandas:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO demandas
                (id_sga, exercicio, unidade, unidade_planejamento, descricao,
                 categoria, subcategoria, prioridade, necessita_contratacao,
                 evento, usuario, data_evento, valor, inativada)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                d['id_sga'], d['exercicio'], d['unidade'], d['unidade_planejamento'],
                d['descricao'], d['categoria'], d['subcategoria'], d['prioridade'],
                1 if d['necessita_contratacao'] else 0,
                d['evento'], d['usuario'], d['data_evento'], d['valor'], d['inativada']
            ))
            if cursor.rowcount > 0:
                inseridos += 1
            else:
                ignorados += 1
        except Exception as e:
            print(f"  ERRO: {e}")
            ignorados += 1
    
    conn.commit()
    return inseridos, ignorados


def main():
    # Caminho do arquivo HTML
    args = sys.argv[1:]
    html_path = None
    
    for i, arg in enumerate(args):
        if arg == '--arquivo' and i + 1 < len(args):
            html_path = args[i + 1]
    
    if not html_path:
        html_path = os.path.join(KB_PATH, 'raw', 'articles',
                                 'demandas-orcamento-regional-2026-todas.html.md')
    
    if not os.path.exists(html_path):
        print(f"ERRO: Arquivo não encontrado: {html_path}")
        sys.exit(1)
    
    print(f"Extraindo demandas de: {html_path}")
    demandas = extrair_demandas(html_path)
    print(f"Encontradas: {len(demandas)} demandas\n")
    
    print(f"Criando banco: {DB_PATH}")
    conn = criar_banco()
    
    print("Importando...")
    inseridos, ignorados = importar(conn, demandas)
    
    # Estatísticas
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(valor) FROM demandas")
    total, valor = cursor.fetchone()
    
    print(f"\nInseridos: {inseridos}")
    print(f"Ignorados (já existentes): {ignorados}")
    print(f"Total no banco: {total} demandas")
    print(f"Valor total: R$ {valor:,.2f}")
    
    conn.close()


if __name__ == '__main__':
    main()
