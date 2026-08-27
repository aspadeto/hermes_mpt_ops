# Otimização de roteamento OpenRouter — Recomendação (para revisão)

Data: 2026-08-27 · Provider: OpenRouter · Fonte: `/api/v1/models/<slug>/endpoints` (métricas 30min)

**Nada foi aplicado ao config — apenas documento de recomendação.**

## 1) Subprovedores — modelo default `deepseek/deepseek-v4-flash-0731` (lista completa)

Total: 29 provedores servindo o modelo.

| Provedor | Quant | Ctx | \$prompt/M | \$comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp4 | 1048576 | 0.0300 | 0.1000 | 9 | 2141 | 99.98 |
| Relace | fp4 | 1048576 | 0.0500 | 0.1000 | 66 | 933 | 99.81 |
| Baidu | fp8 | 1048576 | 0.0599 | 0.1198 | 124 | 741 | 99.92 |
| Ambient | fp4 | 1048576 | 0.0800 | 0.1800 | 52 | 521 | 99.05 |
| DeepInfra | fp8 | 1048576 | 0.0800 | 0.1800 | 41 | 552.5 | 98.56 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 101 | 514 | 92.6 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 31 | 553 | 99.58 |
| GMICloud | fp8 | 1048575 | 0.1120 | 0.2240 | 47 | 2353 | 97.72 |
| Morph | bf16 | 1048576 | 0.0987 | 0.2780 | 9 | 2309 | 93.96 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 43 | 650 | 96.86 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 117 | 403 | 99.97 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 66 | 592.5 | 99.72 |
| AkashML | fp8 | 1048576 | 0.1400 | 0.2800 | 47 | 848 | 99.75 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 38 | 748 | 97.99 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 46 | 670 | 99.6 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 42 | 849 | 97.02 |
| Mancer 2 | fp8 | 1048576 | 0.1500 | 0.4500 | 38 | 660 | 98.03 |
| Alibaba | unknown | 1000000 | 0.1760 | 0.5280 | 67 | 1276 | 99.98 |
| Wafer | unknown | 1048576 | 0.2800 | 0.5600 | 135 | 1165 | 99.19 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 81 | 1102 | 99.99 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 48 | 707 | 99.61 |
| Phala | unknown | 1048576 | 0.2200 | 0.6600 | 52 | 1695 | 97.7 |
| Reka | fp4 | 262144 | 0.2200 | 0.6600 | 152 | 506 | 98.23 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 50 | 1787 | 99.18 |
| StreamLake | fp8 | 1024000 | 0.2200 | 0.6600 | 38 | 850 | 99.9 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 49.5 | 1851 | 98.49 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 86 | 842 | 99.97 |
| NextBit | fp8 | 1048576 | 0.4400 | 1.3200 | 33 | 2261.5 | 99.38 |
| Novita | fp8 | 1048576 | 0.4400 | 1.3200 | 74 | 1425 | 99.89 |

## 2) Modelos auxiliares — 3 candidatos por necessidade

Necessidades auxiliares do Hermes: **title** (título de sessão), **compression** (compressão de contexto), **vision** (análise de imagem).

| Necessidade | Candidatos (modelo @ melhor provider) | Faixa de preço prompt |
|-------------|---------------------------------------|----------------------|
| Título (title) | `google/gemini-2.5-flash-lite` → Google AI Studio @ $p=0.050 $c=0.200 thr=89 lat=1439.5ms | $0.050–$0.180/prompt |
| Título (title) | `google/gemini-2.5-flash` → Google AI Studio @ $p=0.150 $c=1.250 thr=3 lat=2326ms | $0.150–$0.540/prompt |
| Título (title) | `qwen/qwen3.8-flash` → Alibaba @ $p=0.150 $c=0.470 thr=48 lat=4117.5ms | $0.150–$0.150/prompt |

| Compressão (compression) | `deepseek/deepseek-v4-flash-0731` → OpenInference @ $p=0.030 $c=0.100 thr=9 lat=2142ms | $0.030–$0.440/prompt |
| Compressão (compression) | `google/gemini-2.5-flash-lite` → Google AI Studio @ $p=0.050 $c=0.200 thr=89 lat=1439.5ms | $0.050–$0.180/prompt |
| Compressão (compression) | `google/gemini-2.5-flash` → Google AI Studio @ $p=0.150 $c=1.250 thr=3 lat=2326ms | $0.150–$0.540/prompt |

| Visão (vision) | `google/gemini-2.5-flash-lite` → Google AI Studio @ $p=0.050 $c=0.200 thr=89 lat=1439.5ms | $0.050–$0.180/prompt |
| Visão (vision) | `google/gemini-2.5-flash` → Google AI Studio @ $p=0.150 $c=1.250 thr=3 lat=2326ms | $0.150–$0.540/prompt |
| Visão (vision) | `openai/gpt-4o-mini` → Azure @ $p=0.150 $c=0.600 thr=26 lat=1373ms | $0.150–$0.165/prompt |

### Resumo recomendado por necessidade

| Necessidade | Modelo recomendado | Provider | Por quê |
|-------------|-------------------|----------|---------|
| **Título** | `google/gemini-2.5-flash-lite` | Google AI Studio | Mais barato ($0.05–0.10), rápido (127–185 t/s), sem necessidade de visão |
| **Compressão** | `deepseek/deepseek-v4-flash-0731` | Baidu | Já é o modelo principal; compressão fiel + barato (fp8 $0.06) |
| **Visão** | `google/gemini-2.5-flash-lite` | Google AI Studio | Tem visão, barato ($0.05–0.10), latência ok |

## 3) Recomendação de configuração (`provider_routing`)

> Aplicável via `hermes config set` (ou editar `config.yaml`). Provider routing é GLOBAL para o agente (aplica a todas as chamadas do modelo default). Por isso `only`/`order` usam slugs dos subprovedores.

```yaml
# Otimização sugerida para o AGENTE (equilíbrio custo + qualidade, foco tele interativo)
provider_routing:
  order:
    - baidu          # barato (fp8 $0.06) + 124 t/s + up 99.9%
    - coreweave      # fp8, menor latência (403ms), up 99.97%
    - reka           # maior throughput (152 t/s) p/ outputs longos
  sort: throughput
  require_parameters: true

# Modelos auxiliares — rotear p/ barrato sem tocar no agente
auxiliary:
  title:
    provider: openrouter
    model: google/gemini-2.5-flash-lite
  compression:
    provider: openrouter
    model: deepseek/deepseek-v4-flash-0731
  vision:
    provider: openrouter
    model: google/gemini-2.5-flash-lite
```

## 4) Notas / tradeoffs
- **Baidu fp8** é o melhor custo-benefício p/ agente: fp8 (qualidade alta), $0.06/$0.12, 124 t/s, uptime 99.9%.
- **CoreWeave fp8** se priorizar interatividade Telegram: 403ms de latência, uptime 99.97%.
- **Reka fp4** só se priorizar throughput máximo (152 t/s) — aceita qualidade fp4 e ctx 262K.
- **`sort`**: throughput prioriza pico de geração; latency prioriza 1º token (interativo); price prioriza custo.
- **Slugs** usados em `only`/`order` = nome do provedor em minúsculo (ex: `baidu`, `coreweave`, `reka`).
- Auxiliares têm `extra_body` independente — podem ter seu próprio `provider` se quiser restringir ainda mais.
- Contexto do Hermes exige ≥64K — todos os candidatos atendem (≥262K).
