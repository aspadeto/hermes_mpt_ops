#!/usr/bin/env python3
"""catalogar_atos.py — Catálogo de atos normativos de Boletins de Serviço do MPT.

Varre os arquivos .md extraídos (pastas YYYY-MM-DD) de Boletins de Serviço e
detecta os atos publicados. Diferente da 1ª versão (que dependia das seções ##
do auditor), este parser detecta o cabeçalho real de cada ato no texto:

    - gatilho de número+data:  "Nº 1529, DE 30 DE OUTUBRO DE 2024"
    - ou tipo+num explícito:   "PORTARIA Nº 1030/2024"
    - precedido pela seção:    "PORTARIAS" / "DECISÃO" / "EDITAIS" / ...
    - seguido do órgão:        "O PROCURADOR-GERAL DO TRABALHO..."

Popula um banco SQLite com identificação do ato (tipo, número, órgão, data),
referência ao boletim (data/pasta) e página, e resumo/ementa provisória.
O campo `relevante` sinaliza atos que regulamentam funcionamento de processos
administrativos (preenchido em etapa posterior de curadoria).

Uso:
    python3 catalogar_atos.py --raiz boletins --db data/atos.db [--recriar]
"""

import argparse
import re
import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------
# Padrões
# ---------------------------------------------------------------

# Seções de atos dentro do boletim (título que precede a lista de atos)
SECAO_RE = re.compile(
    r"^(?:ATOS\s+)?(?P<secao>PORTARIAS|DECISÕES|DECISÃO|EDITAIS|EDITAL|RESOLUÇÕES|"
    r"RESOLUÇÃO|DESPACHOS|DESPACHO|AVISOS|AVISO|EXTRATOS|EXTRATO|ATAS|ATA|COMUNICADOS|"
    r"COMUNICADO|RETIFICAÇÕES|RETIFICAÇÃO|ERRATA|OFÍCIOS|OFÍCIO|DIVERSOS|"
    r"REQUERIMENTOS|REQUERIMENTO|INSTRUÇÕES\s+NORMATIVAS|INSTRUÇÃO\s+NORMATIVA)\s*$",
    re.IGNORECASE,
)

# Cabeçalho de ato: "Nº 1529, DE 30 DE OUTUBRO DE 2024" ou "Nº 1529, DE 30/10/2024"
NUM_DATA_RE = re.compile(
    r"^N[º°]\s*(\d+(?:\.\d+)?[A-Z]?)\s*(?:,\s*DE\s+(\d{1,2}))?\s*(?:DE\s+(\d{1,2})?\s*"
    r"([A-ZÇÃÊÓÍ][a-zçãêóí]+))?\s*(?:DE\s+(\d{4}))?\s*$",
    re.IGNORECASE,
)

# Tipo + número explícito: "PORTARIA Nº 1030/2024" / "RESOLUÇÃO Nº 222/2024"
TIPO_NUM_RE = re.compile(
    r"^(?P<tipo>PORTARIA(?:\s+(?:CONJUNTA|CONJUNTA\s+NORMATIVA|NORMATIVA|ADMINISTRATIVA))?|"
    r"DESPACHO|DECISÃO|RESOLUÇÃO|EDITAL|AVISO|EXTRATO(?:\s+DE\s+\w+)*|ATA(?:\s+DE\s+\w+)*|"
    r"INSTRUÇÃO\s+NORMATIVA|COMUNICADO|RETIFICAÇÃO|ERRATA|ATO|RECOMENDAÇÃO|OFÍCIO|"
    r"REQUERIMENTO|PARECER|RELATÓRIO|MEMORANDO)"
    r"\s*N[º°]\s*(\d+(?:\.\d+)?[A-Z]?)(?:\s*/\s*(\d{4}))?",
    re.IGNORECASE,
)

# Órgão emissor: "O PROCURADOR-GERAL DO TRABALHO," / "A DIRETORA DE ADMINISTRAÇÃO DA..."
ORGAO_RE = re.compile(
    r"^(?:O|A)\s+(?P<orgao>[A-ZÀ-Úa-zà-ú\-]+(?:[A-ZÀ-Úa-zà-ú\s\-]*))[,:]\s*$|"
    r"^(?:O|A)\s+(?P<orgao2>[A-ZÀ-Úa-zà-ú\s\-]+?)\s*(?:,|no uso)",
    re.IGNORECASE,
)

