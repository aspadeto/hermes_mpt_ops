#!/usr/bin/env python3
"""
openrouter_survey.py — Levantamento recorrente dos subprovedores OpenRouter.

Coleta, via API OpenRouter (/api/v1/models/<slug>/endpoints), os subprovedores
(provedores por trás do OpenRouter) dos modelos principais e auxiliares do
ambiente, e regenera:

  data/_openrouter_survey/endpoints.json       (subprovedores dos modelos principais)
  data/_openrouter_survey/aux_endpoints.json  (subprovedores dos modelos auxiliares)
  data/_openrouter_survey/levantamento.md     (tabelas + recomendação only/order)

Uso:
  python3 openrouter_survey.py            # coleta e grava (modo normal)
  python3 openrouter_survey.py --dry-run  # só alerta subprovedores instáveis, não grava

Padrão cron (no_agent, silencioso): sem argumentos, o script grava os arquivos e
imprime apenas uma linha de confirmação; com --dry-run imprime ALERTA apenas se
houver subprovedor com uptime <95% (watchdog).

Embrião da melhoria futura: a seção "Recomendação p/ only/order" já calcula, por
necessidade auxiliar, o melhor subprovedor (picker) ranqueado por score
(30% custo + 30% throughput + 25% latência + 15% uptime).
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Caminhos
# ---------------------------------------------------------------------------
BASE_DIR = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops")
SURVEY_DIR = BASE_DIR / "data" / "_openrouter_survey"
MAIN_ENDPOINTS_JSON = SURVEY_DIR / "endpoints.json"
AUX_ENDPOINTS_JSON = SURVEY_DIR / "aux_endpoints.json"
LEVANTAMENTO_MD = SURVEY_DIR / "levantamento.md"

# ---------------------------------------------------------------------------
# Modelos a levantar
# ---------------------------------------------------------------------------
# Modelos principais (agente): default atual + alternativas candidatas.
MAIN_MODELS = {
    "deepseek/deepseek-v4-flash-0731": "DEFAULT atual (agente)",
    "deepseek/deepseek-v4-pro-0813": "alternativa agente (qualidade/raciocínio)",
    "qwen/qwen3.8-flash": "alternativa agente (barata)",
}

# Modelos auxiliares (title/compression/vision): candidatos possíveis.
AUX_MODELS = [
    "google/gemini-2.5-flash-lite",
    "google/gemini-2.5-flash",
    "google/gemini-3.6-flash",
    "openai/gpt-4o-mini",
    "openai/gpt-5-mini",
    "deepseek/deepseek-v4-flash-0731",
    "qwen/qwen3.8-flash",
]

# Necessidades auxiliares do Hermes e seus candidatos (para a seção de recomendação).
AUX_NEEDS = {
    "Título (title)": {
        "requer_visao": False,
        "candidatos": ["google/gemini-2.5-flash-lite", "google/gemini-2.5-flash", "qwen/qwen3.8-flash"],
    },
    "Compressão (compression)": {
        "requer_visao": False,
        "candidatos": ["deepseek/deepseek-v4-flash-0731", "google/gemini-2.5-flash-lite", "google/gemini-2.5-flash"],
    },
    "Visão (vision)": {
        "requer_visao": True,
        "candidatos": ["google/gemini-2.5-flash-lite", "google/gemini-2.5-flash", "openai/gpt-4o-mini"],
    },
}

# ---------------------------------------------------------------------------
# Pesos do score (eless para recomendar only/order)
# ---------------------------------------------------------------------------
_W_CUSTO = 0.30
_W_TROUGHPUT = 0.30
_W_LATENCIA = 0.25
_W_UPTIME = 0.15


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _api_key() -> str:
    """Lê a chave OpenRouter do .env do Hermes. Nunca a imprime."""
    env_path = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))) / ".env"
    if not env_path.exists():
        env_path = Path.home() / ".hermes" / ".env"
    for line in env_path.read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("OPENROUTER_API_KEY não encontrada no .env do Hermes")


def _http_get(url: str, key: str) -> dict:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _fmt(v) -> str:
    if v is None:
        return "—"
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def _score(row: dict) -> float:
    """Score combinado (0-100, maior = melhor) p/ ranquear subprovedores."""
    p = (row.get("price_prom_Mtok") or 0) + (row.get("price_comp_Mtok") or 0)
    thr = row.get("thr_p50_tps") or 0
    lat = row.get("lat_p50_ms") or 9999
    up = row.get("up1d") or 0
    cost_score = 100 - (math.log(p + 1) / math.log(10)) * 20 if p > 0 else 100
    thr_score = min(100, thr / 1.5)
    lat_score = max(0, 100 - lat / 20)
    return (_W_CUSTO * cost_score + _W_TROUGHPUT * thr_score
            + _W_LATENCIA * lat_score + _W_UPTIME * up)


# ---------------------------------------------------------------------------
# Coleta
# ---------------------------------------------------------------------------
def _collect(models, key: str, is_main: bool) -> list[dict]:
    rows = []
    for mid in models:
        label = models[mid] if isinstance(models, dict) else mid
        try:
            d = _http_get(f"https://openrouter.ai/api/v1/models/{mid}/endpoints", key)
            eps = d["data"].get("endpoints", [])
        except Exception as ex:  # noqa: BLE001
            print(f"[aviso] Erro ao levantar {mid}: {ex}", file=sys.stderr)
            continue
        arch = d["data"].get("architecture", {})
        has_vision = "image" in arch.get("input_modalities", [])
        for e in eps:
            pr = e.get("pricing", {})
            lat = e.get("latency_last_30m") or {}
            thr = e.get("throughput_last_30m") or {}
            def _f(v):
                try:
                    return round(float(v) * 1e6, 4)
                except (TypeError, ValueError):
                    return None
            rows.append({
                "model": mid,
                "label": label,
                "is_main": is_main,
                "has_vision": has_vision,
                "provider": e.get("provider_name"),
                "quant": e.get("quantization"),
                "ctx": e.get("context_length"),
                "prompt_usd_per_M": _f(pr.get("prompt")),
                "comp_usd_per_M": _f(pr.get("completion")),
                "thr_p50_tps": thr.get("p50"),
                "thr_p90_tps": thr.get("p90"),
                "lat_p50_ms": lat.get("p50"),
                "lat_p90_ms": lat.get("p90"),
                "up1d_pct": round(e.get("uptime_last_1d", 0), 2) if isinstance(e.get("uptime_last_1d"), (int, float)) else None,
                "status": e.get("status"),
            })
        # tweak done
    return rows


# Markdown
def _markdown_table(rows: list[dict]) -> str:
    lines = [
        "| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |",
        "|----------|-------|-----|-----------|----------|-----------|----------|---------|",
    ]
    for r in sorted(rows, key=lambda r: ((r.get("prompt_usd_per_Mtok") or 9e9), r["provider"].lower())):
        lines.append(
            f"| {r['provider']} | {r['quant']} | {r['ctx']} | "
            f"{_fmt(r.get('prompt_usd_per_Mtok'))} | {_fmt(r.get('comp_usd_per_Mtok'))} | "
            f"{r.get('thr_p50_tps') if r.get('thr_p50_tps') is not None else '—'} t/s | "
            f"{r.get('lat_p50_ms') if r.get('lat_p50_ms') is not None else '—'} ms | "
            f"{r.get('up1d_pct')} |"
        )
    return "\n".join(lines)


def _recomend_need(need: str, cfg: dict, aux_rows: list[dict]) -> str:
    cands = [r for r in aux_rows if r["model"] in cfg["candidatos"]]
    if cfg["requer_visao"]:
        cands = [r for r in cands if r.get("has_vision")]
    best = None
    for r in sorted(cands, key=lambda r: -_score(r)):
        best = r
        break
    if not best:
        return f"| {need} | — | sem endpoint disponível |"
    return f"| {need} | `{best['model']}` | {best['provider']} (score {_score(best):.0f}, $p {_fmt(best.get('prompt_usd_per_Mtok'))}, {best.get('thr_p50_tps') or 0} t/s, {best.get('lat_p50_ms') or 0}ms) |"


def generate_markdown(main_rows: list[dict], aux_rows: list[dict]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    L = []
    L.append("# Levantamento OpenRouter — subprovedores e recomendação")
    L.append("")
    L.append(f"Gerado: {now} (automático 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).")
    L.append("")
    # modelos principais por modelo
    for mid in MAIN_MODELS:
        sub = [r for r in main_rows if r["model"] == mid]
        L.append(f"## Modelo: `{mid}` ({MAIN_MODELS[mid]})")
        L.append("")
        L.append(_markdown_table(sub))
        L.append("")
    # auxiliares
    L.append("## Modelos auxiliares")
    for mid in AUX_MODELS:
        sub = [r for r in aux_rows if r["model"] == mid]
        if not sub:
            continue
        L.append(f"### `{mid}`")
        L.append("")
        L.append(_markdown_table(sub))
        L.append("")
    # recomendação
    L.append("## Recomendação por necessidade (embrião da melhoria futura)")
    L.append("")
    L.append("> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).")
    L.append("")
    L.append("| Necessidade | Modelo recomendado | Melhor subprovedor |")
    L.append("|-------------|--------------------|--------------------|")
    for need, cfg in AUX_NEEDS.items():
        L.append(_recomend_need(need, cfg, aux_rows))
    L.append("")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description="Levantamento OpenRouter de subprovedores")
    ap.add_argument("--dry-run", action="store_true",
                    help="Não gravar; emular watchdog (stdout = ALERTA se subprovedor instável).")
    ap.add_argument("--stdout", action="store_true",
                    help="Imprimir o markdown gerado no stdout em vez de gravar.")
    args = ap.parse_args()

    try:
        key = _api_key()
    except RuntimeError as ex:
        print(f"ERRO: {ex}", file=sys.stderr)
        return 1

    main_rows = _collect(MAIN_MODELS, key, is_main=True)
    aux_rows = _collect({m: m for m in AUX_MODELS}, key, is_main=False)

    if args.dry_run:
        instaveis = [
            f"- {r['provider']} ({r['model']}) up1d={r['up1d_pct']}%"
            for r in main_rows + aux_rows
            if (r.get("up1d_pct") or 100) < 95
        ]
        if instaveis:
            print("ALERTA — subprovedores com uptime 1d <95%:\n" + "\n".join(instaveis))
        else:
            print("")
        return 0

    md = generate_markdown(main_rows, aux_rows)
    if args.stdout:
        print(md)
        return 0

    SURVEY_DIR.mkdir(parents=True, exist_ok=True)
    MAIN_ENDPOINTS_JSON.write_text(json.dumps(main_rows, indent=2, ensure_ascii=False))
    AUX_ENDPOINTS_JSON.write_text(json.dumps(aux_rows, indent=2, ensure_ascii=False))
    LEVANTAMENTO_MD.write_text(md)
    print(f"Levantamento OpenRouter atualizado: {LEVANTAMENTO_MD} ({len(main_rows) + len(aux_rows)} endpoints)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())