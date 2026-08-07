#!/usr/bin/env python3
"""audit_boletim.py — Auditoria de extração de Boletins de Serviço do MPT.

Camada 1 (pré-visão): metadados + contagem de páginas + detecção de páginas
    escaneadas (vazias → OCR necessário).
Camada 2 (estrutural): detecção de atos/publicações dentro do BS usando
    padrões recorrentes (PORTARIA, DESPACHO, AVISO, etc.).
Camada 3 (opcional): extração → Markdown por ato + auditoria de completude,
    cobertura de páginas e fidelidade de volume.

Uso:
    audit_boletim.py <BS.pdf> [--sem-extracao] [--saida DIR]

Saída (em DIR, padrão /workspace):
    <BS>.md              — extração MD por ato (se não --sem-extracao)
    auditoria_<BS>.md    — relatório de auditoria (sempre)

Referência: audit_pgea.py (autos digitais MPT). A estrutura de um BS difere
de um PGEA — não há cabeçalho de peça padronizado. Em vez disso, o BS tem:
1. Cabeçalho (BS Eletrônico - NNN/AAAA - DD/MM/AAAA)
2. Índice/Sumário analítico com a lista de atos publicados
3. Atos individuais (PORTARIA, DESPACHO, AVISO, etc.)
4. Fecho com assinatura da autoridade
"""

import fitz, re, sys
from pathlib import Path
from collections import OrderedDict
from datetime import datetime

WORKSPACE = Path("/workspace")

# ==============================================================
# DETECTORES
# ==============================================================

# Padrão do cabeçalho do BS no topo de cada página ou na primeira página
BS_HEADER_RE = re.compile(
    r"BS\s*Eletr[ôo]nico\s*[-–]\s*(\d+(?:\.\d+)?)/(\d{4})\s*[-–]\s*(\d{2}/\d{2}/\d{4})",
    re.IGNORECASE,
)

# Padrões de atos/publicações dentro do boletim
# Portarias: PORTARIA Nº NNN/AAAA, PORTARIA CONJUNTA, etc.
# Despachos: DESPACHO Nº NNN/AAAA
# Avisos: AVISO Nº NNN/AAAA
# Extratos: EXTRATO DE [...] Nº NNN/AAAA
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

# Padrão alternativo: atos sem número no formato "NOME DO ATO"
ACTO_SIMPLE_RE = re.compile(
    r"^(?P<tipo>(?:PORTARIA|DESPACHO|AVISO|EXTRATO|ATA|DECISÃO|RESOLUÇÃO|"
    r"INSTRUÇÃO\s*NORMATIVA|EDITAL|COMUNICADO|RETIFICAÇÃO|ERRATA|"
    r"ATO|RECOMENDAÇÃO|NOTIFICAÇÃO|INTIMAÇÃO|CITAÇÃO|"
    r"REQUERIMENTO|OFÍCIO|MEMORANDO|PARECER|RELATÓRIO))"
    r"(?:\s+(?:N[º°ª]\s*)?\d+(?:\.\d+)?)?[:\s]",
    re.IGNORECASE,
)

# Índice/Sumário: linhas como "1. PORTARIA...", "1.1.", etc.
SUMARIO_RE = re.compile(r"^\s*(?:\d+(?:\.\d+)*[\.\)]?\s+)?(?:PORTARIA|DESPACHO|AVISO|EXTRATO|ATA|DECISÃO|RESOLUÇÃO|EDITAL|COMUNICADO|RETIFICAÇÃO)", re.IGNORECASE)


def detectar_bs_header(linha):
    """Retorna dict com {numero, ano, data} ou None."""
    m = BS_HEADER_RE.search(linha)
    if m:
        return {"numero": m.group(1), "ano": m.group(2), "data": m.group(3)}
    return None


def detectar_ato(linha):
    """Retorna nome completo do ato (ex: 'PORTARIA Nº 123/2026') ou None."""
    m = ACTO_HEADER_RE.match(linha.strip())
    if m:
        tipo = " ".join(m.group("tipo").split())
        num = m.group(2)
        ano = m.group(3) or ""
        return f"{tipo} Nº {num}{'/' + ano if ano else ''}"
    # Fallback para padrão mais simples
    m = ACTO_SIMPLE_RE.match(linha.strip())
    if m:
        tipo = " ".join(m.group("tipo").split())
        return tipo
    return None


# ==============================================================
# FUNÇÕES DE APOIO
# ==============================================================

def intervalo(pags):
    """Converte lista de páginas em string de intervalos."""
    if not pags:
        return "—"
    ranges, ini, ant = [], None, None
    for p in sorted(pags):
        if ini is None:
            ini = ant = p
        elif p == ant + 1:
            ant = p
        else:
            ranges.append((ini, ant))
            ini = ant = p
    if ini is not None:
        ranges.append((ini, ant))
    return ", ".join(f"{a}-{b}" if a != b else str(a) for a, b in ranges)


