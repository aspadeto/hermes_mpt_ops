#!/usr/bin/env python3
"""RAG vetorial sobre o corpus docling (pendência #10).

Estrutura promovível a produção (não PoC-descartável):
- Índice em SQLite (rag_index.db): persistente, incremental, consultável.
  - Nesta versão os embeddings são armazenados como BLOB JSON por praticidade;
    em produção pode-se migrar para SQLite+vec ou pgvector mantendo o SCHEMA.
- Três operações independentes e importáveis:
    indexar(corpus)  -> builda/atualiza o índice (idempotente, incremental)
    buscar(pergunta) -> retrieval top-k por similaridade de cosseno
    benchmark()      -> roda as perguntas do vCground truth e grava JSON
- Resultado de benchmark em JSON estruturado (reaproveitável / auditável).

Uso (CLI):
    python3 rag_ng.py indexar            # embeda o corpus e grava SQLite (cache)
    python3 rag_ng.py buscar "pergunta" -k 5
    python3 rag_ng.py benchmark          # roda as perguntas e grava resultados.json

Uso (library):
    import rag_ng
    rag_ng.indexar()
    rag_ng.buscar("qual portaria?")
"""
import argparse, json, math, os, re, sqlite3, sys, time
from pathlib import Path

OPS = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops")
DOC_DIR = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/boletins_docling")
DATA_DIR = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/data/rag")  # produção: volume no OPS
INDEX_DB = DATA_DIR / "rag_index.db"
RESULTS_JSON = DATA_DIR / "benchmark_v0.json"

EMB_MODEL = "text-embedding-3-small"
CHAT_MODEL = "deepseek/deepseek-v4-flash-0731"

CHUNK_CHARS = 800
CHUNK_STEP = 400
BATCH = 32
TOP_K = 5

# Corpus-alvo por padrão = TODO. Em teste pode restringir via --subconjunto.
DEFAULT_TARGETS = None  # None = todos os boletins

QUESTIONS = [
 {"id":"F1","pergunta":"Em janeiro de 2025 a estrutura organizacional da PRT10 foi alterada por qual portaria?", "expected":["56","012","12/2025","BS-012"], "boletim": "012"},
 {"id":"F2","pergunta":"Em qual boletim foi publicada a portaria que constitui a comissão SPARKS?", "expected":["1124","144","144/2025","BS-144"], "boletim": "144"},
 {"id":"F3","pergunta":"Qual ato emitido entre julho e agosto de 2026 designa ARIANNE CASTRO DE ARAÚJO MIRANDA para o 26º Ofício Especializado da PRT 10ª Região?", "expected":["231","142","142/2026","BS-142","ARIANNE"], "boletim": "142"},
 {"id":"F4","pergunta":"Qual a portaria publicada entre dezembro de 2025 e janeiro de 2026 que dispensa a servidora Ana Paula Alves Dubieux da Comissão de Gestão Socioambiental da PRT14?", "expected":["332","001/2026","BS-001","Ana Paula"], "boletim": "001"},
 {"id":"F5","pergunta":"Em março de 2026 a Procuradora do Trabalho Fernanda Furlaneto foi dispensada do encargo de Coordenadora da CONAP da PRT da 16ª Região, em qual Boletim a portaria foi publicada?", "expected":["47","047","BS-047","47/2026","Fernanda","Furlaneto"], "boletim": "047"},
 {"id":"C1","pergunta":"Sobre o que trata a Portaria 400/2026 da PGT?", "expected":["400","fiscalização","ata","registro","preços"], "boletim": ""},
 {"id":"C2","pergunta":"Sobre o que versa a portaria 26 da PRT18?", "expected":["Luziânia","inventariar","regularizar","bens"], "boletim": "050"},
 {"id":"C3","pergunta":"Qual portaria anula a portaria 1564.2025 do PGEA 20.02.0001?", "expected":["2152","1564","ANULAR","anula"], "boletim": "001"},
 {"id":"C4","pergunta":"Como se deu o funcionamento de todas as unidades da Procuradoria Regional do Trabalho da 16ª Região durante os dias 20/12/2024 e 06/01/2025?", "expected":["plantão","16","16ª","20/12","06/01"], "boletim": ""},
 {"id":"C5","pergunta":"Sobre o que trata o Edital 37/2025 da PRT8?", "expected":["37","redistribuição","comissão","CC-02","analista"], "boletim": ""},
]

