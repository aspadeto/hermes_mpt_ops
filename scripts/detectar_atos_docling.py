#!/usr/bin/env python3
"""detectar_atos_docling.py — Detecta atos normativos em .md docling de boletins.

Lê os markdown ESTRUTURADOS gerados pelo Docling (hermes_mpt_kb/boletins_docling/)
e detecta os atos publicados. Diferente do parser para MD plano (catalogar_atos.py),
este entende a estrutura do docling:

  - Atos como heading  :  "## Nº 56, DE 15 DE JANEIRO DE 2025"
  - Atos como linha    :  "Nº 1124, DE 4 DE AGOSTO DE 2025"  (linha solta)
  - Tipo explícito     :  "## DECISÃO N°111.2025" / "## DESPACHO Nº 1663.2025"
  - Seções             :  "## PORTARIAS" / "## ATOS DO PROCURADOR-GERAL" / "## ATOS DAS PROCURADORIAS REGIONAIS"
  - Órgão/assinatura   :  "## GLÁUCIO ..." (nome) ou linha "O PROCURADOR-GERAL ... RESOLVE"
  - Tabelas Markdown   :  "| Chefe de Gabinete | CC-4 |"

O ano do boletim vem do NOME do arquivo (BS-012-2025 → 2025), pois o docling não
tem frontmatter.

Uso:
    python3 -c "import sys; sys.path.insert(0,'scripts'); import detectar_atos_docling as d; ..."
"""

import re
from pathlib import Path

# ------------------------------------------------------------
# Regex de cabeçalho de ato: "Nº 56, DE 15 DE JANEIRO DE 2025" ou "Nº 56, DE 15/01/2025"
# Aceita Nº / N° / N. e dia "1°" / "1º"
# ------------------------------------------------------------
NUM_DATA_RE = re.compile(
    r"^N[º°\.]\s*(\d+(?:\.\d+)?[A-Za-z]?)\s*,?\s*DE\s+"
    r"(?:(\d{1,2})[º°]?\s+DE\s+)?"
    r"([A-ZÇÃÊÓÍ][a-zçãêóí]+|\d{1,2})"
    r"(?:\s*/\s*(\d{2,4}))?\s*(?:DE\s+(\d{4}))?\s*$",
    re.IGNORECASE,
)

# Tipo + número explícito: "DECISÃO N°111.2025" / "DESPACHO Nº 1663.2025" / "PORTARIA Nº 1030/2024"
TIPO_NUM_RE = re.compile(
    r"^(?P<tipo>PORTARIA(?:\s+(?:CONJUNTA|NORMATIVA|ADMINISTRATIVA))?|"
    r"DESPACHO|DECISÃO|RESOLUÇÃO|EDITAL|AVISO|EXTRATO|ATA|"
    r"INSTRUÇÃO\s+NORMATIVA|COMUNICADO|RETIFICAÇÃO|ERRATA|ATO|RECOMENDAÇÃO|OFÍCIO|"
    r"REQUERIMENTO|PARECER|RELATÓRIO|MEMORANDO)"
    r"\s*N[º°\.]\s*(\d+(?:\.\d+)?[A-Za-z]?)(?:\s*/\s*(\d{4}))?",
    re.IGNORECASE,
)

# Órgão emissor (em linha solta): "O PROCURADOR-GERAL DO TRABALHO ," / "A DIRETORA DE ADMINISTRAÇÃO..."
ORGAO_RE = re.compile(
    r"^(?:O|A)\s+(?P<orgao>[A-ZÀ-Ú][A-ZÀ-Úa-zà-ú\-]*(?:[A-ZÀ-Úa-zà-ú\s\-]*?))\s*,?\s*(?:no uso|$)",
    re.IGNORECASE,
)

# Mapeia seção → tipo de ato (singular)
SECAO_TIPO = {
    "PORTARIAS": "PORTARIA",
    "DECISÕES": "DECISÃO",
    "DECISÃO": "DECISÃO",
    "EDITAIS": "EDITAL",
    "EDITAL": "EDITAL",
    "RESOLUÇÕES": "RESOLUÇÃO",
    "RESOLUÇÃO": "RESOLUÇÃO",
    "DESPACHOS": "DESPACHO",
    "DESPACHO": "DESPACHO",
    "AVISOS": "AVISO",
    "AVISO": "AVISO",
    "EXTRATOS": "EXTRATO",
    "ATAS": "ATA",
    "COMUNICADOS": "COMUNICADO",
    "COMUNICADO": "COMUNICADO",
    "RETIFICAÇÕES": "RETIFICAÇÃO",
    "RETIFICAÇÃO": "RETIFICAÇÃO",
    "OFÍCIOS": "OFÍCIO",
    "OFÍCIO": "OFÍCIO",
    "REQUERIMENTOS": "REQUERIMENTO",
    "INSTRUÇÕES NORMATIVAS": "INSTRUÇÃO NORMATIVA",
    "INSTRUÇÃO NORMATIVA": "INSTRUÇÃO NORMATIVA",
}

