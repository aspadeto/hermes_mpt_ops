#!/usr/bin/env python3
"""
pdf2wiki.py — Converte PDF em Markdown + assets para a wiki PRT14.

Uso:
    python3 pdf2wiki.py <arquivo.pdf> [--dest pasta] [--render-tabelas]

Comportamento:
    1. Extrai texto por página (fiel ao original)
    2. Detecta tabelas (find_tables) → converte para Markdown
    3. Extrai imagens bitmap → salva em assets/ (referenciadas no MD)
    4. Renderiza como PNG as páginas que contêm tabelas (fallback visual
       para células mescladas / layout complexo que o MD não replica)
    5. Gera frontmatter YAML compatível com a wiki
    6. Copia o PDF original como fonte imutável

Estrutura de saída (padrão: wiki/raw/articles/<slug>/):
    artigo.md          ← Markdown convertido (fonte principal de pesquisa)
    assets/            ← imagens e páginas renderizadas
    fonte.pdf          ← PDF original

Dependências: PyMuPDF (pymupdf)
"""

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

# Importa configuração centralizada de caminhos
from ops_paths import KB_PATH, KB_RAW_BOLETINS, KB_BOLETINS, KB_DATA

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("Erro: PyMuPDF não instalado. Use: uv venv .venv && uv pip install pymupdf")


