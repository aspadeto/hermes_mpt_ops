#!/usr/bin/env python3
"""benchmark_fts5.py — Teste do SQLite FTS5 sobre o corpus boletins_docling.

Benchmark das 10 perguntas do benchmark-boletins.md contra:
  - FTS5 (novo teste): índice full-text dos MDs + metadados estruturais

Saída: data/benchmark/fts5_resultado.json
       + relatório texto na saída padrão.
"""

import json
import re
import sqlite3
import sys
import time
from pathlib import Path

# ------------------------------------------------------------ Configuração
OPS = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops")
KB = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb")
DOCLING = KB / "boletins_docling"
DEST = OPS / "data" / "benchmark"
DEST.mkdir(parents=True, exist_ok=True)

PYTHON = sys.executable

# ------------------------------------------------------------ 10 perguntas + ground truth
# extraído de benchmark-boletins.md (F1-F5 + C1-C5)
QUESTOES = [
    # --- Factual ---
    {
        "id": "F1",
        "tipo": "factual",
        "pergunta": "Qual a portaria que altera a estrutura organizacional da PRT10?",
        "expected": ["56", "2025", "012"],
        "boletim_esperado": "BS-012-2025",
        "label": "Portaria 56/2025 - estrutura PRT10",
    },
    {
        "id": "F2",
        "tipo": "factual",
        "pergunta": "Em qual boletim foi publicada a comissão SPARKS?",
        "expected": ["1124", "2025", "144"],
        "boletim_esperado": "BS-144-2025",
        "label": "Comissão SPARKS - Portaria 1124/2025",
    },
    {
        "id": "F3",
        "tipo": "factual",
        "pergunta": "Qual ato designa ARIANNE CASTRO DE ARAÚJO MIRANDA para o 26º Ofício da PRT10?",
        "expected": ["ARIANNE", "PRT10", "26º"],
        "boletim_esperado": "BS-142-2026",
        "label": "Designação ARIANNE - Portaria 240/2026 BS-145",
    },
    {
        "id": "F4",
        "tipo": "factual",
        "pergunta": "Qual a portaria que dispensa a servidora Ana Paula Alves Dubieux?",
        "expected": ["332", "Ana Paula", "dispensa"],
        "boletim_esperado": "BS-001-2026",
        "label": "Portaria 332/2025 - dispensa Ana Paula PRT14",
    },
    {
        "id": "F5",
        "tipo": "factual",
        "pergunta": "Qual a portaria 1 do boletim 002/2026 da PRT1?",
        "expected": ["002", "2026", "PRT1"],
        "boletim_esperado": "BS-002-2026",
        "label": "BS 002/2026 - PRT1 - portaria 1",
    },
    # --- Conteúdo ---
    {
        "id": "C1",
        "tipo": "conteudo",
        "pergunta": "Qual a gratificação do Chefe de Gabinete da portaria de estrutura organizacional da PRT10?",
        "expected": ["CC-4", "Chefe de Gabinete", "56"],
        "boletim_esperado": "BS-012-2025",
        "label": "CC-4 - gratificação Chefe de Gabinete",
    },
    {
        "id": "C2",
        "tipo": "conteudo",
        "pergunta": "Sobre o que versa a portaria 26 da PRT18?",
        "expected": ["26", "PRT18", "Luziânia", "inventário", "regularizar", "almoxarifado"],
        "boletim_esperado": "BS-050-2025",
        "label": "Portaria 26/2025 PRT18 - inventário PTM Luziânia",
    },
    {
        "id": "C3",
        "tipo": "conteudo",
        "pergunta": "Qual portaria anula a portaria 1564.2025 do PGEA 20.02.0001?",
        "expected": ["2152", "1564", "20.02.0001", "anula"],
        "boletim_esperado": "BS-001-2026",
        "label": "Portaria 2152 anula 1564 (PGEA 20.02.0001)",
    },
    {
        "id": "C4",
        "tipo": "conteudo",
        "pergunta": "Sobre o que versa a portaria 332 de 30 de dezembro de 2025?",
        "expected": ["332", "30", "dezembro", "2025", "dispensa", "Ana Paula"],
        "boletim_esperado": "BS-001-2026",
        "label": "Portaria 332/2025 - dispensa Ana Paula",
    },
    {
        "id": "C5",
        "tipo": "conteudo",
        "pergunta": "Qual portaria designa Daniel Gemignani para o 58º Ofício?",
        "expected": ["Daniel Gemignani", "58º", "Ofício"],
        "boletim_esperado": "BS-004-2026",
        "label": "Portaria 13/2026 - Daniel Gemignani 58º Ofício",
    },
]