# Marcador de página
PAG_RE = re.compile(r"<!-- pág (\d+) -->")

# Cabeçalho de regional/unidade (não é ato)
UNIDADE_RE = re.compile(r"^(?:PRT-|PTM-|PROCURADORIA|BSE |CIRCULAÇÃO|MINISTÉRIO|BOLETIM)", re.IGNORECASE)

# Palavras que iniciam o corpo (não atos)
NAO_ATO_RE = re.compile(
    r"^(?:Art\.?|Parágrafo|§|I\b|II\b|III\b|IV\b|V\b|VI\b|VII\b|VIII\b|IX\b|X\b|"
    r"REGISTRE|PUBLIQUE|CONSIDERANDO|RESOLVE|RESOLVO|O\s+PROCURADOR|A\s+PROCURADORA|"
    r"O\s+SUBPROCURADOR|Registre|Brasília|FÁBIO|JOSÉ|JEFERSON|GLÁUCIO|FELIPE|TERESA|"
    r"IZAÍAS|MARIA|ALBERTO|Nº\s+\d+.*,?\s*DE)",  # linha longa de considerando
    re.IGNORECASE,
)


def detectar_secao(linha: str) -> str | None:
    m = SECAO_RE.match(linha.strip())
    if m:
        return m.group("secao").upper()
    return None


def detectar_num_data(linha: str) -> dict | None:
    m = NUM_DATA_RE.match(linha.strip())
    if not m:
        return None
    num = m.group(1)
    dia = m.group(2)
    mes_txt = m.group(4)
    ano = m.group(5)
    data = None
    MESES = {"janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
             "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
             "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12"}
    if dia and mes_txt and ano:
        mes = MESES.get(mes_txt.lower())
        if mes:
            data = f"{ano}-{mes}-{int(dia):02d}"
    return {"numero": num, "data": data}


def detectar_tipo_num(linha: str) -> dict | None:
    m = TIPO_NUM_RE.match(linha.strip())
    if m:
        return {"tipo": m.group("tipo").upper(), "numero": m.group(2),
                "ano": m.group(3)}
    return None


def detectar_orgao(linha: str) -> str | None:
    m = ORGAO_RE.match(linha.strip())
    if m:
        org = m.group("orgao") or m.group("orgao2")
        if org and len(org) < 120 and not UNIDADE_RE.match(org):
            return " ".join(org.split()).upper()
    return None


def extrair_ementa(linhas: list[str], inicio: int, max_chars: int = 400) -> str:
    """Pega as linhas de resumo do ato (a linha logo após 'Nº ... DE' costuma ser a ementa)."""
    partes = []
    for l in linhas[inicio:inicio + 6]:
        l = l.strip()
        if not l or UNIDADE_RE.match(l) or re.fullmatch(r"\d+", l) or l.startswith("<!--"):
            continue
        # para de coletar quando achar corpo do ato
        if re.match(r"^(?:O|A)\s+(?:PROCURADOR|SUBPROCURADOR|CORREGEDOR|DIRETOR|SECRETÁRIO)", l):
            continue
        partes.append(l)
        if sum(len(p) for p in partes) >= max_chars:
            break
    # junta, removendo quebras de linha duplicadas
    texto = " ".join(p for p in partes if p)
    return texto[:max_chars]


