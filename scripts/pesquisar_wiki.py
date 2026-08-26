#!/usr/bin/env python3
"""
pesquisar_wiki.py — Pesquisa no wiki do KB com seleção local + LLM remoto.

Fluxo:
  1. Busca candidatos no index.md e entities/ por termos da pergunta
  2. Seleciona até N candidatos mais relevantes
  3. Monta prompt com o contexto dos candidatos
  4. Envia para LLM remoto (configurável) para resposta final

Uso:
  python scripts/pesquisar_wiki.py "Qual portaria altera a estrutura organizacional da PRT10?"
  python scripts/pesquisar_wiki.py "Sobre o que versa a portaria 26 da PRT18?" --candidates 5
  python scripts/pesquisar_wiki.py "Qual ato designa ARIANNE CASTRO?" --model gpt-4o
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_KB = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb")
DEFAULT_ENTITIES = DEFAULT_KB / "entities"
DEFAULT_INDEX = DEFAULT_KB / "index.md"
DEFAULT_DOCLING = DEFAULT_KB / "boletins_docling"

DEFAULT_MODEL = os.getenv("WIKI_LLM_MODEL", "gpt-4o-mini")
DEFAULT_MAX_CANDIDATES = 5


def load_index(index_path: Path) -> list[dict]:
    """Carrega entradas do index.md como lista de {slug, title}."""
    if not index_path.exists():
        return []
    text = index_path.read_text(encoding="utf-8")
    entries = []
    for line in text.splitlines():
        m = re.search(r"\[\[([^\]]+)\]\]\s*—\s*(.+)", line)
        if m:
            entries.append({"slug": m.group(1), "title": m.group(2).strip()})
    return entries


def score_candidate(entry: dict, terms: list[str], content: str = "") -> int:
    """Pontua candidato por presença de termos no título/slug e conteúdo."""
    slug = entry.get("slug") or ""
    title = entry.get("title") or ""
    text = f"{title} {slug} {content}".lower()
    score = 0
    for term in terms:
        if term.lower() in text:
            score += 1
    return score


def search_candidates(question: str, max_candidates: int = DEFAULT_MAX_CANDIDATES) -> list[dict]:
    """Busca candidatos no wiki por termos da pergunta."""
    stopwords = {"qual", "quais", "quem", "onde", "quando", "como", "por", "que", "de", "do", "da", "no", "na", "em", "para", "por", "com", "sobre", "o", "a", "os", "as", "um", "uma", "foi", "for", "são", "tem", "entre", "e", "ou"}
    terms = [w for w in re.findall(r"\w+", question.lower()) if len(w) > 2 and w not in stopwords]

    entries: list[dict] = []

    # 1) entradas do index.md que existem em entities/
    for entry in load_index(DEFAULT_INDEX):
        slug = entry.get("slug") or ""
        if (DEFAULT_ENTITIES / f"{slug}.md").exists():
            entries.append(entry)

    # 2) páginas de boletins em entities/
    for path in DEFAULT_ENTITIES.glob("bs-*-202*.md"):
        slug = path.stem
        if not any(e.get("slug") == slug for e in entries):
            title = slug.replace("bs-", "BS-").upper()
            entries.append({"slug": slug, "title": title})

    # 3) fallback: boletins_docling/
    if not entries:
        for path in DEFAULT_DOCLING.glob("BS-*.md"):
            slug = path.stem.lower().replace("bs-", "bs-")
            title = path.stem.replace("BS-", "BS-").upper()
            entries.append({"slug": slug, "title": title})

    scored = []
    for entry in entries:
        content = load_entity_content(entry.get("slug") or "")
        scored.append((entry, score_candidate(entry, terms, content)))
    scored.sort(key=lambda x: x[1], reverse=True)

    candidates = [entry for entry, score in scored if score > 0][:max_candidates]
    return candidates


def load_entity_content(slug: str) -> str:
    """Carrega conteúdo de uma entidade do wiki."""
    path = DEFAULT_ENTITIES / f"{slug}.md"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_prompt(question: str, candidates: list[dict]) -> str:
    """Monta prompt para o LLM com contexto dos candidatos."""
    if not candidates:
        return f"""Pergunta: {question}

Contexto: Nenhum documento relevante encontrado no wiki. Responda que não encontrou a informação nos boletins disponíveis."""

    context_parts = []
    for i, candidate in enumerate(candidates, 1):
        content = load_entity_content(candidate["slug"])
        # Pega só o início do conteúdo (título + primeiros atos)
        if content:
            lines = content.splitlines()[:30]
            content_preview = "\n".join(lines)
        else:
            content_preview = "(arquivo não encontrado)"
        context_parts.append(f"[{i}] {candidate['title']}\n{content_preview}\n")

    context = "\n".join(context_parts)

    prompt = f"""Você é um assistente que responde perguntas sobre boletins de serviço do MPT (Ministério Público do Trabalho).
Use APENAS o contexto fornecido abaixo para responder. Se a resposta não estiver no contexto, diga que não encontrou a informação.

Contexto:
{context}

Pergunta: {question}

Resposta:"""
    return prompt


def call_llm(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """Chama LLM remoto via OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        return "Erro: biblioteca openai não instalada. Instale com: pip install openai"

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "Erro: OPENAI_API_KEY não configurada."

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro na chamada ao LLM: {e}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Pesquisa no wiki do KB")
    parser.add_argument("pergunta", help="Pergunta a ser pesquisada")
    parser.add_argument("--candidates", type=int, default=DEFAULT_MAX_CANDIDATES, help="Número máximo de candidatos")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Modelo LLM a ser usado")
    parser.add_argument("--kb", default=str(DEFAULT_KB), help="Caminho do KB")
    parser.add_argument("--no-llm", action="store_true", help="Apenas mostra candidatos, não chama LLM")
    args = parser.parse_args()

    kb = Path(args.kb)
    global DEFAULT_ENTITIES, DEFAULT_INDEX
    DEFAULT_ENTITIES = kb / "entities"
    DEFAULT_INDEX = kb / "index.md"

    print(f"🔍 Pergunta: {args.pergunta}\n")
    print(f"📋 Buscando candidatos no wiki...\n")

    candidates = search_candidates(args.pergunta, args.candidates)
    if not candidates:
        print("❌ Nenhum candidato encontrado no wiki.")
        return 1

    print(f"✅ {len(candidates)} candidato(s) encontrado(s):\n")
    for i, c in enumerate(candidates, 1):
        print(f"  {i}. {c['title']} ({c['slug']})")

    print("\n" + "=" * 70)

    if args.no_llm:
        print("\n[Modo sem LLM] Candidatos selecionados. Mostrando conteúdo...\n")
        for i, c in enumerate(candidates, 1):
            content = load_entity_content(c["slug"])
            print(f"\n{'=' * 70}")
            print(f"[{i}] {c['title']}")
            print(f"{'=' * 70}")
            if content:
                print(content)
            else:
                print("(arquivo não encontrado)")
        return 0

    prompt = build_prompt(args.pergunta, candidates)
    print("\n📤 Enviando para LLM remoto...\n")
    resposta = call_llm(prompt, args.model)

    print(f"{'=' * 70}")
    print("🤖 Resposta do LLM:")
    print(f"{'=' * 70}")
    print(resposta)
    print(f"{'=' * 70}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