# ------------------------------------------------------------ helpers FTS5
def conn_fts5(db_path: Path) -> sqlite3.Connection:
    """Abre (ou cria) banco com tabela FTS5 simples (sem content externo)."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS boletim_meta (
            arquivo TEXT PRIMARY KEY,
            numero_boletim TEXT,
            data_boletim TEXT,
            ano TEXT
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS doc_fts USING fts5(
            conteudo,
            arquivo,
            numero_boletim,
            data_boletim,
            ano
        );
    """)
    conn.commit()
    return conn


def ler_md_docling(path: Path) -> str:
    """Lê MD docling e normaliza para indexação: preserva estrutura, remove
    apenas marcadores de imagem que inibem tokenização (opcional).
    """
    txt = path.read_text(encoding="utf-8")
    # remove <!-- image --> para não poluir o índice textual, mas mantém
    # heading, tabelas, ementa, etc.
    txt = re.sub(r"<!-- image -->", " ", txt)
    return txt


def achar_meta_arquivo(md: Path) -> dict:
    """Extrai metadados estruturais do nome do arquivo + cabeçalho do boletim."""
    m = re.match(r"BS-(\d+(?:\.\d+)*)-(\d{4})\.md$", md.name)
    if not m:
        numero = md.name
        ano = ""
    else:
        numero = f"{m.group(1)}/{m.group(2)}"
        ano = m.group(2)
    txt = md.read_text(encoding="utf-8")
    data = ""
    # CIRCULAÇÃO: DD/MM/AAAA
    cm = re.search(r"CIRCULA[ÇC][ÃA]O\s*[:.]?\s*(\d{1,2})/(\d{1,2})/(\d{4})", txt, re.IGNORECASE)
    if cm:
        try:
            data = f"{int(cm.group(3)):04d}-{int(cm.group(2)):02d}-{int(cm.group(1)):02d}"
        except ValueError:
            pass
    else:
        # SEGUNDA-FEIRA, DD DE MÊS DE AAAA (capa)
        dm = re.search(r"\b(\d{1,2})\s+DE\s+([A-ZÇÃÊÓÍÀ-Ú]+)\s+DE\s+(\d{4})\b", txt, re.IGNORECASE)
        if dm:
            MES = {
                "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
                "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
                "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12",
            }
            mes = MES.get(dm.group(2).lower())
            if mes:
                try:
                    data = f"{int(dm.group(3)):04d}-{mes}-{int(dm.group(1)):02d}"
                except ValueError:
                    pass
    return {"arquivo": md.name, "numero_boletim": numero, "data_boletim": data, "ano": ano}


def construir_indice(conn: sqlite3.Connection, docling_dir: Path) -> int:
    """Popula FTS5 com um registro por MD docling (todo o conteúdo do arquivo)."""
    md_paths = sorted(docling_dir.glob("BS-*.md"))
    if not md_paths:
        raise RuntimeError(f"Não encontrei MDs em {docling_dir}")

    meta_ins = conn.executemany(
        "INSERT OR REPLACE INTO boletim_meta (arquivo, numero_boletim, data_boletim, ano) VALUES (?,?,?,?)",
        [tuple(achar_meta_arquivo(md).values()) for md in md_paths],
    )
    conn.commit()

    # inserção em lote no FTS5
    doc_texts = []
    for md in md_paths:
        meta = achar_meta_arquivo(md)
        txt = ler_md_docling(md)
        doc_texts.append((txt, meta["arquivo"], meta["numero_boletim"], meta["data_boletim"], meta["ano"]))

    conn.executemany(
        "INSERT INTO doc_fts (conteudo, arquivo, numero_boletim, data_boletim, ano) VALUES (?,?,?,?,?)",
        doc_texts,
    )
    conn.commit()
    return len(md_paths)


def formatar_relevancia_score(conn: sqlite3.Connection, query_fts: str) -> list[dict]:
    """Retorna os top-10 documentos rankingados pelo BM25 do FTS5."""
    sql = """
        SELECT
            arquivo,
            numero_boletim,
            data_boletim,
            rank
        FROM doc_fts
        WHERE doc_fts MATCH ?
        ORDER BY rank
        LIMIT 10
    """
    rows = conn.execute(sql, (query_fts,)).fetchall()
    return [{"arquivo": r["arquivo"], "boletim": r["numero_boletim"],
             "data": r["data_boletim"], "score": r["rank"]} for r in rows]


def buscar_fts5(conn: sqlite3.Connection, pergunta: str) -> dict:
    """Consulta FTS5 + ranking BM25 + metadados estruturais.

    FTS5 não aceita parâmetro vinculado no MATCH; a query deve ser embutida.
    Escapamos aspas simples para segurança.
    """
    # escape single quotes para FTS5 (duplicar)
    safe = pergunta.replace("'", "''")
    t0 = time.time()
    sql = f"""
        SELECT
            arquivo,
            numero_boletim,
            data_boletim,
            rank
        FROM doc_fts
        WHERE doc_fts MATCH '{safe}'
        ORDER BY rank
        LIMIT 10
    """
    try:
        rows = conn.execute(sql).fetchall()
    except sqlite3.OperationalError as e:
        # fallback: pesquisa por documento vazio retorna erro; retornamos lista vazia
        rows = []
    scores = [{"arquivo": r["arquivo"], "boletim": r["numero_boletim"],
               "data": r["data_boletim"], "score": r["rank"]} for r in rows]
    dt = (time.time() - t0) * 1000
    return {"scores": scores, "tempo_ms": round(dt, 1)}


