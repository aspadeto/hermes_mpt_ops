#!/usr/bin/env python3
"""compreender_pgea.py — Rascunho da compreensão causal de um PGEA.

Regras primeiro (zero custo): lê o extracao.md auditado, detecta peças
(HEADER_RE do extrair_auditar_pgea.py), datas e infere a função causal por
heurística de tipo de peça + verbo do despacho. Marca DÚVIDAS para revisão
do LLM/usuário.

Uso:
    compreender_pgea.py <extracao.md>                 # rascunho da tabela em stdout
    compreender_pgea.py <extracao.md> --saida ARQ.md  # grava rascunho em arquivo
    compreender_pgea.py <extracao.md> --duvidas       # só os pontos incertos
"""
import re, sys
from pathlib import Path

HEADER_RE = re.compile(
    r"^(?P<tipo>[A-ZÀ-Úa-zà-ú ]+?)\s+(?P<num>\d{5,6}\.\d{4})\s*\((?P<id>\d{7,8})\)\s*(?:[−-]\s*PGEA\s)?$",
    re.IGNORECASE,
)

# Heurística de função causal por tipo de peça (extensível)
TIPO_FUNCAO = {
    "requerimento": "origem",
    "decisão": "decisao",
    "decisão administrativa": "decisao",
    "elaboração de minuta": "manifestacao",
    "relatório": "manifestacao",
    "manifestação do servidor": "manifestacao",
    "juntada": "instrucao",
    "cópia de documento": "instrucao",
    "outras providências": "instrucao",
    "despacho": "movimentacao",  # refinado pelo verbo abaixo
    "ofício": "movimentacao",
}

# Verbos que refinam despachos/ofícios
VERBO_FUNCAO = [
    (r"(?i)autoriz|defer|indefer|aprov", "decisao"),
    (r"(?i)design|nomei", "movimentacao"),
    (r"(?i)encaminhe|remeta|devolv|retorn", "movimentacao"),
    (r"(?i)ciente|comunico|informo|levo ao conhecimento", "instrucao"),
    (r"(?i)suger|opino|entendo|considerando", "manifestacao"),
    (r"(?i)providenc|adot", "execucao"),
]

ESTAGIO_POR_FUNCAO = {
    "origem": "abertura",
    "instrucao": "instrucao",
    "movimentacao": None,  # mantém estágio anterior
    "manifestacao": "analise",
    "decisao": "decisao",
    "execucao": "execucao",
}

def detectar_peca(linha):
    m = HEADER_RE.match(linha.strip())
    if not m:
        return None
    tipo = " ".join(m.group("tipo").split()).lower()
    return tipo, f"{m.group('tipo').strip()} {m.group('num')} ({m.group('id')})"

def funcao_por_heuristica(tipo, corpo):
    base = TIPO_FUNCAO.get(tipo, None)
    if base == "movimentacao" and corpo:
        for pat, fn in VERBO_FUNCAO:
            if re.search(pat, corpo):
                return fn
    return base

def extrair_datas(corpo):
    return sorted(set(re.findall(r"\d{2}/\d{2}/\d{4}", corpo)))

def pecas_de(md_texto):
    """Retorna [(tipo, nome_peca, datas, corpo_resumido, paginas)]."""
    secoes = re.split(r"\n## ", md_texto)
    out = []
    for sec in secoes[1:]:
        titulo = sec.split("\n")[0].strip()
        m = HEADER_RE.match(titulo)
        if not m:
            continue
        tipo = " ".join(m.group("tipo").split()).lower()
        nome = f"{m.group('tipo').strip()} {m.group('num')} ({m.group('id')})"
        corpo = re.sub(r"<!-- pág \d+ -->", "", sec)
        corpo = re.sub(r"\s+", " ", corpo)[:4000]
        pags = re.findall(r"<!-- pág (\d+) -->", sec)
        out.append({"tipo": tipo, "nome": nome, "datas": extrair_datas(corpo), "corpo": corpo, "pags": pags})
    return out

def montar_eventos(pecas):
    eventos, estagio_atual = [], None
    for i, p in enumerate(pecas):
        fn = funcao_por_heuristica(p["tipo"], p["corpo"])
        if fn is None:
            fn = "movimentacao"  # fallback seguro
        if ESTAGIO_POR_FUNCAO[fn]:
            estagio_atual = ESTAGIO_POR_FUNCAO[fn]
        # datas: primeira data do corpo (ou da peça seguinte se vazia)
        data = p["datas"][0] if p["datas"] else None
        if not data:
            for prox in pecas[i+1:]:
                if prox["datas"]:
                    data = f"≈ {prox['datas'][0]}"
                    break
        # efeito: primeira frase com verbo de ato (ou aviso de dúvida)
        efeito = None
        for fr in re.split(r"(?<=[.!?])\s+", p["corpo"][:1500]):
            if re.search(r"(?i)(encaminh|autoriz|defer|solicit|junt|design|determin|informo|ciente|opino|aprova|providenc)", fr):
                efeito = fr.strip()[:180]
                break
        duvida = fn is None or not data or not efeito
        eventos.append({
            "seq": i + 1, "tipo": p["tipo"], "nome": p["nome"],
            "datas": p["datas"], "data": data, "funcao": fn,
            "estagio": estagio_atual, "efeito": efeito, "duvida": duvida,
        })
    return eventos

def formatar_rascunho(eventos):
    L = ["| # | Data | Peça | Função | Estágio | Efeito (rascunho) |",
         "|---|------|------|--------|---------|-------------------|"]
    for ev in eventos:
        flag = " ⚠️" if ev["duvida"] else ""
        efeito = ev["efeito"] or "*[rever]*"
        L.append(f"| {ev['seq']} | {ev['data'] or '—'} | {ev['nome']} | {ev['funcao']}{flag} | {ev['estagio'] or '—'} | {efeito} |")
    return "\n".join(L)

def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__); sys.exit(1)
    md_path = Path(args[0])
    saida, so_duvidas = None, False
    if "--saida" in args:
        saida = Path(args[args.index("--saida") + 1])
    if "--duvidas" in args:
        so_duvidas = True
    pecas = pecas_de(md_path.read_text())
    eventos = montar_eventos(pecas)
    if so_duvidas:
        for ev in eventos:
            if ev["duvida"]:
                print(f"- #{ev['seq']} {ev['nome']}: data={ev['data'] or 'SEM DATA'} função={ev['funcao']} efeito={ev['efeito'] or 'SEM EFEITO'}")
        return
    rascunho = formatar_rascunho(eventos)
    if saida:
        saida.write_text(rascunho)
        print(f"Rascunho gravado em {saida} ({len(eventos)} eventos, "
              f"{sum(1 for e in eventos if e['duvida'])} dúvidas)")
    else:
        print(rascunho)

if __name__ == "__main__":
    main()
