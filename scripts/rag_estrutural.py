#!/usr/bin/env python3
"""RAG ESTRUTURAL (pendência #18) — recuperação por ATO, não por chunk fixo.

Hipótese: segmentar o boletim por ato (unidade legal natural) preserva a
estrutura que o chunking de janela fixa da #10 destrói. Recuperamos o ato
inteiro (cabeçalho + ementa + artigos) em vez de fatias de 800 chars.

REUSO: importa helpers do harness #10 (rag_vetorial_ng) para manter o MESMO
juiz, as MESMAS perguntas e o MESMO retrieval — único delta é a unidade de
indexação. Isso faz o A/B justo.
"""
import argparse, json, os, re, sqlite3, sys, time
from pathlib import Path
import rag_vetorial_ng as R          # reusa _embed, buscar-scorer, QUESTIONS, benchmark

# Índice separado — não polui o da #10
DATA_DIR = R.DATA_DIR
INDEX_DB = DATA_DIR / "rag_estrutural.db"
RESULTS_JSON = DATA_DIR / "benchmark_v1_estrutural.json"

ATO_RE = re.compile(r"^##\s+(N|EDITAL|DECIS)")   # inícios de ato (Nº/N°, EDITAL, DECISÃO/DECISÃO ADM); exclui EDITAIS/PORTARIAS

def segmentar_por_ato(texto, src, max_chars=10000):
    """Divide o boletim em atos, preservando o corpo completo de cada um.
    Retorna lista de (src, texto_do_ato).
    Atos anormalmente grandes (cabeçalho não capturado / tabelas enormes) são
    subdivididos por quebras de parágrafo para caber no limite do modelo."""
    linhas = texto.splitlines()
    cortes = [i for i, l in enumerate(linhas) if ATO_RE.match(l.strip())]
    if not cortes:
        cortes = [0]
    cortes.append(len(linhas))
    out = []
    for k in range(len(cortes) - 1):
        bloco = "\n".join(linhas[cortes[k]:cortes[k+1]])
        # normaliza whitespace preservando texto completo
        txt = re.sub(r"[ \t]+", " ", bloco)
        txt = re.sub(r"\n{3,}", "\n\n", txt).strip()
        if len(txt) < 60:
            continue
        if len(txt) <= max_chars:
            out.append((src, txt))
        else:
            out.extend(_subdividir(txt, src, max_chars))
    return out

def _subdividir(txt, src, max_chars):
    """Quebra por parágrafos até cada pedaço caber em max_chars (sem perder texto)."""
    paragrafos = [p.strip() for p in re.split(r"\n\s*\n", txt) if p.strip()]
    pedacos, atual = [], ""
    for par in paragrafos:
        # parágrafo individual maior que o teto: quebra por janela
        if len(par) > max_chars:
            if atual:
                pedacos.append(atual); atual = ""
            for i in range(0, len(par), max_chars):
                pedacos.append(par[i:i+max_chars])
            continue
        if len(atual) + len(par) + 2 > max_chars:
            pedacos.append(atual); atual = par
        else:
            atual = (atual + "\n\n" + par) if atual else par
    if atual:
        pedacos.append(atual)
    return [(src, p.strip()) for p in pedacos if len(p.strip()) >= 60]