# ------------------------------------------------------------------ helpers
def _api(path, payload, key):
    import requests
    r = requests.post(f"https://openrouter.ai/api/v1/{path}",
                      headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                      json=payload, timeout=120)
    r.raise_for_status()
    return r.json()

def _embed(texts, key):
    out = []
    for i in range(0, len(texts), BATCH):
        d = _api("embeddings", {"model": EMB_MODEL, "input": texts[i:i+BATCH]}, key)
        out += [x["embedding"] for x in d["data"]]
    return out

def _cos(a, b):
    return sum(x*y for x, y in zip(a, b)) / (math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b)) + 1e-9)

def _chunks_of(text, src):
    out = []
    for i in range(0, max(1, len(text) - CHUNK_CHARS + 1), CHUNK_STEP):
        frag = text[i:i+CHUNK_CHARS]
        if len(frag) >= 60:
            out.append((src, frag))
    return out

# ------------------------------------------------------------------ index
def indexar(subconjunto=None, api_key=None):
    """Builda/atualiza o índice SQLite (idempotente e incremental por arquivo+hash)."""
    api_key = api_key or os.environ["OPENROUTER_API_KEY"]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(INDEX_DB)
    con.execute("""CREATE TABLE IF NOT EXISTS chunks(
        id INTEGER PRIMARY KEY, src TEXT, txt TEXT, emb TEXT, n CHAR(32), ts REAL)""")
    con.execute("CREATE INDEX IF NOT EXISTS idx_src ON chunks(src)")

    pdfs = sorted(DOC_DIR.glob("BS-*.md"))
    if subconjunto:
        pdfs = [p for p in pdfs if p.stem in subconjunto]

    novos, faltam_embed = [], []
    for p in pdfs:
        h = hashlib_md5_chars(p)
        row = con.execute("SELECT 1 FROM chunks WHERE src=? AND n=?", (p.stem, h)).fetchone()
        if row is None:
            novos.append(p)
    if not novos:
        print(f"[index] sem novidades ({len(pdfs)} arquivos revisitados).")
        return con.total_changes or 0

    todas = []
    for p in novos:
        txt = re.sub(r"\s+", " ", p.read_text(encoding="utf-8")).strip()
        todas.extend(_chunks_of(txt, p.stem))
    print(f"[embed] {len(todas)} chunks novos ({len(novos)} boletins)…")
    vecs = _embed([c[1] for c in todas], api_key)

    cur = con.cursor()
    now = time.time()
    for (src, txt), v in zip(todas, vecs):
        h = hashlib_md5_chars(Path(f"{src}.md"))  # hash do arquivo de origem
        cur.execute("INSERT INTO chunks(src,txt,emb,n,ts) VALUES(?,?,?,?,?)",
                    (src, txt, json.dumps(v), h, now))
    # remove chunks de fontes que sumiram (boletim removido)
    srcs_vivos = {p.stem for p in pdfs}
    cur.execute("DELETE FROM chunks WHERE src NOT IN (%s)" % ",".join("?"*len(srcs_vivos)), list(srcs_vivos))
    con.commit()
    total = cur.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    print(f"[index] OK: {total} chunks no índice.")
    con.close()
    return total

def hashlib_md5_chars(path):
    import hashlib
    return hashlib.md5(path.read_bytes()[:2_000_000]).hexdigest()