def camada1(doc):
    """Camada 1 - Pré-visão: metadados, contagem, páginas vazias."""
    chars = {i + 1: len(doc[i].get_text().strip()) for i in range(doc.page_count)}
    vazias = [p for p, c in chars.items() if p > 1 and c < 50]  # p>1: capa não conta
    meta = {}
    # Tentar extrair cabeçalho do BS da primeira página
    primeira_pag = doc[0].get_text().strip()
    bs_info = detectar_bs_header(primeira_pag)
    if bs_info:
        meta["bs_numero"] = bs_info["numero"]
        meta["bs_ano"] = bs_info["ano"]
        meta["bs_data"] = bs_info["data"]
    return meta, vazias, chars


def camada2(doc):
    """Camada 2 - Estrutural: detectar atos dentro do boletim.

    Retorna (atos: [(nome, [pags])], sumario: [linhas], sem_ato: [pags]).
    """
    atos, atual, pags_sem_ato = [], None, []
    sumario_linhas = []

    for i in range(doc.page_count):
        txt = doc[i].get_text().strip()
        if not txt or i == 0:
            continue  # capa tratada separadamente

        # Tentar detectar ato na primeira linha significativa
        ato = None
        for linha in txt.splitlines():
            linha = linha.strip()
            if len(linha) < 15:
                continue
            ato = detectar_ato(linha)
            if ato:
                break
            # Verificar se é sumário
            if SUMARIO_RE.match(linha):
                sumario_linhas.append(linha)

        if ato:
            if ato != atual:
                atual = ato
                atos.append([atual, []])
        elif atual is None and not sumario_linhas:
            # Antes do primeiro ato e sem sumário — pode ser sumário
            for linha in txt.splitlines():
                if SUMARIO_RE.match(linha.strip()):
                    sumario_linhas.append(linha.strip())

        if atual:
            atos[-1][1].append(i + 1)
        else:
            # Páginas que não foram atribuídas a nenhum ato
            pags_sem_ato.append(i + 1)

    return atos, sumario_linhas, pags_sem_ato


def extrair_md(doc, atos, titulo, sumario_linhas):
    """Gera Markdown por ato com marcadores <!-- pág N -->."""
    blocos = {t: [] for t, _ in atos}
    atual = None

    # Capa (página 1)
    md = [f"# {titulo}\n"]
    md.append(f"> Extração auditada · {len(atos)} atos · {doc.page_count} págs\n")

    capa_txt = doc[0].get_text().strip()
    md.append("## Cabeçalho\n<!-- pág 1 -->\n" + capa_txt)

    # Índice/Sumário
    if sumario_linhas:
        md.append("\n## Sumário/Índice\n" + "\n".join(sumario_linhas))

    # Atos
    for i in range(1, doc.page_count):
        txt = doc[i].get_text().strip()
        if not txt:
            continue

        ato = None
        for linha in txt.splitlines():
            linha = linha.strip()
            if len(linha) < 15:
                continue
            ato = detectar_ato(linha)
            if ato:
                break

        if ato and ato in blocos:
            atual = ato
        elif ato and ato not in blocos:
            # Ato detectado mas não estava no inventário inicial
            atual = ato
            blocos[ato] = []
            atos.append([ato, []])

        if atual and atual in blocos:
            blocos[atual].append(f"\n<!-- pág {i + 1} -->\n{txt}")

    for t, _ in atos:
        if t in blocos and blocos[t]:
            md.append(f"\n## {t}\n" + "\n".join(blocos[t]))

    return "\n".join(md)


def auditar_extracao(doc, md_text, atos, chars, total_pags):
    """Camada 3 - auditoria da extração MD."""
    linhas = []
    md_atos = set(re.findall(r"^## (.+)$", md_text, re.M))
    pag_markers = [int(m) for m in re.findall(r"<!-- pág (\d+) -->", md_text)]
    md_chunks = dict(re.findall(r"<!-- pág (\d+) -->\n(.+?)(?=<!-- pág|\n## |\Z)", md_text, re.S))

    linhas.append("## ✅/❌ Camada 3 — Auditoria da Extração\n")

    # Completude
    nomes_inventario = {t for t, _ in atos}
    faltando = nomes_inventario - md_atos
    sobrando = md_atos - nomes_inventario - {"Cabeçalho", "Sumário/Índice"}
    linhas.append(f"- Atos no inventário: **{len(atos)}** · Seções no MD: **{len(md_atos)}**")
    if faltando:
        linhas.append(f"- ❌ **Ausentes no MD:** {', '.join(faltando)}")
    else:
        linhas.append(f"- ✅ **Ausentes no MD:** nenhum")
    if sobrando:
        linhas.append(f"- ⚠️ **Seções extra sem ato correspondente:** {', '.join(sobrando)}")

    # Cobertura de páginas
    cobertas = {p for p in pag_markers}
    nao_cobertas = [
        p for p in range(1, total_pags + 1)
        if p not in cobertas and p != 1 and chars.get(p, 0) >= 50
    ]
    total_conteudo = sum(1 for p in range(1, total_pags + 1) if chars.get(p, 0) >= 50)
    linhas.append(f"- Páginas com conteúdo: {total_conteudo} · Cobertas: {len(cobertas)}" +
                  (f" · ❌ Faltam: {nao_cobertas}" if nao_cobertas else " ✅"))

    # Fidelidade por volume
    linhas.append("\n| Pág | PDF chars | MD chars | Razão | Verdicto | Ato |")
    linhas.append("|-----|-----------|----------|-------|----------|-----|")
    suspeitas = 0

    # Mapa ato → página
    ato_por_pag = {}
    for t, pags in atos:
        for p in pags:
            ato_por_pag[p] = t

    for p in range(1, total_pags + 1):
        c_pdf = chars.get(p, 0)
        if c_pdf < 50:
            continue
        c_md = len(md_chunks.get(str(p), ""))
        razao = c_md / c_pdf if c_pdf else 0
        nome_ato = ato_por_pag.get(p, "—")

        if c_pdf < 400:
            # Página pequena: comparar conteúdo exato
            raw = re.sub(r"<!-- pág \d+ -->", "", md_chunks.get(str(p), "")).strip()
            ok = raw == doc[p - 1].get_text().strip()
            v = "✅ idêntica" if ok else "❌ divergente"
            if not ok:
                suspeitas += 1
        else:
            v = "✅" if 0.88 <= razao <= 1.18 else ("⚠️" if 0.5 <= razao < 0.88 or 1.18 < razao <= 2 else "❌")
            if v != "✅":
                suspeitas += 1

        linhas.append(f"| {p} | {c_pdf} | {c_md} | {razao:.2f} | {v} | {nome_ato} |")

    linhas.append(f"\n**Pontos suspeitos: {suspeitas}** → para verificação manual (amostral)")
    return "\n".join(linhas)


