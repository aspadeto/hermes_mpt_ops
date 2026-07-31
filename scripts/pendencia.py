#!/usr/bin/env python3
"""
pendencia.py — Sistema de pendências (TODO) para o fluxo de trabalho Hermes ↔ Usuário.

Fluxo:
  1. HAL adiciona pendências quando algo precisa de confirmação do usuário
     (ex: indexação de artigo, revisão de despacho, decisão de processo).
  2. Lembretes automáticos (cron, até 3x/dia) chamam `remind`.
     Se não houver pendências ativas → stdout vazio (cron silencioso).
     Se houver → mensagem de lembrete para o usuário.
  3. Quando o usuário está disponível, HAL apresenta as pendências
     uma a uma e as resolve com `resolve <id>`.

Banco: SQLite em /opt/data/hermes-data/dr_mpt_ops/data/pendencias.db (persistente, fora do git).

Uso:
  pendencia.py add --titulo "..." [--contexto "caminho/doc"] [--tipo confirmacao|decisao|revisao|outro] [--prioridade alta|media|baixa]
  pendencia.py list                     # pendências ativas
  pendencia.py list --todas             # todas (ativas + resolvidas + canceladas)
  pendencia.py resolve <id>             # marca como resolvida
  pendencia.py cancel <id>              # cancela
  pendencia.py remind                   # mensagem de lembrete (para cron)
  pendencia.py stats                    # resumo rápido
"""

import argparse
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("/opt/data/hermes-data/dr_mpt_ops/data/pendencias.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS pendencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    contexto TEXT DEFAULT '',
    tipo TEXT DEFAULT 'outro',        -- confirmacao | decisao | revisao | outro
    prioridade TEXT DEFAULT 'media',  -- alta | media | baixa
    status TEXT DEFAULT 'pendente',   -- pendente | resolvida | cancelada
    criada_em TEXT NOT NULL,
    resolvida_em TEXT
);
"""


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(SCHEMA)
    return conn


def agora():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def cmd_add(args):
    conn = conectar()
    cur = conn.execute(
        "INSERT INTO pendencias (titulo, contexto, tipo, prioridade, criada_em) VALUES (?, ?, ?, ?, ?)",
        (args.titulo, args.contexto or "", args.tipo, args.prioridade, agora()),
    )
    conn.commit()
    print(f"✅ Pendência #{cur.lastrowid} criada: {args.titulo}")
    conn.close()


def cmd_list(args):
    conn = conectar()
    if args.todas:
        rows = conn.execute("SELECT * FROM pendencias ORDER BY status, id").fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM pendencias WHERE status='pendente' ORDER BY id"
        ).fetchall()
    conn.close()

    if not rows:
        print("📭 Nenhuma pendência ativa.")
        return

    for r in rows:
        pid, titulo, ctx, tipo, prio, status, criada, resolvida = r
        icone = {"pendente": "⏳", "resolvida": "✅", "cancelada": "🚫"}[status]
        prio_icon = {"alta": "🔴", "media": "🟡", "baixa": "🟢"}.get(prio, "⚪")
        print(f"{icone} #{pid} [{prio_icon}{prio}] ({tipo}) {titulo}")
        if ctx:
            print(f"     📎 {ctx}")
        print(f"     🕐 criada: {criada}")


def cmd_resolve(args):
    conn = conectar()
    cur = conn.execute(
        "UPDATE pendencias SET status='resolvida', resolvida_em=? WHERE id=? AND status='pendente'",
        (agora(), args.id),
    )
    conn.commit()
    if cur.rowcount:
        print(f"✅ Pendência #{args.id} marcada como resolvida.")
    else:
        print(f"⚠️  Pendência #{args.id} não encontrada ou já resolvida.")
    conn.close()


def cmd_cancel(args):
    conn = conectar()
    cur = conn.execute(
        "UPDATE pendencias SET status='cancelada', resolvida_em=? WHERE id=? AND status='pendente'",
        (agora(), args.id),
    )
    conn.commit()
    if cur.rowcount:
        print(f"🚫 Pendência #{args.id} cancelada.")
    else:
        print(f"⚠️  Pendência #{args.id} não encontrada ou já encerrada.")
    conn.close()


def cmd_remind(args):
    """Gera mensagem de lembrete. Saída vazia = nada pendente (cron silencioso)."""
    conn = conectar()
    rows = conn.execute(
        "SELECT * FROM pendencias WHERE status='pendente' ORDER BY "
        "CASE prioridade WHEN 'alta' THEN 1 WHEN 'media' THEN 2 ELSE 3 END, id"
    ).fetchall()
    conn.close()

    if not rows:
        return  # stdout vazio → cron não notifica

    n = len(rows)
    altas = sum(1 for r in rows if r[4] == "alta")
    print(f"⏳ Você tem {n} pendência(s) aguardando — {altas} de prioridade alta.")
    print(f"Me diga 'resolver pendências' quando estiver disponível que eu apresento uma a uma. 🙂")
    for r in rows:
        pid, titulo, ctx, tipo, prio, status, criada, resolvida = r
        print(f"  • #{pid} [{prio}] {titulo}" + (f" ({ctx})" if ctx else ""))


def cmd_stats(args):
    conn = conectar()
    pend = conn.execute("SELECT COUNT(*) FROM pendencias WHERE status='pendente'").fetchone()[0]
    res = conn.execute("SELECT COUNT(*) FROM pendencias WHERE status='resolvida'").fetchone()[0]
    can = conn.execute("SELECT COUNT(*) FROM pendencias WHERE status='cancelada'").fetchone()[0]
    total = conn.execute("SELECT COUNT(*) FROM pendencias").fetchone()[0]
    conn.close()
    print(f"📊 Pendências: {pend} ativas | {res} resolvidas | {can} canceladas | {total} total")


def main():
    parser = argparse.ArgumentParser(description="Sistema de pendências Hermes ↔ Usuário")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_add = sub.add_parser("add", help="Adiciona pendência")
    p_add.add_argument("--titulo", required=True)
    p_add.add_argument("--contexto", default="")
    p_add.add_argument("--tipo", default="outro", choices=["confirmacao", "decisao", "revisao", "outro"])
    p_add.add_argument("--prioridade", default="media", choices=["alta", "media", "baixa"])
    p_add.set_defaults(func=cmd_add)

    p_list = sub.add_parser("list", help="Lista pendências")
    p_list.add_argument("--todas", action="store_true")
    p_list.set_defaults(func=cmd_list)

    p_res = sub.add_parser("resolve", help="Resolve pendência")
    p_res.add_argument("id", type=int)
    p_res.set_defaults(func=cmd_resolve)

    p_can = sub.add_parser("cancel", help="Cancela pendência")
    p_can.add_argument("id", type=int)
    p_can.set_defaults(func=cmd_cancel)

    p_rem = sub.add_parser("remind", help="Mensagem de lembrete (para cron)")
    p_rem.set_defaults(func=cmd_remind)

    p_sta = sub.add_parser("stats", help="Resumo")
    p_sta.set_defaults(func=cmd_stats)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
