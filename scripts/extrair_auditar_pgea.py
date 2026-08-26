#!/usr/bin/env python3
"""extrair_auditar_pgea.py — Extrai e audita PGEAs (autos digitais MPT).

Extrai o PDF para Markdown por peça E audita a extração num comando só.

Camada 1+2 (zero custo): inventário de peças + páginas vazias/escaneadas.
Camada 3 (opcional): extrai o PDF → MD por peça e audita a extração
(completude, cobertura, fidelidade — páginas pequenas comparadas por conteúdo).

Uso:
    extrair_auditar_pgea.py <PGEA.pdf> [--sem-extracao] [--saida DIR]
"""
import fitz, re, sys
from pathlib import Path
from collections import OrderedDict

WORKSPACE = Path("/workspace")

HEADER_RE = re.compile(
    r"^(?P<tipo>[A-ZÀ-Úa-zà-ú ]+?)\s+(?P<num>\d{5,6}\.\d{4})\s*\((?P<id>\d{7,8})\)\s*[−-]\s*PGEA\s",
    re.IGNORECASE,
)

HISTORICO_RE = re.compile(r"[Hh]ist[óo]rico do [Pp]rocedimento|Hist[óo]rico do Procedimento")
CABECALHO_BOLETIM_RE = re.compile(r"^(PROCURADORIA-GERAL\s*\n?.*?(BSE|Boletim)|Boletim de Servi)[a-zãé]", re.I)

def peca_da_linha(linha):
    m = HEADER_RE.match(linha.strip())
    if not m:
        return None
    return f"{' '.join(m.group('tipo').split())} {m.group('num')} ({m.group('id')})"

def intervalo(pags):
    ranges, ini = [], None
    ant = None
    for p in pags:
        if ini is None:
            ini = ant = p
        elif p == ant + 1:
            ant = p
        else:
            ranges.append((ini, ant)); ini = ant = p
    if ini is not None:
        ranges.append((ini, ant))
    return ", ".join(f"{a}-{b}" if a != b else str(a) for a, b in ranges)

def inventario(doc):
    """Retorna (pecas: [(titulo, [pags])], vazias: [pags], chars: {pag: n})."""
    pecas, atual = [], None
    vazias, chars = [], {}
    for i in range(doc.page_count):
        txt = doc[i].get_text().strip()
        chars[i + 1] = len(txt)
        if i == 0 or len(txt) < 30:
            if len(txt) < 30 and i > 0:
                vazias.append(i + 1)
            continue
        peca = None
        for linha in txt.splitlines():
            if len(linha.strip()) < 10:
                continue
            peca = peca_da_linha(linha)
            break
        if peca:
            if peca != atual:
                atual = peca
                pecas.append([atual, []])
        if atual:
            pecas[-1][1].append(i + 1)
    return pecas, vazias, chars

def extrair_md(doc, pecas, titulo):
    """Gera markdown por peça a partir do PDF."""
    blocos = {t: [] for t, _ in pecas}
    atual = None
    for i in range(1, doc.page_count + 1):
        txt = doc[i - 1].get_text().strip()
        if not txt:
            continue
        peca = None
        for linha in txt.splitlines():
            if len(linha.strip()) < 10:
                continue
            peca = peca_da_linha(linha)
            break
        if peca and peca in blocos:
            atual = peca
        if atual:
            blocos[atual].append(f"\n<!-- pág {i} -->\n{txt}")
    md = [f"# {titulo}\n", f"> Extração auditada · {len(pecas)} peças · {doc.page_count} págs\n"]
    md.append("## Capa\n" + doc[0].get_text().strip())
    for t, _ in pecas:
        md.append(f"\n## {t}\n" + "\n".join(blocos[t]))
    return "\n".join(md)