def avaliar_acerto(q: dict, scores: list[dict]) -> tuple:
    """Avalia se a busca recuperou o documento esperado.
    Critério: o arquivo esperado está no top-10.
    """
    esperado = q["boletim_esperado"]
    encontrado = any(s["arquivo"] == esperado for s in scores)
    return encontrado


# ------------------------------------------------------------ main
def main():
    # 0. construir (ou reutilizar) índice FTS5
    db_path = DEST / "fts5_boletins.db"
    print(f"📚 Corpus docling: {DOCLING}  ({len(list(DOCLING.glob('BS-*.md')))} MDs)")
    print(f"🗄️  Banco FTS5: {db_path}")

    if db_path.exists():
        db_path.unlink()
        print("🗑️  Índice anterior removido para reconstrução limpa.")

    print("🏗️  Construindo índice FTS5...")
    t_start = time.time()
    conn = conn_fts5(db_path)
    n = construir_indice(conn, DOCLING)
    print(f"✅ Índice construído: {n} documentos em {round(time.time()-t_start, 1)}s")
    conn.close()

    conn = conn_fts5(db_path)

    # 1. rodar benchmark
    resultados = []
    print("\n" + "="*60)
    print("RUNNNIG FTS5 × 10 PERGUNTAS")
    print("="*60)

    for q in QUESTOES:
        scores = buscar_fts5(conn, q["pergunta"])["scores"]
        acertou = avaliar_acerto(q, scores)
        resultado = {
            "ferramenta": "fts5",
            "pergunta_id": q["id"],
            "tipo": q["tipo"],
            "label": q["label"],
            "pergunta": q["pergunta"],
            "acerto": acertou,
            "tempo_ms": scores[0]["tempo_ms"] if scores else 0,
            "top3": [{"arquivo": s["arquivo"], "boletim": s["boletim"], "score": s["score"]} for s in scores[:3]],
            "boletim_esperado": q["boletim_esperado"],
        }
        resultados.append(resultado)
        status = "✅" if acertou else "❌"
        print(f"{status} {q['id']} [{q['tipo']}] {q['label']}")
        print(f"   esperado: {q['boletim_esperado']}")
        print(f"   top-3: " + "  |  ".join(f"{s['arquivo']} (score={s['score']})" for s in scores[:3]))
        print(f"   tempo: {resultado['tempo_ms']}ms")
        print()

    # 2. estatísticas
    total = len(resultados)
    factual_ok = sum(1 for r in resultados if r["tipo"] == "factual" and r["acerto"])
    factual_total = sum(1 for r in resultados if r["tipo"] == "factual")
    conteudo_ok = sum(1 for r in resultados if r["tipo"] == "conteudo" and r["acerto"])
    conteudo_total = sum(1 for r in resultados if r["tipo"] == "conteudo")
    print("="*60)
    print("RESUMO")
    print("="*60)
    print(f"FTS5: {sum(1 for r in resultados if r['acerto'])}/{total} total")
    print(f"  factual: {factual_ok}/{factual_total}")
    print(f"  conteúdo: {conteudo_ok}/{conteudo_total}")
    print(f"  tempo médio: {round(sum(r['tempo_ms'] for r in resultados)/total, 1)}ms/pergunta")
    print()

    # comparação com baseline do documento
    baseline = {
        "csv_factual": {"factual": 4, "conteudo": 0, "total": 10},
        "fulltext_docling": {"factual": 2, "conteudo": 0, "total": 5},
        "fulltext_plano": {"factual": 1, "conteudo": 0, "total": 5},
        "docling_poc": {"factual": 3, "conteudo": 1, "total": 5},
    }
    print("COMPARAÇÃO COM BASELINE (23/08/2026)")
    print("-"*40)
    fts5_f = factual_ok
    fts5_c = conteudo_ok
    for nome, vals in baseline.items():
        print(f"  {nome:20s} factual={vals['factual']}/5  conteudo={vals['conteudo']}/5  total={vals['total']}/10")
    print(f"  {'fts5 (teste)':20s} factual={fts5_f}/5  conteudo={fts5_c}/5  total={fts5_c+fts5_f}/10")
    print()

    # 3. salvar JSON
    json_path = DEST / "fts5_resultado.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)
    print(f"📄 Resultado salvo: {json_path}")

    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
