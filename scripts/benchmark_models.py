#!/usr/bin/env python3
"""
benchmark_models.py — Benchmark de modelos OpenRouter para processamento de boletins.

Testa múltiplos modelos com o mesmo boletim e coleta:
- Tempo de resposta
- Tokens (input/output)
- Custo estimado
- Qualidade (completude dos campos)

Modelos a testar (guardrails ativos):
- deepseek/deepseek-v4-flash-0731
- poolside/laguna-s-2.1:free
- z-ai/glm-5.2:free
- nvidia/nemotron-3-ultra-550b-a55b:free
- google/gemini-2.5-flash
- deepseek/deepseek-v4-flash-0423

Uso:
    python scripts/benchmark_models.py --api-key "sk-or-..." [--boletim BS-XXX-YYYY.md]
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import openai
except ImportError:
    print("Erro: openai não instalado. Instale com: pip install openai", file=sys.stderr)
    sys.exit(1)

from ingest_boletim_wiki import extract_boletim_fields


# Modelos a testar (IDs OpenRouter)
MODELOS = [
    "deepseek/deepseek-v4-flash-0731",
    "poolside/laguna-s-2.1:free",
    "z-ai/glm-5.2:free",
    "nvidia/nemotron-3-ultra-550b-a55b:free",
    "google/gemini-2.5-flash",
    "deepseek/deepseek-v4-flash-0423",
]

# Preços por 1M tokens (USD) - valores aproximados OpenRouter
# Fonte: https://openrouter.ai/models
PRECOS = {
    "deepseek/deepseek-v4-flash-0731": {"input": 0.10, "output": 0.40},
    "poolside/laguna-s-2.1:free": {"input": 0.00, "output": 0.00},
    "z-ai/glm-5.2:free": {"input": 0.00, "output": 0.00},
    "nvidia/nemotron-3-ultra-550b-a55b:free": {"input": 0.00, "output": 0.00},
    "google/gemini-2.5-flash": {"input": 0.075, "output": 0.30},
    "deepseek/deepseek-v4-flash-0423": {"input": 0.10, "output": 0.40},
}


def sanitize_for_json(s: str) -> str:
    return s.replace('\x00', '').replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')


def build_prompt(regex_fields: dict, full_text: str) -> str:
    clean_text = full_text[:8000].replace('\x00', '').replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
    regex_json = json.dumps(regex_fields, ensure_ascii=False, indent=2)[:3000].replace('\x00', '').replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')

    template = """Voce e um especialista em processamento de Boletins de Servico do MPT.
Retorne APENAS JSON valido. NAO inclua markdown, explicacoes, ou texto extra.

REGRAS OBRIGATORIAS DO JSON:
1. Array 'atos_patches': cada objeto DEVE ter virgula separando do proximo (exceto o ultimo)
2. Strings: SEMPRE use aspas duplas, escape aspas internas com \\\", feche todas as strings
3. Objetos: chaves e valores SEMPRE com aspas duplas, virgula entre pares chave-valor
4. Nao inclua comentarios, markdown, ou texto antes/depois do JSON

DADOS REGEX:
{regex_json}

TEXTO (primeiros 8000 chars):
{text}