def main():
    if len(sys.argv) < 2:
        print("Uso: audit_boletim.py <BS.pdf> [--sem-extracao] [--saida DIR]")
        sys.exit(1)

    pdf = Path(sys.argv[1])
    if not pdf.exists():
        print(f"❌ Arquivo não encontrado: {pdf}")
        sys.exit(1)

    sem_ext = "--sem-extracao" in sys.argv
    outdir = Path(sys.argv[sys.argv.index("--saida") + 1]) if "--saida" in sys.argv else WORKSPACE
    outdir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf)
    TOTAL_PAGS = doc.page_count  # guardar ANTES de doc.close()!
    titulo = pdf.stem

    # ==============================================================
    # RELATÓRIO DE AUDITORIA
    # ==============================================================
    rel = [f"# 🔍 Auditoria — {titulo}\n"]

    # Camada 1
    meta, vazias, chars = camada1(doc)
    rel.append("## 📊 Camada 1 — Pré-visão\n")
    rel.append(f"- **Arquivo:** {pdf.name}")
    rel.append(f"- **Páginas:** {TOTAL_PAGS}")
    if meta.get("bs_numero"):
        rel.append(f"- **BS:** {meta.get('bs_numero')}/{meta.get('bs_ano')} · **Data:** {meta.get('bs_data')}")
    rel.append(f"- **Páginas vazias (escaneadas?):** {vazias if vazias else 'nenhuma ✅'}")
    if vazias:
        rel.append(f"  → ⚠️ {len(vazias)} páginas vazias detectadas. Pode ser PDF escaneado — considerar OCR.")

    # Camada 2
    atos, sumario_linhas, pags_sem_ato = camada2(doc)
    rel.append(f"\n## 📑 Camada 2 — Atos Detectados\n")
    rel.append(f"- **Atos encontrados:** {len(atos)}")
    rel.append(f"- **Sumário/Índice detectado:** {'sim ✅' if sumario_linhas else 'não — pode estar embutido no texto'}")
    rel.append(f"- **Páginas sem ato identificado:** {len(pags_sem_ato)} (capa, sumário, fecho — esperado)\n")

    if atos:
        rel.append("| # | Ato | Páginas |")
        rel.append("|---|-----|---------|")
        for idx, (t, pags) in enumerate(atos, 1):
            rel.append(f"| {idx} | {t} | {intervalo(pags)} |")
    else:
        rel.append("⚠️ Nenhum ato detectado com os padrões conhecidos.")
        rel.append("  → Possíveis causas: PDF escaneado (imagem), formato de ato não reconhecido,")
        rel.append("     ou boletim com estrutura atípica.")
        rel.append("  → Solução: extrair texto manualmente e verificar.")

    # Camada 3
    if not sem_ext and atos:
        md_path = outdir / f"{pdf.stem}.md"
        md_path.write_text(extrair_md(doc, atos, titulo, sumario_linhas), encoding="utf-8")

        md_text = md_path.read_text(encoding="utf-8")
        rel.append(f"\n📄 **Extração gerada:** `{md_path.name}`\n")
        rel.append(auditar_extracao(doc, md_text, atos, chars, TOTAL_PAGS))

    elif sem_ext:
        rel.append("\n📄 Extração omitida (--sem-extracao)")

    doc.close()

    # Salvar relatório
    out = outdir / f"auditoria_{pdf.stem}.md"
    out.write_text("\n".join(rel), encoding="utf-8")
    print(f"✅ {out.name} — {len(atos)} atos, {len(vazias)} vazias, suspeitas: {suspeitas if not sem_ext and atos else 'n/a'}")


if __name__ == "__main__":
    main()