# ------------------------------------------------------------------ index
def indexar(subconjunto=None, api_key=None):
    api_key = api_key or os.environ["OPENROUTER_API_KEY"]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(INDEX_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS atos(
        id INTEGER PRIMARY KEY, src TEXT, txt TEXT, emb TEXT, n CHAR(32), ts REAL)""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_src ON atos(src)")

    pdfs = sorted(R.DOC_DIR.glob("BS-*.md"))
    if subconjunto:
        pdfs = [p for p in pdfs if p.stem in subconjunto]
    hash_por_src = {p.stem: R.hashlib_md5_chars(p) for p in pdfs}

    novos = [p for p in pdfs
             if con.execute("SELECT 1 FROM atos WHERE src=? AND n=?", (p.stem, hash_por_src[p.stem])).fetchone() is None]
    if not novos:
        print(f"[index] sem novidades ({len(pdfs)} boletins revisitados).")
        con.close()
        return 0

    todas = []
    for p in novos:
        txt = p.read_text(encoding="utf-8")  # cru (com linhas) — cabeçalhos ## são âncora de linha
        todas.extend(segmentar_por_ato(txt, p.stem))
    print(f"[embed] {len(todas)} ATOS novos ({len(novos)} boletins)…")
    vecs = R._embed([c[1] for c in todas], api_key)

    cur = con.cursor()
    now = time.time()
    for (src, txt), v in zip(todas, vecs):
        cur.execute("INSERT INTO atos(src,txt,emb,n,ts) VALUES(?,?,?,?,?)",
                    (src, txt, json.dumps(v), hash_por_src[src], now))
    srcs_vivos = set(hash_por_src)
    placeholders = ",".join("?"*len(srcs_vivos))
    cur.execute(f"DELETE FROM atos WHERE src NOT IN ({placeholders})", list(srcs_vivos))
    con.commit()
    total = cur.execute("SELECT COUNT(*) FROM atos").fetchone()[0]
    print(f"[index] OK: {total} atos no índice estrural.")
    con.close()
    return total

# ------------------------------------------------------------------ buscar (mesma mecânica da #10, mas lê o índice de atos)
def buscar(pergunta, k=R.TOP_K, api_key=None):
    api_key = api_key or os.environ["OPENROUTER_API_KEY"]
    con = sqlite3.connect(INDEX_DB)
    rows = con.execute("SELECT src,txt,emb FROM atos").fetchall()
    if not rows:
        raise SystemExit("Índice vazio. Rode `indexar` primeiro.")
    qv = R._embed([pergunta], api_key)[0]
    scored = sorted(((R._cos(qv, json.loads(e)), s, t) for s, t, e in rows), reverse=True)
    return [{"src": s, "score": round(float(score), 4), "txt": t[:400]} for score, s, t in scored[:k]]

# ------------------------------------------------------------------ benchmark (reedita o da #10 usando o buscar estrural + RESULTS v1)
def benchmark(subconjunto=None, api_key=None):
    api_key = api_key or os.environ["OPENROUTER_API_KEY"]
    resultados, acerto = [], 0
    for q in R.QUESTIONS:
        top = buscar(q["pergunta"], api_key=api_key)
        contexto = "\n\n---\n\n".join(f"[{x['src']}] {x['txt']}" for x in top)
        r = R._chat([
            {"role":"system","content":"Consultor jurídico do MPT. Responda com base APENAS nos trechos. "
                                        "Cite o arquivo BS-##. Dê número do ato/boletim quando pedido. "
                                        "Se realmente não houver informação, diga 'NENHUMA INFORMAÇÃO'."},
            {"role":"user","content":f"PERGUNTA: {q['pergunta']}\n\nTRECHOS:\n{contexto}"}], api_key)
        up = (r or "").upper()
        tem_dado = ("NENHUMA INFORMAÇÃO" not in up and "NÃO HÁ" not in up
                    and "não há" not in (r or "").lower() and "impossível" not in (r or "").lower()
                    and "sem informação" not in (r or "").lower())
        achou = [t for t in q["expected"] if t.upper() in up] if tem_dado else []
        ok = bool(achou)
        acerto += 1 if ok else 0
        resultados.append({"id": q["id"], "pergunta": q["pergunta"], "resposta": r,
                           "acerto": ok, "termos": achou, "top_srcs": [x["src"] for x in top],
                           "tem_dado": tem_dado})
        print(f"{q['id']}: {'✅' if ok else '❌'}  {r[:140].strip()}")
    pacote = {"modelo_emb": R.EMB_MODEL, "modelo_chat": R.CHAT_MODEL, "estrategia": "ato-estrutural",
              "acerto_objetivo": f"{acerto}/{len(R.QUESTIONS)}", "perguntas": resultados,
              "gerado_em": time.strftime("%Y-%m-%d %H:%M:%S")}
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(pacote, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nResultado salvo: {RESULTS_JSON}")
    print(f"\n===== ACERTO OBJETIVO (ESTRUTURAL): {acerto}/{len(R.QUESTIONS)} =====")
    return pacote

# ------------------------------------------------------------------ main
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("indexar").add_argument("--subconjunto", nargs="*")
    b = sub.add_parser("buscar"); b.add_argument("pergunta"); b.add_argument("-k", type=int, default=R.TOP_K)
    sub.add_parser("benchmark").add_argument("--subconjunto", nargs="*")
    a = ap.parse_args()
    if a.cmd == "indexar":
        indexar(subconjunto=a.subconjunto); sys.exit(0)
    elif a.cmd == "buscar":
        for x in buscar(a.pergunta, k=a.k):
            print(json.dumps(x, ensure_ascii=False))
    elif a.cmd == "benchmark":
        benchmark(subconjunto=a.subconjunto); sys.exit(0)