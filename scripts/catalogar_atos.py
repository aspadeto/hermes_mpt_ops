#!/usr/bin/env python3
"""catalogar_atos.py — Catálogo de atos normativos de Boletins de Serviço do MPT.

Varre os arquivos .md extraídos (pastas YYYY-MM-DD) de Boletins de Serviço,
detecta os atos normativos publicados e popula um banco SQLite com:
    - identificação do ato (tipo, número, órgão, data)
    - referência ao boletim (número + data + pasta) e página
    - resumo/ementa do ato
    - flag de relevância para regulamentação de processos administrativos

Uso:
    python3 catalogar_atos.py                 # usa ./boletins e atos.db por padrão
    python3 catalogar_atos.py --raiz DIR      # dir com pastas YYYY-MM-DD
    python3 catalogar_atos.py --db ARQ        # caminho do banco sqlite
    python3 catalogar_atos.py --recriar       # dropa e recria as tabelas
"""

import argparse
import re
import sqlite3
import sys
from pathlib import Path

# ---------------------------------------------------------------
# Padrões de atos (reaproveitados de audit_boletim.py)
# ---------------------------------------------------------------
ACTO_HEADER_RE = re.compile(
    r"^(?P<tipo>(?:PORTARIA\s*(?:CONJUNTA|CONJ|NORMATIVA|CONJUNTA\s*NORMATIVA|"
    r"CONJUNTA\s*ADMINISTRATIVA)?|"
    r"DESPACHO(?:\s*(?:ADMINISTRATIVO|DA\s*DIREÇÃO|DA\s*SECRETARIA))?|"
    r"AVISO|EXTRATO\s*(?:DE\s*)?(?:INEXIGIBILIDADE|DISPENSA|CONTRATO|"
    r"CONV[EÊ]NIO|ACORDO\s*(?:DE\s*)?COOPERAÇÃO|TERMO\s*(?:ADITIVO|DE\s*)?)?|"
    r"ATA\s*(?:DE\s*)?(?:REGISTRO\s*DE\s*PREÇOS|SESSÃO)?|"
    r"DECISÃO|RESOLUÇÃO|INSTRUÇÃO\s*NORMATIVA|"
    r"EDITAL|COMUNICADO|RETIFICAÇÃO|ERRATA|"
    r"ATO\s*(?:DO\s*(?:PROCURADOR|DIRETOR|SECRETÁRIO))?|"
    r"RECOMENDAÇÃO|NOTIFICAÇÃO|INTIMAÇÃO|CITAÇÃO|"
    r"REQUERIMENTO|OFÍCIO|MEMORANDO|PARECER|RELATÓRIO"
    r"))\s*(?:N[º°ª]|N[úu]mero)?\s*(\d+(?:\.\d+)?(?:[A-Z])?)\s*(?:/\s*(\d{4}))?\b",
    re.IGNORECASE,
)

# "Nº 1529, DE 30 DE OUTUBRO DE 2024" — número e data do ato
NUM_DATA_RE = re.compile(
    r"N[º°ª]\s*(\d+(?:\.\d+)?[A-Z]?)\s*(?:DE\s+(\d{1,2}))?\s*(?:DE\s+([A-ZÇÃÊÓÍ]+))?\s*(?:DE\s+(\d{4}))?",
    re.IGNORECASE,
)

# Órgão emissor: linhas como "O PROCURADOR-GERAL DO TRABALHO," / "A CORREGEDORA-GERAL..."
ORGAO_RE = re.compile(
    r"^(?:O|A)\s+(?P<orgao>"
    r"(?:SUBPROCURADOR(?:A)?|PROCURADOR(?:A)?|CORREGEDOR(?:A)?|DIRETOR(?:A)?|SECRETÁRIO|"
    r"OUVIDOR|COORDENADOR(?:A)?)[A-ZÀ-Ú\s]*-?\s*"
    r"(?:GERAL(?: DO TRABALHO)?|DA DIRETORIA|DE GESTÃO|EXECUTIVO[A-ZÀ-Ú\s]*)?)"
    r"[A-ZÀ-Ú\s]*,",
    re.IGNORECASE,
)

# Sumário: linhas do índice "1. PORTARIA ..." (ignorar)
SUMARIO_RE = re.compile(r"^\s*\d+(\.\d+)*[\.,\)]?\s+(?:PORTARIA|DESPACHO|AVISO|EXTRATO|ATA|DECISÃO|RESOLUÇÃO|EDITAL|COMUNICADO|RETIFICAÇÃO)", re.IGNORECASE)


def pagina_de(md_text: str, offset: int) -> int:
    """Acha o número da página mais próximo ANTES do offset (marcador <!-- pág N -->)."""
    antes = md_text[:offset]
    m = re.findall(r"<!-- pág (\d+) -->", antes)
    return int(m[-1]) if m else 0


def detectar_ato_em(bloco: str) -> dict | None:
    """Detecta tipo/número/ano de um ato a partir do início do bloco de texto."""
    for linha in bloco.splitlines():
        linha = linha.strip()
        if len(linha) < 8 or SUMARIO_RE.match(linha):
            continue
        m = ACTO_HEADER_RE.match(linha)
        if m:
            tipo = " ".join(m.group("tipo").split())
            num = m.group(2)
            ano = m.group(3)
            # número e data do ato (pode estar em linha seguinte: "Nº 1529, DE 30 DE OUTUBRO DE 2024")
            m2 = NUM_DATA_RE.search(linha)
            num_ato = num
            if m2 and m2.group(1):
                num_ato = m2.group(1)
            return {
                "tipo": tipo.upper(),
                "numero": num_ato,
                "ano": ano,
                "linha": linha,
            }
    return None