MESES = {
    "janeiro": "01", "fevereiro": "02", "março": "03", "abril": "04",
    "maio": "05", "junho": "06", "julho": "07", "agosto": "08",
    "setembro": "09", "outubro": "10", "novembro": "11", "dezembro": "12",
}

# Cabeçalhos de unidade/regional (não são atos)
UNIDADE_RE = re.compile(
    r"^(?:PRT-?\s*\d+|PTM-|PROCURADORIA REGIONAL|BOLETIM|MINISTÉRIO|CIRCULAÇÃO|BSE|EQUIPE|SUPERVISÃO)",
    re.IGNORECASE,
)


def ano_do_arquivo(md: Path) -> str | None:
    """Extrai o ano do nome do arquivo BS-012-2025 → 2025."""
    m = re.search(r"(\d{4})\.md$", md.name)
    return m.group(1) if m else None


def numero_boletim(md: Path) -> str:
    """BS-012-2025 → '12/2025' ; BS-7.1-2025 → '7.1/2025'."""
    stem = md.stem  # BS-012-2025
    m = re.match(r"BS-(\d+(?:\.\d+)*)-(\d{4})", stem, re.IGNORECASE)
    return f"{m.group(1)}/{m.group(2)}" if m else stem


def _normalizar_data(dia: str | None, mes: str | None, ano: str | None) -> str | None:
    """Monta YYYY-MM-DD a partir de dia/mês-nome/ano."""
    if not (dia and mes and ano):
        return None
    mes_num = MESES.get(mes.lower())
    if not mes_num:
        # pode ser numérico (DD/MM/AAAA) já tratado pelo NUM_DATA_RE
        return None
    try:
        return f"{int(ano):04d}-{mes_num}-{int(dia):02d}"
    except ValueError:
        return None


def _limpar_heading(linha: str) -> str:
    """Remove prefixo de heading markdown '## '."""
    return re.sub(r"^#{1,6}\s*", "", linha).strip()


def _tipo_por_secao(secao: str | None) -> str:
    if not secao:
        return "ATO"
    s = secao.strip().upper()
    for k, v in SECAO_TIPO.items():
        if k in s or s in k:
            return v
    return "ATO"


def _inferir_tipo_de_trecho(trecho: str) -> str | None:
    """Infere o tipo de ato a partir do conteúdo, quando a seção é genérica
    (ex: 'ATOS DA DIRETORIA-GERAL'). Heurísticas conservadoras."""
    t = trecho.upper()
    # verbos/contextos que indicam o tipo
    if "DESIGNA" in t or "DESIGNAR" in t or "NOMEAR" in t or "ALTERA A PORTARIA" in t \
       or "ESTRUTURA ORGANIZACIONAL" in t or "REESTRUTURA" in t or "APROVA" in t:
        return "PORTARIA"
    if "RESOLVE" in t or "RESOLVO" in t or "DECIDE" in t:
        return "DECISÃO"
    if "HOMOLOGA" in t or "HOMOLOGAR" in t:
        return "PORTARIA"
    if "DISPÕE" in t or "DISPÕE SOBRE" in t or "INSTITUI" in t or "REGULAMENTA" in t:
        return "PORTARIA"
    if "EXPEDE" in t or "OFÍCIO" in t:
        return "OFÍCIO"
    return None


def extrair_ementa(linhas: list[str], inicio: int, max_chars: int = 350) -> str:
    """Coleta as linhas após o cabeçalho do ato, até achar um novo heading ou assinatura."""
    partes = []
    i = inicio
    n = len(linhas)
    while i < n and len(" ".join(partes)) < max_chars:
        l = linhas[i].strip()
        # para em novo heading ##  (novo ato/seção/assinatura), marcador de imagem, ou fim
        if l.startswith("##") or l.startswith("<!--") or not l:
            # não quebra se ainda não juntou nada (pule linhas em branco)
            if partes:
                break
            i += 1
            continue
        # para em padrão de assinatura/órgão
        if re.match(r"^(?:O|A)\s+(?:PROCURADOR|DIRETOR|SUBPROCURADOR|CORREGEDOR|SECRETÁRIO)", l):
            if partes:
                break
            i += 1
            continue
        # pula linha de regional/unidade
        if UNIDADE_RE.match(l) or re.fullmatch(r"\d+", l):
            i += 1
            continue
        # pula cabeçalho de tabela isolado
        if l.startswith("|") and set(l) <= set("|-: "):
            i += 1
            continue
        partes.append(l)
        i += 1
    return " ".join(p for p in partes if p)[:max_chars]


