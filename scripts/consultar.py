#!/usr/bin/env python3
"""
Script de consultas rápidas ao banco de dados orçamentário.
Uso: python3 scripts/consultar.py [opção]

Opções:
  unidades     - Resumo por unidade de planejamento
  categorias   - Resumo por categoria
  top10        - Maiores demandas em valor
  detalhe [id] - Detalhe de uma demanda específica
  export       - Exporta tudo em markdown
  execucao     - Resumo da execução orçamentária
  sql "SQL"    - Executa SQL livre (ex: 'SELECT * FROM demandas LIMIT 5')
"""

import sqlite3
import os
import sys

OPS_PATH = os.environ.get('OPS_PATH', '/opt/data/hermes-data/dr_mpt_ops')
DB_PATH = os.path.join(OPS_PATH, 'data', 'prt14.db')

def conectar():
    if not os.path.exists(DB_PATH):
        print(f"ERRO: Banco não encontrado em {DB_PATH}")
        print("Execute primeiro: python3 scripts/importar-demandas.py")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def query(sql, params=None):
    conn = conectar()
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    rows = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    conn.close()
    return colunas, rows

def formatar(valor):
    return f"R$ {valor:,.2f}" if isinstance(valor, (int, float)) else str(valor)

def cmd_unidades():
    cols, rows = query("""
        SELECT unidade_planejamento,
               COUNT(*) as qtd,
               SUM(valor) as total,
               ROUND(AVG(valor), 2) as media,
               MAX(valor) as maior
        FROM demandas
        GROUP BY unidade_planejamento
        ORDER BY total DESC
    """)
    print(f"{'Unidade':35s} {'Itens':>6s} {'Total':>15s} {'Média':>12s} {'Maior':>12s}")
    print("-" * 80)
    for r in rows:
        print(f"{r[0]:35s} {r[1]:6d} {formatar(r[2]):>15s} {formatar(r[3]):>12s} {formatar(r[4]):>12s}")

def cmd_categorias():
    cols, rows = query("""
        SELECT categoria, subcategoria,
               COUNT(*) as qtd,
               SUM(valor) as total
        FROM demandas
        GROUP BY categoria, subcategoria
        ORDER BY total DESC
    """)
    print(f"{'Categoria':30s} {'Subcategoria':35s} {'Itens':>6s} {'Total':>15s}")
    print("-" * 90)
    for r in rows:
        print(f"{r[0]:30s} {r[1]:35s} {r[2]:6d} {formatar(r[3]):>15s}")

def cmd_top10():
    cols, rows = query("""
        SELECT id, unidade_planejamento, descricao, valor, evento
        FROM demandas
        ORDER BY valor DESC
        LIMIT 10
    """)
    print(f"{'#':>4s} {'Unidade':25s} {'Descrição':50s} {'Valor':>15s}")
    print("-" * 96)
    for i, r in enumerate(rows, 1):
        desc = r[2][:47] + '...' if len(r[2]) > 50 else r[2]
        print(f"{i:4d} {r[1]:25s} {desc:50s} {formatar(r[3]):>15s}")

def cmd_detalhe(id_demanda):
    cols, rows = query("SELECT * FROM demandas WHERE id = ? OR id_sga = ?",
                        (id_demanda, id_demanda))
    if not rows:
        print(f"Demanda não encontrada: {id_demanda}")
        return
    for i, col in enumerate(cols):
        valor = rows[0][i]
        if col == 'valor':
            print(f"{col:25s}: R$ {valor:,.2f}")
        else:
            print(f"{col:25s}: {valor}")

def cmd_export():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT unidade_planejamento, categoria, subcategoria,
               descricao, valor, evento, usuario
        FROM demandas
        ORDER BY unidade_planejamento, valor DESC
    """)
    rows = cursor.fetchall()
    
    print("# Relatório de Demandas Orçamentárias — PRT14 2026\n")
    print("Fonte: `data/prt14.db` — SQLite\n")
    
    atual = None
    for r in rows:
        if r[0] != atual:
            atual = r[0]
            print(f"## {atual}\n")
        desc = r[3][:80]
        print(f"- {r[1]} / {r[2]} — **R$ {r[4]:,.2f}** — {desc}")
        print(f"  *{r[5]} — {r[6]}*\n")
    
    conn.close()

def cmd_execucao():
    cols, rows = query("""
        SELECT
            d.unidade_planejamento,
            COUNT(DISTINCT d.id) as demandas,
            COUNT(i.id) as itens,
            COALESCE(SUM(i.planejado), 0) as planejado,
            COALESCE(SUM(i.empenhado), 0) as empenhado,
            COALESCE(SUM(i.atestado_pago), 0) as pago
        FROM demandas d
        LEFT JOIN itens_demanda i ON d.id_sga = i.demanda_id
        GROUP BY d.unidade_planejamento
        ORDER BY planejado DESC
    """)
    print(f"{'Unidade':30s} {'Dem.':>5s} {'Itens':>5s} {'Planejado':>14s} {'Empenhado':>14s} {'Pago':>14s} {'% Exec':>7s}")
    print("-" * 91)
    for r in rows:
        exec_pct = f"{r[4]/r[3]*100:.0f}%" if r[3] > 0 else "-"
        print(f"{r[0]:30s} {r[1]:5d} {r[2]:5d} {formatar(r[3]):>14s} {formatar(r[4]):>14s} {formatar(r[5]):>14s} {exec_pct:>7s}")
    
    print()
    # Total geral
    total = query("SELECT SUM(planejado), SUM(empenhado), SUM(atestado_pago) FROM itens_demanda")
    p, e, a = total[1][0]
    print(f"Total planejado: R$ {p:,.2f}")
    print(f"Total empenhado: R$ {e:,.2f} ({e/p*100:.1f}%)" if p else "")
    print(f"Total pago:     R$ {a:,.2f} ({a/p*100:.1f}%)" if p else "")

def cmd_sql(sql_texto):
    try:
        cols, rows = query(sql_texto)
        print(f"Colunas: {', '.join(cols)}")
        print(f"Linhas: {len(rows)}\n")
        for r in rows:
            print(" | ".join(str(v) for v in r))
    except Exception as e:
        print(f"ERRO: {e}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    
    cmd = args[0]
    
    if cmd == 'unidades':
        cmd_unidades()
    elif cmd == 'categorias':
        cmd_categorias()
    elif cmd == 'top10':
        cmd_top10()
    elif cmd == 'detalhe' and len(args) > 1:
        cmd_detalhe(args[1])
    elif cmd == 'export':
        cmd_export()
    elif cmd == 'execucao':
        cmd_execucao()
    elif cmd == 'sql' and len(args) > 1:
        cmd_sql(' '.join(args[1:]))
    else:
        print(__doc__)


if __name__ == '__main__':
    main()