def detectar_orgao(bloco: str) -> str | None:
    for linha in bloco.splitlines():
        linha = linha.strip()
        m = ORGAO_RE.match(linha)
        if m:
            return " ".join(m.group("orgao").split()).upper()
    return None


def extrair_ementa(bloco: str, max_chars: int = 500) -> str:
    """Pega o início significativo do ato como ementa/resumo provisório."""
    linhas = []
    for linha in bloco.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        if linha.startswith("PROCURADORIA") or linha.startswith("BSE ") or linha.startswith("CIRCULAÇÃO"):
            continue
        if re.fullmatch(r"\d+", linha):  # número de página
            continue
        linhas.append(linha)
        if sum(len(l) for l in linhas) >= max_chars:
            break
    return " ".join(linhas)[:max_chars]


def atos_por_arquivo(md: Path) -> list[dict]:
    """Extrai atos de um .md extraído (seções ## ... com marcadores <!-- pág N -->)."""
    txt = md.read_text(encoding="utf-8")
    # divide nas seções de nível 2
    secoes = []
    for m in re.finditer(r"^## (.+?)\s*$", txt, re.M):
        secoes.append((m.start(), m.group(1).strip()))
    atos = []
    for i, (start, nome_secao) in enumerate(secoes):
        end = secoes[i + 1][0] if i + 1 < len(secoes) else len(txt)
        bloco = txt[start:end]
        pagina = pagina_de(txt, start + 5)
        det = detectar_ato_em(bloco) or {}
        if not det:
            # usa o nome da seção como fallback
            det = {"tipo": nome_secao.upper(), "numero": None, "ano": None, "linha": nome_secao}
        org = detectar_orgao(bloco)
        atos.append({
            "secao": nome_secao,
            "tipo": det.get("tipo", "?"),
            "numero": det.get("numero"),
            "ano": det.get("ano"),
            "orgao": org,
            "pagina": pagina,
            "ementa": extrair_ementa(bloco),
        })
    return atos


def registrar_boletim(db: sqlite3.Connection, pasta: Path) -> int:
    """Insere/atualiza o boletim na tabela e retorna o id."""
    # pasta é YYYY-MM-DD
    data = pasta.name
    pdf = next(pasta.glob("*.pdf"), None)
    md = next(pasta.glob("*.md"), None)
    # número do boletim a partir do nome do arquivo (ex: BS-210.1-2024)
    numero = None
    if pdf:
        m = re.search(r"BS-([\d.]+)-(\d{4})", pdf.stem)
        if m:
            numero = f"{m.group(1)}/{m.group(2)}"
    cur = db.execute("SELECT id FROM boletins WHERE data=? AND numero=?", (data, numero))
    row = cur.fetchone()
    if row:
        bid = row[0]
        db.execute(
            "UPDATE boletins SET numero=?, pdf=?, md=? WHERE id=?",
            (numero, str(pdf) if pdf else None, str(md) if md else None, bid),
        )
    else:
        cur = db.execute(
            "INSERT INTO boletins (data, numero, pdf, md) VALUES (?,?,?,?)",
            (data, numero, str(pdf) if pdf else None, str(md) if md else None),
        )
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
        data_ato TEXT,               -- data do ato (se detectada)
        pagina INTEGER,              -- página no boletim
        ementa TEXT,                 -- resumo provisório do ato
        relevante INTEGER DEFAULT 0, -- 1 = regulamenta funcionamento de processos adm.
        observacao TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_atos_boletim ON atos_normativos(boletim_id);
    CREATE INDEX IF NOT EXISTS idx_atos_tipo ON atos_normativos(tipo);
    """)
    db.commit()


def main():
    ap = argparse.ArgumentParser(description="Catálogo de atos normativos de Boletins de Serviço do MPT")
    ap.add_argument("--raiz", default="boletins", help="dir com pastas YYYY-MM-DD (padrão: boletins)")
    ap.add_argument("--db", default="atos.db", help="caminho do banco sqlite (padrão: atos.db)")
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
        mds = sorted(pasta.glob("*.md"))
        # ignora arquivos de auditoria (auditoria_*.md)
        mds = [m for m in mds if not m.name.startswith("auditoria_")]
        if not mds:
            continue
        bid = registrar_boletim(db, pasta)
        for md in mds:
            for ato in atos_por_arquivo(md):
                db.execute(
                    "INSERT INTO atos_normativos (boletim_id, tipo, numero, ano, orgao, pagina, ementa) "
                    "VALUES (?,?,?,?,?,?,?)",
                    (bid, ato["tipo"], ato["numero"], ato["ano"], ato["orgao"], ato["pagina"], ato["ementa"]),
                )
                total_atos += 1
        print(f"  {pasta.name}: {len(mds)} arquivo(s) MD")
        # contagem de atos por boletim
        n = db.execute("SELECT COUNT(*) FROM atos_normativos WHERE boletim_id=?", (bid,)).fetchone()[0]
        print(f"    → {n} atos catalogados")

    db.commit()
    print(f"\n✅ Total: {len(pastas)} datas, {total_atos} atos catalogados em {args.db}")


if __name__ == "__main__":
    main()