def atos_por_arquivo(md: Path) -> list[dict]:
    """Detecta atos individuais no texto do MD, com página e órgão."""
    txt = md.read_text(encoding="utf-8")
    linhas = txt.splitlines()

    atos = []
    pagina = 0
    secao = None
    i = 0
    n = len(linhas)
    while i < n:
        linha = linhas[i]
        linha_strip = linha.strip()

        # atualiza página corrente
        m = PAG_RE.search(linha)
        if m:
            pagina = int(m.group(1))
            i += 1
            continue

        # atualiza seção
        s = detectar_secao(linha_strip)
        if s:
            secao = s
            i += 1
            continue

        # ignora cabeçalhos de unidade/cabeçalho do boletim
        if UNIDADE_RE.match(linha_strip) or re.fullmatch(r"\d+", linha_strip) or len(linha_strip) < 3:
            i += 1
            continue

        # tipo+numero explícito?  "PORTARIA Nº 1030/2024"
        tn = detectar_tipo_num(linha_strip)
        if tn and (tn["tipo"] != "OFÍCIO" or True):
            # número+data (pode estar na linha seguinte ou mesma)
            num = tn["numero"]
            ano = tn["ano"]
            data = None
            # procura "DE ..." na mesma linha ou na próxima
            nd = detectar_num_data(linha_strip)
            if not nd and i + 1 < n:
                nd = detectar_num_data(linhas[i + 1].strip())
                if nd:
                    i += 1
            if nd:
                num = nd["numero"] or num
                data = nd.get("data")
            atos.append({
                "tipo": tn["tipo"], "numero": num, "ano": ano, "data": data,
                "pagina": pagina, "secao": secao,
                "linha_inicio": i + 1,
            })
            i += 1
            continue

        # gatilho número+data: "Nº 1529, DE 30 DE OUTUBRO DE 2024"
        nd = detectar_num_data(linha_strip)
        if nd and (secao or len(linha_strip) < 40):
            # tipo derivado da seção corrente
            tipo = secao.rstrip("S") if secao else "ATO"
            # corrige plurais/mapeia seção → tipo
            tipo = _tipo_por_secao(secao)
            # ementa na linha seguinte (após o cabeçalho de número)
            ementa = extrair_ementa(linhas, i + 1)
            # órgão: procura nas próximas 6 linhas
            orgao = None
            for j in range(i + 1, min(i + 7, n)):
                o = detectar_orgao(linhas[j].strip())
                if o:
                    orgao = o
                    break
            atos.append({
                "tipo": tipo, "numero": nd["numero"], "ano": None,
                "data": nd.get("data"), "orgao": orgao,
                "pagina": pagina, "secao": secao,
                "ementa": ementa, "linha_inicio": i + 1,
            })
            i += 1
            continue

        i += 1

    # completa órgão/ementa para atos tipo+num
    for a in atos:
        if a.get("orgao") or a.get("ementa"):
            continue
        pass

    # DEDUPLICAÇÃO: remove atos repetidos com mesmo (tipo, numero, pagina)
    # (o número aparece no sumário E no corpo; mantém o 1º que tem ementa/órgão)
    vistos = {}
    unicos = []
    for a in atos:
        chave = (a["tipo"], a["numero"], a["pagina"])
        if chave in vistos:
            # se o já registrado não tem ementa mas este tem, atualiza
            ant = vistos[chave]
            if not ant.get("ementa") and a.get("ementa"):
                ant["ementa"] = a["ementa"]
            if not ant.get("orgao") and a.get("orgao"):
                ant["orgao"] = a["orgao"]
            continue
        vistos[chave] = a
        unicos.append(a)
    return unicos


def _tipo_por_secao(secao: str | None) -> str:
    if not secao:
        return "ATO"
    mapa = {
        "PORTARIAS": "PORTARIA", "PORTARIA": "PORTARIA",
        "DECISÕES": "DECISÃO", "DECISÃO": "DECISÃO",
        "EDITAIS": "EDITAL", "EDITAL": "EDITAL",
        "RESOLUÇÕES": "RESOLUÇÃO", "RESOLUÇÃO": "RESOLUÇÃO",
        "DESPACHOS": "DESPACHO", "DESPACHO": "DESPACHO",
        "AVISOS": "AVISO", "AVISO": "AVISO",
        "EXTRATOS": "EXTRATO", "EXTRATO": "EXTRATO",
        "ATAS": "ATA", "ATA": "ATA",
        "COMUNICADOS": "COMUNICADO", "COMUNICADO": "COMUNICADO",
        "RETIFICAÇÕES": "RETIFICAÇÃO", "RETIFICAÇÃO": "RETIFICAÇÃO",
        "OFÍCIOS": "OFÍCIO", "OFÍCIO": "OFÍCIO",
        "REQUERIMENTOS": "REQUERIMENTO", "REQUERIMENTO": "REQUERIMENTO",
        "INSTRUÇÕES NORMATIVAS": "INSTRUÇÃO NORMATIVA",
        "INSTRUÇÃO NORMATIVA": "INSTRUÇÃO NORMATIVA",
        "DIVERSOS": "ATO",
    }
    return mapa.get(secao, "ATO")