TAREFA: Retorne JSON com:
{{
  "atos_patches": [
    {{"index": 0, "unidade_correta": "pgt", "ementa_limpa": "...", "tipo_ato": "portaria"}},
    {{"index": 1, "unidade_correta": "dgp", "ementa_limpa": "...", "tipo_ato": "decisao"}}
  ],
  "temas": ["tema1", "tema2", "tema3"],
  "confianca_global": 0.9
}}"""

    return template.format(regex_json=regex_json, text=clean_text)


def call_model(client: openai.OpenAI, model: str, prompt: str, temperature: float = 0.1) -> tuple[str, dict]:
    """Chama modelo e retorna (content, usage_info)."""
    start = time.time()
    
    response = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        temperature=temperature,
        max_tokens=3000,
        response_format={'type': 'json_object'},
    )
    
    elapsed = time.time() - start
    content = response.choices[0].message.content
    
    usage = {}
    if hasattr(response, 'usage') and response.usage:
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }
    
    return content, {"elapsed_seconds": elapsed, "usage": usage}


def evaluate_quality(parsed: dict, regex_fields: dict) -> dict:
    """Avalia qualidade do enriquecimento."""
    atos_patches = parsed.get("atos_patches", [])
    temas = parsed.get("temas", [])
    
    total_atos = len(regex_fields.get("atos", []))
    patched = len(atos_patches)
    
    # Conta campos preenchidos nos patches
    unidades = sum(1 for p in atos_patches if p.get("unidade_correta"))
    ementas = sum(1 for p in atos_patches if p.get("ementa_limpa"))
    tipos = sum(1 for p in atos_patches if p.get("tipo_ato"))
    
    return {
        "total_atos_regex": total_atos,
        "atos_patched": patched,
        "cobertura_patches": patched / total_atos if total_atos > 0 else 0,
        "unidades_preenchidas": unidades,
        "ementas_preenchidas": ementas,
        "tipos_preenchidos": tipos,
        "temas_extraidos": len(temas),
        "confianca": parsed.get("confianca_global", 0),
    }


def run_benchmark(api_key: str, boletim_path: Path, modelos: list[str] = None) -> list[dict]:
    if modelos is None:
        modelos = MODELOS
    
    # Carrega boletim
    text = boletim_path.read_text(encoding="utf-8")
    regex_fields = extract_boletim_fields(text)
    
    prompt = build_prompt(regex_fields, text)
    
    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
    )
    
    resultados = []
    
    for model in modelos:
        print(f"\n{'='*60}")
        print(f"Testando: {model}")
        print(f"{'='*60}")
        
        resultado = {
            "model": model,
            "success": False,
            "error": None,
            "tempo_segundos": 0,
            "tokens_input": 0,
            "tokens_output": 0,
            "custo_estimado_usd": 0.0,
            "quality": {},
            "raw_response": None,
        }
        
        try:
            content, meta = call_model(
                openai.OpenAI(
                    api_key=api_key,
                    base_url="https://openrouter.ai/api/v1",
                ),
                model,
                build_prompt(
                    regex_fields,
                    open(boletim_path, encoding="utf-8").read()
                )
            )
            
            resultado["tempo_segundos"] = meta["elapsed_seconds"]
            resultado["tokens_input"] = meta["usage"].get("prompt_tokens", 0)
            resultado["tokens_output"] = meta["usage"].get("completion_tokens", 0)
            
            # Calcula custo
            precos = PRECOS.get(model, {"input": 0, "output": 0})
            custo = (meta["usage"].get("prompt_tokens", 0) / 1_000_000 * precos["input"] +
                     meta["usage"].get("completion_tokens", 0) / 1_000_000 * precos["output"])
            resultado["custo_estimado_usd"] = round(custo, 6)
            
            # Parse e qualidade
            parsed = json.loads(content)
            resultado["raw_response"] = content[:500] + "..." if len(content) > 500 else content
            resultado["quality"] = evaluate_quality(parsed, regex_fields)
            resultado["success"] = True
            
            print(f"✓ Sucesso em {meta['elapsed_seconds']:.2f}s")
            print(f"  Tokens: {meta['usage'].get('prompt_tokens', 0)} in / {meta['usage'].get('completion_tokens', 0)} out")
            print(f"  Custo estimado: ${resultado['custo_estimado_usd']:.6f}")
            print(f"  Qualidade: {resultado['quality']['cobertura_patches']:.0%} atos, {resultado['quality']['temas_extraidos']} temas")
            
        except Exception as e:
            resultado["error"] = str(e)
            print(f"✗ Erro: {e}")
        
        resultados.append(resultado)
    
    return resultados


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark de modelos OpenRouter para boletins")
    parser.add_argument("--api-key", required=True, help="Chave da API OpenRouter")
    parser.add_argument("--boletim", help="Caminho do BS-XXX-YYYY.md (default: aleatório)")
    parser.add_argument("--output", "-o", help="Arquivo JSON de saída")
    parser.add_argument("--modelos", nargs="+", help="Modelos específicos para testar")
    args = parser.parse_args()
    
    api_key = args.api_key
    if not api_key:
        print("Erro: --api-key é obrigatório", file=sys.stderr)
        return 1
    
    # Seleciona boletim
    if args.boletim:
        boletim_path = Path(args.boletim)
    else:
        # Aleatório
        import random
        boletins = list(Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/boletins_docling").glob("BS-*-2026.md"))
        boletim_path = random.choice(boletins)
    
    print(f"Boletim: {boletim_path.name}")
    
    modelos = args.modelos if args.modelos else MODELOS
    print(f"Modelos a testar: {len(modelos)}")
    
    resultados = run_benchmark(api_key, boletim_path, modelos)
    
    # Resumo
    print(f"\n{'='*80}")
    print("RESUMO DO BENCHMARK")
    print(f"{'='*80}")
    print(f"{'Modelo':<45} {'Tempo(s)':>8} {'In/Out':>12} {'Custo($)':>10} {'Cobertura':>10} {'Temas':>6} {'Status'}")
    print(f"{'-'*80}")
    
    for r in resultados:
        if r["success"]:
            cov = f"{r['quality'].get('cobertura_patches', 0):.0%}"
            temas = r['quality'].get('temas_extraidos', 0)
            status = "OK"
        else:
            cov = "N/A"
            temas = "N/A"
            status = "ERRO"
        
        print(f"{r['model']:<45} {r['tempo_segundos']:>8.2f} "
              f"{r['tokens_input']}/{r['tokens_output']:>12} "
              f"${r['custo_estimado_usd']:>9.6f} {cov:>10} {temas:>6} {status}")
    
    # Salva resultados
    if args.output:
        Path(args.output).write_text(
            json.dumps({
                "boletim": str(boletim_path),
                "timestamp": time.time(),
                "resultados": resultados
            }, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"\nResultados salvos em: {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())