# ------------------------------------------------------------------ buscar
def buscar(pergunta, k=TOP_K, api_key=None):
    api_key = api_key or os.environ["OPENROUTER_API_KEY"]
    con = sqlite3.connect(INDEX_DB)
    rows = con.execute("SELECT src,txt,emb FROM chunks").fetchall()
    if not rows:
        raise SystemExit("Índice vazio. Rode `indexar` primeiro.")
    qv = _embed([pergunta], api_key)[0]
    scored = sorted((( _cos(qv, json.loads(e)), s, t) for s, t, e in rows), reverse=True)
    return [{"src": s, "score": round(float(score), 4), "txt": t[:400]} for score, s, t in scored[:k]]

def _chat(messages, key):
    d = _api("chat/completions", {"model": CHAT_MODEL, "messages": messages}, key)
    return d["choices"][0]["message"]["content"]

# ------------------------------------------------------------------ benchmark
def benchmark(subconjunto=None, api_key=None, gravar=True):
    api_key = api_key or os.environ["OPENROUTER_API_KEY"]
    resultados, acerto_objetivo = [], 0
    for q in QUESTIONS:
        top = buscar(q["pergunta"], api_key=api_key)
        contexto = "\n\n---\n\n".join(f"[{x['src']}] {x['txt']}" for x in top)
        r = _chat([
            {"role":"system","content":"Consultor jurídico do MPT. Responda com base APENAS nos trechos. "
                                        "Cite o arquivo BS-##. Dê número do ato/boletim quando pedido. "
                                        "Se realmente não houver informação, diga 'NENHUMA INFORMAÇÃO'."},
            {"role":"user","content":f"PERGUNTA: {q['pergunta']}\n\nTRECHOS:\n{contexto}"}], api_key)
        up = (r or "").upper()
        # Judge OBJETIVO: resposta que declara ausência NÃO conta mesmo se ecoar número da pergunta
        tem_dado = "NENHUMA INFORMAÇÃO" not in up and ("N" + "\u00c3O " + "HÁ" not in up.replace("NÃO HÁ", "NAOHADE")) and "não há" not in (r or "").lower() and "impossível" not in (r or "").lower() and "sem informação" not in (r or "").lower()
        achou = [t for t in q["expected"] if t.upper() in up] if tem_dado else []
        ok = bool(achou)
        acerto_objetivo += 1 if ok else 0
        resultados.append({"id": q["id"], "pergunta": q["pergunta"], "resposta": r,
                           "acerto": ok, "termos": achou, "top_srcs": [x["src"] for x in top],
                           "tem_dado": tem_dado})
        print(f"{q['id']}: {'✅' if ok else '❌'}  {r[:140].strip()}")

    pacote = {"modelo_emb": EMB_MODEL, "modelo_chat": CHAT_MODEL, "n_boletins_no_indice": None,
              "acerto_objetivo": f"{acerto_objetivo}/{len(QUESTIONS)}", "perguntas": resultados,
              "gerado_em": time.strftime("%Y-%m-%d %H:%M:%S")}
    if gravar:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        RESULTS_JSON.write_text(json.dumps(pacote, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nResultado salvo: {RESULTS_JSON}")
    print(f"\n===== ACERTO OBJETIVO: {acerto_objetivo}/{len(QUESTIONS)} =====")
    return pacote

# ------------------------------------------------------------------ main
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("indexar").add_argument("--subconjunto", nargs="*", help="nomes BS-*")
    b = sub.add_parser("buscar"); b.add_argument("pergunta"); b.add_argument("-k", type=int, default=TOP_K)
    bm = sub.add_parser("benchmark"); bm.add_argument("--subconjunto", nargs="*")
    a = ap.parse_args()
    if a.cmd == "indexar":
        sys.exit(indexar(subconjunto=a.subconjunto))
    elif a.cmd == "buscar":
        for x in buscar(a.pergunta, k=a.k):
            print(json.dumps(x, ensure_ascii=False))
    elif a.cmd == "benchmark":
        benchmark(subconjunto=a.subconjunto)
        sys.exit(0)