def registrar_boletim(db: sqlite3.Connection, pasta: Path) -> int:
    data = pasta.name
    pdf = next(pasta.glob("*.pdf"), None)
    mds = [m for m in pasta.glob("*.md") if not m.name.startswith("auditoria_")]
    numero = None
    if pdf:
        m = re.search(r"BS-([\d.]+)-(\d{4})", pdf.stem)
        if m:
            numero = f"{m.group(1)}/{m.group(2)}"
    cur = db.execute("SELECT id FROM boletins WHERE data=? AND numero=?", (data, numero))
    row = cur.fetchone()
    if row:
        bid = row[0]
        db.execute("UPDATE boletins SET numero=?, pdf=?, md=? WHERE id=?",
                   (numero, str(pdf) if pdf else None,
                    ",".join(str(m) for m in mds) if mds else None, bid))
    else:
        cur = db.execute("INSERT INTO boletins (data, numero, pdf, md) VALUES (?,?,?,?)",
                         (data, numero, str(pdf) if pdf else None,
                          ",".join(str(m) for m in mds) if mds else None))
        bid = cur.lastrowid
    db.execute("DELETE FROM atos_normativos WHERE boletim_id=?", (bid,))
    return bid


def criar_schema(db: sqlite3.Connection):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS boletins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT NOT NULL,          -- YYYY-MM-DD
        numero TEXT,                 -- "210/2024" ou "210.1/2024"
        pdf TEXT,
        md TEXT,
        UNIQUE(data, numero)
    );

    CREATE TABLE IF NOT EXISTS atos_normativos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        boletim_id INTEGER NOT NULL REFERENCES boletins(id) ON DELETE CASCADE,
        tipo TEXT,                   -- PORTARIA, RESOLUÇÃO, INSTRUÇÃO NORMATIVA...
        numero TEXT,                 -- número do ato
        ano TEXT,                    -- ano do ato
        orgao TEXT,                  -- órgão emissor
        data_ato TEXT,               -- data do ato (YYYY-MM-DD)
        pagina INTEGER,              -- página no boletim
        secao TEXT,                  -- seção do boletim
        ementa TEXT,                 -- resumo provisório do ato
        relevante INTEGER DEFAULT 0, -- 1 = regulamenta funcionamento de processos adm.
        observacao TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_atos_boletim ON atos_normativos(boletim_id);
    CREATE INDEX IF NOT EXISTS idx_atos_tipo ON atos_normativos(tipo);
    """)
    db.commit()


def main():
    ap = argparse.ArgumentParser(description="Catálogo de atos de Boletins de Serviço do MPT")
    ap.add_argument("--raiz", default="boletins", help="dir com pastas YYYY-MM-DD")
    ap.add_argument("--db", default="atos.db", help="caminho do banco sqlite")
    ap.add_argument("--recriar", action="store_true", help="dropa e recria as tabelas")
    args = ap.parse_args()

    raiz = Path(args.raiz)
    if not raiz.is_dir():
        sys.exit(f"❌ Diretório não encontrado: {raiz}")

    db = sqlite3.connect(args.db)
    if args.recriar:
        db.execute("DROP TABLE IF EXISTS atos_normativos")
        db.execute("DROP TABLE IF EXISTS boletins")
    criar_schema(db)

    total_atos = 0
    pastas = sorted([p for p in raiz.iterdir() if p.is_dir() and re.fullmatch(r"\d{4}-\d{2}-\d{2}", p.name)])
    for pasta in pastas:
        mds = [m for m in sorted(pasta.glob("*.md")) if not m.name.startswith("auditoria_")]
        if not mds:
            continue
        bid = registrar_boletim(db, pasta)
        for md in mds:
            for ato in atos_por_arquivo(md):
                db.execute(
                    "INSERT INTO atos_normativos (boletim_id, tipo, numero, ano, orgao, data_ato, pagina, secao, ementa) "
                    "VALUES (?,?,?,?,?,?,?,?,?)",
                    (bid, ato["tipo"], ato["numero"], ato.get("ano"),
                     ato.get("orgao"), ato.get("data"), ato["pagina"],
                     ato.get("secao"), ato.get("ementa", "")),
                )
                total_atos += 1
        n = db.execute("SELECT COUNT(*) FROM atos_normativos WHERE boletim_id=?", (bid,)).fetchone()[0]
        print(f"  {pasta.name}: {len(mds)} MD, {n} atos")

    db.commit()
    print(f"\n✅ Total: {len(pastas)} datas, {total_atos} atos catalogados em {args.db}")


if __name__ == "__main__":
    main()