def atos_por_arquivo_docling(md: Path) -> list[dict]:
    """Detecta atos no markdown docling de um boletim."""
    txt = md.read_text(encoding="utf-8")
    linhas = txt.splitlines()
    ano_bs = ano_do_arquivo(md)

    atos = []
    secao = None
    pagina = 0
    i = 0
    n = len(linhas)

    while i < n:
        raw = linhas[i]
        linha = raw.strip()
        # conta imagens como proxy de página (docling não tem <!-- pág N -->)
        if "<!-- image -->" in linha:
            pagina += 1
            i += 1
            continue

        # seção: heading puro tipo "## PORTARIAS", "## ATOS DO PROCURADOR-GERAL"
        m_head = re.match(r"^##\s+(.+)$", linha)
        if m_head:
            cab = m_head.group(1).strip()
            # se for seção reconhecida, atualiza
            tipo_secao = _tipo_por_secao(cab)
            # seção genuína (plural/reconhecida) OU "ATOS DA ..."
            if cab.upper() in SECAO_TIPO or re.match(r"^ATOS\s+(?:DA|DAS|DO|DOS)", cab, re.IGNORECASE) or \
               tipo_secao != "ATO" and len(cab) < 40:
                # pode ser "## PORTARIAS" (seção) ou "## DECISÃO N°111.2025" (ato explícito)
                tn = TIPO_NUM_RE.match(cab)
                if tn:
                    # ato com tipo explícito
                    num = tn.group(2)
                    ano_ato = tn.group(3) or ano_bs
                    atos.append({
                        "tipo": tn.group(1).upper(), "numero": num, "ano": ano_ato,
                        "data": None, "orgao": None, "pagina": pagina, "secao": secao,
                        "ementa": extrair_ementa(linhas, i + 1), "linha_inicio": i + 1,
                    })
                    i += 1
                    continue
                if cab.upper() in SECAO_TIPO:
                    secao = cab.upper()
                else:
                    secao = cab.upper()
                i += 1
                continue
            # heading Nº (ato): "## Nº 56, DE 15 DE JANEIRO DE 2025"
            nd = NUM_DATA_RE.match(cab)
            if nd:
                data = _normalizar_data(nd.group(2), nd.group(3), nd.group(5))
                tipo = _tipo_por_secao(secao)
                ementa = extrair_ementa(linhas, i + 1)
                # se seção genérica (ATO), infere tipo do conteúdo
                if tipo == "ATO":
                    tipo_inf = _inferir_tipo_de_trecho(ementa)
                    if tipo_inf:
                        tipo = tipo_inf
                # órgão: procurar nas próximas 8 linhas uma assinatura
                orgao = None
                for j in range(i + 1, min(i + 8, n)):
                    oj = ORGAO_RE.match(linhas[j].strip())
                    if oj:
                        org = oj.group("orgao")
                        if org and len(org) < 120 and not UNIDADE_RE.match(org):
                            orgao = " ".join(org.split()).upper()
                        break
                atos.append({
                    "tipo": tipo, "numero": nd.group(1), "ano": nd.group(5) or ano_bs,
                    "data": data, "orgao": orgao, "pagina": pagina, "secao": secao,
                    "ementa": ementa, "linha_inicio": i + 1,
                })
                i += 1
                continue
            # heading de nome próprio (GLÁUCIO...) → não é ato, só avança
            i += 1
            continue

        # linha solta (não heading): pode ser "Nº 1124, DE 4 DE AGOSTO DE 2025"
        tn = TIPO_NUM_RE.match(linha)
        if tn:
            num = tn.group(2)
            ano_ato = tn.group(3) or ano_bs
            atos.append({
                "tipo": tn.group(1).upper(), "numero": num, "ano": ano_ato,
                "data": None, "orgao": None, "pagina": pagina, "secao": secao,
                "ementa": extrair_ementa(linhas, i + 1), "linha_inicio": i + 1,
            })
            i += 1
            continue

        nd = NUM_DATA_RE.match(linha)
        if nd and (secao or len(linha) < 40):
            data = _normalizar_data(nd.group(2), nd.group(3), nd.group(5))
            tipo = _tipo_por_secao(secao)
            ementa = extrair_ementa(linhas, i + 1)
            # se seção genérica (ATO), infere tipo do conteúdo
            if tipo == "ATO":
                tipo_inf = _inferir_tipo_de_trecho(ementa)
                if tipo_inf:
                    tipo = tipo_inf
            orgao = None
            for j in range(i + 1, min(i + 8, n)):
                oj = ORGAO_RE.match(linhas[j].strip())
                if oj:
                    org = oj.group("orgao")
                    if org and len(org) < 120 and not UNIDADE_RE.match(org):
                        orgao = " ".join(org.split()).upper()
                    break
            atos.append({
                "tipo": tipo, "numero": nd.group(1), "ano": nd.group(5) or ano_bs,
                "data": data, "orgao": orgao, "pagina": pagina, "secao": secao,
                "ementa": ementa, "linha_inicio": i + 1,
            })
            i += 1
            continue

        i += 1

    return atos


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("uso: detectar_atos_docling.py <arquivo.md>")
        sys.exit(1)
    md = Path(sys.argv[1])
    for a in atos_por_arquivo_docling(md):
        print(f"{a.get('tipo')} Nº{a.get('numero')} ano={a.get('ano')} "
              f"data={a.get('data')} sec={a.get('secao')} org={a.get('orgao','')} "
              f"ementa={(a.get('ementa') or '')[:60]}")
