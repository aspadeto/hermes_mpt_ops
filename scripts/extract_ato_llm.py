#!/usr/bin/env python3
"""
extract_ato_llm.py — Extrai lista de atos de um boletim docling via LLM.

Usa a mesma configuração do Hermes:
  - base_url/model/provider em ~/.hermes/config.yaml
  - OPENROUTER_API_KEY em ~/.hermes/.env
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Erro: PyYAML não instalado. Instale com: pip install pyyaml")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("Erro: openai não instalado. Instale com: pip install openai")
    sys.exit(1)

DEFAULT_KB = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb")
DEFAULT_DOCLING = DEFAULT_KB / "boletins_docling"
HERMES_DIR = Path("/home/hermes/.hermes")


def load_hermes_llm_config() -> dict:
    config_path = HERMES_DIR / "config.yaml"
    env_path = HERMES_DIR / ".env"

    cfg = {}
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

    model_cfg = cfg.get("model", {})
    # Padrão de extração: deepseek-v4-flash-0731 via OpenRouter.
    # Permite override por --model / --base-url na CLI; o carregamento da key
    # continua vindo de ~/.hermes/.env (OPENROUTER_API_KEY).
    base_url = os.getenv("WIKI_LLM_BASE_URL", "https://openrouter.ai/api/v1")
    model = os.getenv("WIKI_LLM_MODEL", "deepseek/deepseek-v4-flash-0731")
    provider = model_cfg.get("provider", "openrouter")

    api_key = ""
    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("OPENROUTER_API_KEY="):
                    api_key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break

    return {
        "base_url": base_url.rstrip("/"),
        "model": model,
        "provider": provider,
        "api_key": api_key,
    }


def call_llm(prompt: str, model: str, base_url: str, api_key: str) -> str:
    client = OpenAI(api_key=api_key, base_url=base_url)
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            # Modelos de raciocínio (ex.: deepseek-v4-flash) gastam parte da
            # janela de saída com reasoning tokens; 8000 evita corte prematuro.
            max_tokens=8000,
            temperature=0.3,
        )
        content = response.choices[0].message.content
        if not content:
            finish = response.choices[0].finish_reason
            return f"Erro na chamada ao LLM: resposta vazia (finish_reason={finish})"
        return content.strip()
    except Exception as e:
        return f"Erro na chamada ao LLM: {e}"


def chunk_text(md_text: str, max_chars: int = 12000) -> list[str]:
    """Divide o boletim em chunks de até max_chars.

    Tenta quebrar em limites de cabeçalho markdown (##/###) para não cortar
    um ato no meio; se não houver quebra adequada dentro do limite, corta
    na última linha em branco; como último recurso, corta duro.
    """
    if len(md_text) <= max_chars:
        return [md_text]

    chunks = []
    start = 0
    n = len(md_text)
    while start < n:
        end = min(start + max_chars, n)
        if end >= n:
            chunks.append(md_text[start:])
            break
        # Procura último limite de seção (cabeçalho ##) antes do corte.
        window = md_text[start:end]
        cut = -1
        for m in re.finditer(r"^#{1,4} .*$", window, re.MULTILINE):
            cut = m.start()
        if cut > max_chars // 3:  # só aceita quebra depois dos primeiros 1/3
            end = start + cut
        else:
            nl = window.rfind("\n\n")
            if nl > max_chars // 3:
                end = start + nl + 1
        chunks.append(md_text[start:end])
        start = end
    return chunks


def extract_atos_from_llm(md_text: str, model: str, base_url: str, api_key: str) -> list[dict]:
    """Extrai atos via LLM em chunks, com dedup por (numero, tipo, unidade)."""
    atos: list[dict] = []
    seen: set[tuple] = set()

    chunks = chunk_text(md_text)
    total = len(chunks)
    for i, chunk in enumerate(chunks, 1):
        print(f"  Chunk {i}/{total} ({len(chunk)} chars)...", file=sys.stderr)
        prompt = f"""Extraia TODOS os atos do fragmento de boletim abaixo. Para CADA ato, retorne UM JSON com EXATAMENTE estas 4 chaves:
- "numero": string (número do ato, só dígitos)
- "tipo": string, um de: portaria, resolucao, ato, instrucao-normativa, decreto
- "ementa": string (resumo do ato, máximo 200 caracteres)
- "unidade": string, um de: prt2, prt3, ..., prt24, pgt, mpt (regional/órgão emissor, SEM colchetes, ex: prt13 ou pgt)

Se o fragmento NÃO contiver nenhum ato completo, responda [].

Responda APENAS com um JSON array. Nada mais: sem markdown, sem texto explicativo, sem comentários.
Formato de exemplo:
[{{"numero": "55", "tipo": "portaria", "ementa": "Altera a estrutura organizacional", "unidade": "pgt"}}]

Fragmento {i}/{total} do boletim:
{chunk}
"""

        resposta = call_llm(prompt, model, base_url, api_key)

        json_match = re.search(r"\[.*\]", resposta, re.DOTALL)
        if not json_match:
            print(f"  Aviso: sem JSON válido na resposta do chunk {i}", file=sys.stderr)
            continue

        try:
            parsed = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            print(f"  Aviso: JSON inválido no chunk {i}", file=sys.stderr)
            continue

        if not isinstance(parsed, list):
            continue

        for ato in parsed:
            key = (
                str(ato.get("numero", "")).strip(),
                str(ato.get("tipo", "")).strip().lower(),
                str(ato.get("unidade", "")).strip().lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            atos.append(ato)

    return atos


def main() -> int:
    parser = argparse.ArgumentParser(description="Extrai atos de boletim via LLM")
    parser.add_argument("boletim", help="Caminho do BS-XXX-YYYY.md")
    parser.add_argument("--model", default=None, help="Modelo LLM")
    parser.add_argument("--kb", default=str(DEFAULT_KB), help="Caminho do KB")
    args = parser.parse_args()

    cfg = load_hermes_llm_config()
    model = args.model or cfg["model"]
    base_url = cfg["base_url"]
    api_key = cfg["api_key"]

    if not api_key:
        print("Erro: OPENROUTER_API_KEY não encontrada em ~/.hermes/.env")
        return 1

    path = Path(args.boletim)
    if not path.exists():
        path = DEFAULT_DOCLING / Path(args.boletim).name

    if not path.exists():
        print(f"Arquivo não encontrado: {args.boletim}")
        return 1

    text = path.read_text(encoding="utf-8")
    atos = extract_atos_from_llm(text, model, base_url, api_key)

    print(f"=== {path.name} ===")
    print(f"Provider: {cfg['provider']}")
    print(f"Modelo: {model}")
    print(f"Base URL: {base_url}")
    print(f"Total de atos extraídos: {len(atos)}")
    print()

    for i, ato in enumerate(atos, 1):
        print(f"{i}. [{ato.get('tipo', 'ato').upper()}] {ato.get('numero', '')} - {ato.get('unidade', '').upper()}")
        print(f"   {ato.get('ementa', '')[:120]}")
        print()

    output_path = DEFAULT_KB / "entities" / f"{path.stem}_llm_atos.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(atos, f, ensure_ascii=False, indent=2)
    print(f"JSON salvo em: {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