def main():
    pdf = Path(sys.argv[1])
    sem_ext = "--sem-extracao" in sys.argv
    outdir = Path(sys.argv[sys.argv.index("--saida") + 1]) if "--saida" in sys.argv else WORKSPACE
    outdir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf)
    pecas, vazias, chars = inventario(doc)
    titulo = pdf.stem
    rel = [f"# 🔍 Auditoria — {titulo}\n",
           f"- **Páginas:** {doc.page_count} · **Peças:** {len(pecas)}",
           f"- **Páginas vazias (escaneadas?):** {vazias if vazias else 'nenhuma — PDF 100% digital ✅'}\n",
           "| # | Peça | Páginas |", "|---|------|---------|"]
    for idx, (t, pags) in enumerate(pecas, 1):
        rel.append(f"| {idx} | {t} | {intervalo(pags)} |")

    if not sem_ext:
        md_path = outdir / f"{pdf.stem}.md"
        md_path.write_text(extrair_md(doc, pecas, titulo), encoding="utf-8")
        # auditoria da extração
        md_text = md_path.read_text(encoding="utf-8")
        md_pecas = set(re.findall(r"^## (.+)$", md_text, re.M))
        pag_markers = [int(m) for m in re.findall(r"<!-- pág (\d+) -->", md_text)]
        md_chunks = dict(re.findall(r"<!-- pág (\d+) -->\n(.+?)(?=<!-- pág|\n## |\Z)", md_text, re.S))

        rel.append("\n## ✅/❌ Camada 3 — Auditoria da extração")
        faltando = [t for t, _ in pecas if t not in md_pecas]
        rel.append(f"- Peças no inventário: **{len(pecas)}** · Seções no MD: **{len(md_pecas)}**")
        rel.append(f"- **Ausentes no MD:** {faltando if faltando else 'nenhuma ✅'}")
        cobertas = [p for p in range(1, doc.page_count + 1) if p in pag_markers]
        nao_cobertas = [p for p in range(1, doc.page_count + 1) if p not in pag_markers and p != 1 and chars[p] >= 30]
        rel.append(f"- Páginas com conteúdo cobertas: {len(cobertas)}/{sum(1 for p in range(1, doc.page_count+1) if chars[p] >= 30)}"
                   + (f" · ❌ Faltam: {nao_cobertas}" if nao_cobertas else " ✅"))

        # fidelidade: páginas pequenas por conteúdo exato; grandes por razão de volume
        rel.append("\n| Pág | PDF chars | MD chars | Razão | Verdicto |")
        rel.append("|-----|-----------|----------|-------|----------|")
        suspeitas = 0
        for p in range(2, doc.page_count + 1):
            c_pdf = chars[p]
            if c_pdf < 30:
                continue
            c_md = len(md_chunks.get(str(p), ""))
            razao = c_md / c_pdf if c_pdf else 0
            if c_pdf < 500:
                # página pequena: compara conteúdo exato (lição do PGEA 281)
                raw = re.sub(r"<!-- pág \d+ -->", "", md_chunks.get(str(p), "")).strip()
                ok = raw == doc[p - 1].get_text().strip()
                v = "✅ idêntica" if ok else "❌ divergente"
                if not ok:
                    suspeitas += 1
            else:
                v = "✅" if 0.9 <= razao <= 1.15 else ("⚠️" if 0.5 <= razao < 0.9 or 1.15 < razao <= 2 else "❌")
                if v != "✅":
                    suspeitas += 1
            rel.append(f"| {p} | {c_pdf} | {c_md} | {razao:.2f} | {v} |")
        rel.append(f"\n**Pontos suspeitos: {suspeitas}** → para judge LLM (amostral)")
        rel.append(f"\n📄 Extração gerada: `{md_path.name}`")

    doc.close()
    out = outdir / f"auditoria_{pdf.stem}.md"
    out.write_text("\n".join(rel), encoding="utf-8")
    print(f"✅ {out.name} — {len(pecas)} peças, {len(vazias)} vazias, suspeitas: {suspeitas if not sem_ext else 'n/a'}")

if __name__ == "__main__":
    main()
