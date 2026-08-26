#!/usr/bin/env python3
"""
llm_enrich_boletim.py — Enriquece campos de boletim extraídos por regex usando LLM.

Uso:
    python scripts/llm_enrich_boletim.py /path/to/BS-XXX-YYYY.md [--model MODEL] [--dry-run]
    python scripts/llm_enrich_boletim.py --stdin < boletim.md [--model MODEL]

Variáveis de ambiente:
    LLM_ENRICH_MODEL — modelo OpenRouter (default: nvidia/nemotron-3-ultra)
    OPENROUTER_API_KEY — chave da API OpenRouter
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# Configuração do modelo via env var (parametrizado)
DEFAULT_MODEL = os.environ.get("LLM_ENRICH_MODEL", "deepseek/deepseek-v4-flash-0731")
# OPENROUTER_API_KEY será passado como parâmetro

try:
    import openai
except ImportError:
    print("Erro: openai não instalado. Instale com: pip install openai", file=sys.stderr)
    sys.exit(1)


def build_enrichment_prompt(regex_fields: dict, full_text: str) -> str:
    """Constrói prompt estruturado para enriquecimento LLM."""
    
    # Prepara dados para o prompt (limita texto para caber no contexto)
    max_text_chars = 25000
    text_for_prompt = full_text[:max_text_chars]
    if len(full_text) > max_text_chars:
        text_for_prompt += f"\n\n[... texto truncado, total {len(full_text)} chars ...]"

    # Serializa campos regex para JSON legível
    regex_json = json.dumps(regex_fields, ensure_ascii=False, indent=2)

    return f"""Você é um especialista em processamento de Boletins de Serviço do MPT (Ministério Público do Trabalho).
Recebeu dados já extraídos por regex de um boletim. Sua tarefa: CORRIGIR/ENRIQUECER campos onde o regex é impreciso.

=== DADOS REGEX (base) ===
{regex_json}

=== TEXTO COMPLETO DO BOLETIM ===
{text_for_prompt}

=== TAREFAS ===
Retorne APENAS JSON válido com as correções/enriquecimentos:

1. **UNIT_DISAMBIGUATION**: Para cada ato em "atos", defina "unidade_correta"
   Valores permitidos: "pgt" | "dgp" | "dadm" | "cg" | "ouv" | "setic" | "prt-N" | "mpt"
   Baseie-se no CONTEXTO da seção onde o ato aparece (ex: "ATOS DA PROCURADORIA-GERAL" → pgt,
   "ATOS DA DIRETORIA DE GESTÃO DE PESSOAS" → dgp, "PRT-7ª REGIÃO" → prt-7).

2. **EMENTA_CLEAN**: Para cada ato, reescreva "ementa_limpa" (máx 180 chars):
   - Remove preâmbulos jurídicos padrão ("O PROCURADOR-GERAL..., no uso..., considerando..., RESOLVE:")
   - Remove citações de leis, PGEAs, "considerando que...", "tendo em vista..."
   - Mantém: AÇÃO PRINCIPAL + BENEFICIÁRIO + DETALHES RELEVANTES
   - Exemplo: "ANULAR remoção por motivo de saúde e determinar remoção sub judice de servidor para PRT-6"

3. **TIPO_ATO**: Se regex deixou "ato" genérico, classifique corretamente:
   portaria | decisao | edital | portaria-conjunta | resolucao | instrucao-normativa |
   aviso | extrato | ata | comunicado | retificacao | recomendacao | notificacao | outro

4. **TEMAS_RELEVANTES**: 5-8 temas SEMÂNTICOS (não apenas frequência), ex:
   ["licença-prêmio", "remoção", "plantão", "substituição", "auxílio-pré-escolar", "diárias", "concurso"]

=== FORMATO DE SAÍDA (JSON EXATO) ===
{{
  "atos_patches": [
    {{"index": 0, "unidade_correta": "pgt", "ementa_limpa": "...", "tipo_ato": "portaria"}},
    {{"index": 1, "unidade_correta": "dgp", "ementa_limpa": "...", "tipo_ato": "decisao"}}
  ],
  "temas": ["tema1", "tema2", "tema3", "tema4", "tema5"],
  "confianca_global": 0.92
}}