def slugify(texto: str) -> str:
    """Gera slug seguro para nome de pasta."""
    slug = re.sub(r"[^\w\s-]", "", texto.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or "documento"


def detectar_titulo(doc: fitz.Document) -> tuple[str, str | None]:
    """
    Tenta extrair o título do documento.
    Ordem: metadados → primeira página (maior fonte).
    Retorna (titulo, titulo_en).
    """
    # 1. Metadados
    md_titulo = (doc.metadata.get("title") or "").strip()
    if md_titulo and md_titulo.lower() != "untitled":
        return md_titulo, None

    # 2. Primeira página: procura spans com a maior fonte (título em destaque)
    if len(doc) > 0:
        page = doc[0]
        dados = page.get_text("dict")
        spans = []
        for bloco in dados.get("blocks", []):
            for linha in bloco.get("lines", []):
                for span in linha.get("spans", []):
                    texto = span.get("text", "").strip()
                    if texto and len(texto) > 3:
                        spans.append((span.get("size", 0), texto, span.get("flags", 0)))

        if spans:
            # Título = spans com a maior fonte
            max_size = max(s[0] for s in spans)
            # Junta spans consecutivos com fonte >= 85% da maior
            limiar = max_size * 0.85
            titulo_spans = [s[1] for s in spans if s[0] >= limiar]
            if titulo_spans:
                return " ".join(titulo_spans), None

    return "", None


def detectar_autores(doc: fitz.Document) -> list[str]:
    """Tenta extrair nomes de autores da primeira página.

    Heurística: nomes de autor são linhas CURTAS (< 60 chars), SEM ponto final,
    que aparecem ANTES de uma bio (linha longa começando com Mestre/Doutor/
    Especialista/Graduado/Servidor/Professor/Técnica).
    """
    if len(doc) == 0:
        return []
    texto = doc[0].get_text("text")
    # Autores podem continuar na página 2 (bios longas quebram layout)
    if len(doc) > 1 and any(k in doc[1].get_text("text") for k in ["Lattes:", "Orcid:", "E-mail:"]):
        texto += "\n" + doc[1].get_text("text")
    linhas = [l.strip() for l in texto.split("\n") if l.strip()]

    autores: list[str] = []
    for i, linha in enumerate(linhas):
        # Critérios para ser NOME de autor:
        # - 2+ palavras (até 6 — nomes compostos)
        # - Curta (< 60 chars) — bios são longas
        # - Sem ponto final no fim (bios terminam com .)
        # - Primeira letra maiúscula (nome próprio)
        palavras = linha.split()
        if not (2 <= len(palavras) <= 6):
            continue
        if len(linha) > 60 or linha.endswith("."):
            continue
        if not linha[0].isupper():
            continue
        # Evita headers/números/cabeçalhos de página
        if linha.isdigit() or "revista" in linha.lower() or "julho" in linha.lower():
            continue

        # A linha seguinte deve parecer uma bio de autor
        prox = linhas[i + 1] if i + 1 < len(linhas) else ""
        if any(prox.startswith(k) for k in ["Mestre", "Mestra", "Doutor", "Doutora",
                                            "Especialista", "Graduado", "Graduada",
                                            "Servidor", "Servidora", "Professor",
                                            "Professora", "Técnica", "Técnico",
                                            "Mestranda", "Doutoranda", "Pós-graduado",
                                            "Bacharel", "Bacharela"]):
            autores.append(linha)

    # Dedupe preservando ordem
    vistos = set()
    unicos = []
    for a in autores:
        if a not in vistos:
            vistos.add(a)
            unicos.append(a)
    return unicos


def extrair_imagem(doc: fitz.Document, xref: int, dest: Path, prefixo: str) -> str | None:
    """Extrai uma imagem bitmap do PDF e salva em dest. Retorna nome do arquivo."""
    try:
        info = doc.extract_image(xref)
        ext = info["ext"]  # png, jpeg, etc.
        nome = f"{prefixo}-img-{xref}.{ext}"
        (dest / nome).write_bytes(info["image"])
        return nome
    except Exception:
        return None


def tabela_para_markdown(tabela) -> str:
    """Converte uma tabela PyMuPDF para Markdown."""
    dados = tabela.extract()
    if not dados:
        return ""

    linhas = []
    for linha in dados:
        # Normaliza células: None → vazio, quebras de linha → espaço
        células = []
        for c in linha:
            if c is None:
                células.append("")
            else:
                células.append(re.sub(r"\s*\n\s*", " ", str(c)).strip())
        linhas.append(células)

    if not linhas:
        return ""

    n_cols = max(len(l) for l in linhas)
    # Preenche linhas com menos colunas
    linhas = [l + [""] * (n_cols - len(l)) for l in linhas]

    # Cabeçalho = primeira linha; separador = segunda; resto = dados
    out = []
    cab = linhas[0]
    out.append("| " + " | ".join(cab) + " |")
    out.append("|" + "|".join(["---"] * n_cols) + "|")
    for l in linhas[1:]:
        out.append("| " + " | ".join(l) + " |")
    return "\n".join(out)


def converter_pdf(pdf_path: Path, dest: Path, render_tabelas: bool, dpi: int) -> tuple[Path, dict]:
    """Converte o PDF e salva em dest/. Retorna (caminho do artigo.md, metadados detectados)."""
    doc = fitz.open(pdf_path)
    total = len(doc)

    assets = dest / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    # Detecção automática de metadados
    titulo, titulo_en = detectar_titulo(doc)
    autores = detectar_autores(doc)

    # Frontmatter básico (será enriquecido pelo HAL depois)
    frontmatter = (
        "---\n"
        f"tipo: artigo\n"
        f"titulo: {titulo or pdf_path.stem}\n"
        f"fonte: {pdf_path.name}\n"
        f"paginas: {total}\n"
        f"conversao: {date.today().isoformat()}\n"
        f"---\n\n"
    )

    partes = [frontmatter]
    imagens_nomes: list[str] = []
    tabelas_detectadas: list[dict] = []

    for i in range(total):
        page = doc[i]
        num = i + 1
        partes.append(f"\n\n## Página {num}\n")

        # --- Texto ---
        texto = page.get_text("text").strip()
        if texto:
            partes.append(texto)
        else:
            partes.append("*[Página sem texto extraível — ver renderização em assets/]*")

        # --- Tabelas ---
        tabelas = page.find_tables()
        for t_idx, tab in enumerate(tabelas.tables, 1):
            md = tabela_para_markdown(tab)
            if md:
                partes.append(f"\n### Tabela {t_idx} (página {num})\n")
                partes.append(md)
                tabelas_detectadas.append({
                    "pagina": num,
                    "ordem": t_idx,
                    "linhas": tab.row_count,
                    "colunas": tab.col_count,
                })
                # Fallback visual: renderiza a página com a tabela
                if render_tabelas:
                    nome_png = f"pagina-{num:03d}.png"
                    pix = page.get_pixmap(dpi=dpi)
                    pix.save(assets / nome_png)
                    partes.append(f"\n*[Visual original:](assets/{nome_png})*\n")
                    imagens_nomes.append(nome_png)

        # --- Imagens bitmap ---
        for img in page.get_images(full=True):
            xref = img[0]
            nome = extrair_imagem(doc, xref, assets, f"p{num:03d}")
            if nome and nome not in imagens_nomes:
                imagens_nomes.append(nome)
                partes.append(f"\n![Imagem extraída](assets/{nome})\n")

    # Copia o PDF original
    shutil.copy2(pdf_path, dest / "fonte.pdf")

    artigo_path = dest / "artigo.md"
    artigo_path.write_text("\n".join(partes), encoding="utf-8")

    # Metadados para JSON de indexação
    metadados = {
        "arquivo_original": pdf_path.name,
        "slug": dest.name,
        "titulo": titulo,
        "titulo_en": titulo_en,
        "autores": autores,
        "publicacao": "",
        "ano": "",
        "doi": "",
        "tema": "",
        "paginas": total,
        "tabelas": tabelas_detectadas,
        "imagens": imagens_nomes,
        "paginas_renderizadas": [i["pagina"] for i in tabelas_detectadas],
        "status": "aguardando_confirmacao",
    }
    # Salva JSON de indexação para confirmação
    (dest / "indexacao.json").write_text(
        json.dumps(metadados, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    doc.close()
    return artigo_path, metadados


def main():
    parser = argparse.ArgumentParser(description="Converte PDF para Markdown + assets na wiki")
    parser.add_argument("pdf", help="Caminho do arquivo PDF")
    parser.add_argument("--dest", default=str(KB_RAW_BOLETINS / "articles"),
                        help="Pasta base de destino (default: wiki/raw/articles)")
    parser.add_argument("--slug", help="Nome da pasta de destino (default: derivado do nome do PDF)")
    parser.add_argument("--no-render", action="store_true",
                        help="Não renderizar páginas com tabelas como PNG")
    parser.add_argument("--dpi", type=int, default=150, help="Resolução das renderizações (default: 150)")
    args = parser.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        sys.exit(f"Erro: arquivo não encontrado: {pdf}")

    slug = args.slug or slugify(pdf.stem)
    dest = Path(args.dest) / slug
    if dest.exists():
        sys.exit(f"Erro: destino já existe: {dest} (use --slug para outro nome)")

    dest.mkdir(parents=True)
    print(f"📄 Convertendo: {pdf.name}")
    print(f"📁 Destino: {dest}")

    artigo, metadados = converter_pdf(pdf, dest, render_tabelas=not args.no_render, dpi=args.dpi)

    print(f"\n✅ Conversão concluída!")
    print(f"   📝 Artigo: {artigo}")
    print(f"   🖼️  Assets: {dest / 'assets'}")
    print(f"   📄 Fonte:  {dest / 'fonte.pdf'}")
    print(f"   📋 Indexação: {dest / 'indexacao.json'}")
    print(f"\n🔎 Metadados detectados:")
    print(f"   Título: {metadados['titulo'] or '⚠️ NÃO DETECTADO'}")
    print(f"   Autores: {', '.join(metadados['autores']) if metadados['autores'] else '⚠️ NÃO DETECTADOS'}")
    print(f"   Tabelas: {len(metadados['tabelas'])} | Imagens: {len(metadados['imagens'])}")
    print(f"\n👉 Revise {dest / 'indexacao.json'} (ou envie ao HAL) e confirme antes de indexar.")


if __name__ == "__main__":
    main()