REGRAS:
- Índices em "atos_patches" correspondem à ordem em "atos" do regex
- Se não houver correção para um campo, omita-o no patch (ex: só "unidade_correta")
- "confianca_global": 0.0 a 1.0 — sua confiança na qualidade geral do enriquecimento
- NÃO inclua comentários, markdown, ou texto extra — APENAS O JSON"""


def call_llm(prompt: str, model: str, temperature: float = 0.1, api_key: str = None) -> str:
    """Chama LLM via OpenRouter."""
    if not api_key:
        raise RuntimeError("api_key não fornecida")
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Você processa boletins do MPT. Retorne APENAS JSON válido."},
            {"role": "user", "content": prompt},
        ],
        temperature=temperature,
        max_tokens=3000,
        response_format={"type": "json_object"},
    )

    return response.choices[0].message.content


def parse_llm_response(response: str) -> dict:
    """Parseia e valida resposta JSON do LLM."""
    try:
        data = json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Resposta do LLM não é JSON válido: {e}")

    # Validação básica
    if "atos_patches" not in data:
        data["atos_patches"] = []
    if "temas" not in data:
        data["temas"] = []
    if "confianca_global" not in data:
        data["confianca_global"] = 0.5

    return data


def apply_patches(regex_fields: dict, patches: dict) -> dict:
    """Aplica patches do LLM sobre campos regex."""
    enriched = regex_fields.copy()
    atos = enriched.get("atos", [])

    # Aplica patches por índice
    for patch in patches.get("atos_patches", []):
        idx = patch.get("index")
        if idx is None or idx < 0 or idx >= len(atos):
            continue

        ato = atos[idx]
        if "unidade_correta" in patch:
            ato["unidade"] = patch["unidade_correta"]
        if "ementa_limpa" in patch:
            ato["ementa"] = patch["ementa_limpa"]
        if "tipo_ato" in patch:
            ato["tipo"] = patch["tipo_ato"]

    # Atualiza temas se fornecidos
    if patches.get("temas"):
        enriched["temas_llm"] = patches["temas"]

    enriched["llm_confianca"] = patches.get("confianca_global", 0.5)
    return enriched


def load_boletim_text(path: Path | None = None) -> tuple[str, dict]:
    """Carrega texto do boletim e extrai campos regex (reutiliza lógica existente)."""
    if path:
        text = path.read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()

    # Importa função de extração regex do script principal
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ingest_boletim_wiki import extract_boletim_fields

    regex_fields = extract_boletim_fields(text)
    regex_fields["_full_text"] = text  # guarda para prompt
    return text, regex_fields


def enrich_boletim(boletim_path: Path | None, model: str, dry_run: bool = False, api_key: str = None) -> dict:
    """Pipeline principal de enriquecimento."""
    # 1. Carrega e extrai regex
    text, regex_fields = load_boletim_text(boletim_path)
    full_text = regex_fields.pop("_full_text")

    # 2. Constrói prompt
    prompt = build_enrichment_prompt(regex_fields, full_text)

    if dry_run:
        print("=== PROMPT (dry-run) ===")
        print(prompt[:2000] + ("..." if len(prompt) > 2000 else ""))
        print("\n=== FIM DRY-RUN ===")
        return {"status": "dry-run", "model": model}

    # 3. Chama LLM
    print(f"Chamando LLM ({model})...", file=sys.stderr)
    response = call_llm(prompt, model=model, api_key=api_key)

    # 4. Parseia e aplica patches
    patches = parse_llm_response(response)
    enriched = apply_patches(regex_fields, patches)

    return {
        "status": "success",
        "model": model,
        "regex_fields": regex_fields,
        "enriched_fields": enriched,
        "patches_applied": patches,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Enriquece boletim com LLM")
    parser.add_argument("boletim", nargs="?", help="Caminho do BS-XXX-YYYY.md (ou stdin se omitido)")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Modelo OpenRouter (default: {DEFAULT_MODEL})")
    parser.add_argument("--dry-run", action="store_true", help="Só mostra prompt, não chama LLM")
    parser.add_argument("--output", "-o", help="Arquivo JSON de saída (default: stdout)")
    parser.add_argument("--api-key", help="Chave da API OpenRouter (obrigatório)")
    args = parser.parse_args()

    boletim_path = Path(args.boletim) if args.boletim else None

    try:
        result = enrich_boletim(boletim_path, model=args.model, dry_run=args.dry_run, api_key=args.api_key)
    except Exception as e:
        print(f"Erro: {e}", file=sys.stderr)
        return 1

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output)

    return 0


if __name__ == "__main__":
    sys.exit(main())