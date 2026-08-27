# Levantamento OpenRouter — subprovedores e recomendação

Gerado: 2026-08-27 15:27 (automático, 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).

## Modelo: `deepseek/deepseek-v4-flash-0731` — DEFAULT atual (agente)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp4 | 1048576 | 0.0300 | 0.1000 | 9 | 2150 | 99.98 |
| Relace | fp4 | 1048576 | 0.0500 | 0.1000 | 68 | 959.5 | 99.82 |
| Baidu | fp8 | 1048576 | 0.0599 | 0.1198 | 120 | 709 | 99.92 |
| Ambient | fp4 | 1048576 | 0.0800 | 0.1800 | 51 | 571 | 99.06 |
| DeepInfra | fp8 | 1048576 | 0.0800 | 0.1800 | 40 | 575 | 98.57 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 31 | 560 | 99.58 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 99 | 598 | 92.56 |
| Morph | bf16 | 1048576 | 0.0987 | 0.2780 | 10 | 2400 | 93.97 |
| GMICloud | fp8 | 1048575 | 0.1120 | 0.2240 | 47 | 2397 | 97.68 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 42 | 667 | 96.85 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 111 | 420 | 99.97 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 66 | 596 | 99.72 |
| AkashML | fp8 | 1048576 | 0.1400 | 0.2800 | 46 | 926 | 99.75 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 41 | 827 | 97.99 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 56 | 631 | 99.61 |
| Mancer 2 | fp8 | 1048576 | 0.1500 | 0.4500 | 40 | 670.5 | 98.06 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 40 | 863 | 97.1 |
| Alibaba | unknown | 1000000 | 0.1760 | 0.5280 | 30 | 1296 | 99.99 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 80 | 1166 | 99.99 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 48 | 713.5 | 99.62 |
| Phala | unknown | 1048576 | 0.2200 | 0.6600 | 58 | 1754 | 97.68 |
| Reka | fp4 | 262144 | 0.2200 | 0.6600 | 126 | 582 | 98.23 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 46 | 1594 | 99.18 |
| StreamLake | fp8 | 1024000 | 0.2200 | 0.6600 | 39 | 977 | 99.9 |
| Wafer | unknown | 1048576 | 0.2800 | 0.5600 | 139 | 1414 | 99.18 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 47 | 1957 | 98.48 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 85 | 902 | 99.97 |
| NextBit | fp8 | 1048576 | 0.4400 | 1.3200 | 25 | 2206.5 | 99.39 |
| Novita | fp8 | 1048576 | 0.4400 | 1.3200 | 75 | 1476 | 99.89 |

## Modelo: `deepseek/deepseek-v4-pro-0813` — alternativa agente (qualidade/raciocínio)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.5808 | 1.7424 | 50 | 1415.5 | 99.96 |
| DeepSeek | unknown | 1048576 | 0.6600 | 1.9800 | 35 | 1335 | 100.0 |
| StreamLake | unknown | 1024000 | 0.6600 | 1.9800 | 48 | 3934.5 | 99.85 |
| GMICloud | fp8 | 1048575 | 1.1220 | 3.3660 | 45 | 4362 | 99.09 |
| DeepInfra | fp8 | 1048576 | 1.3000 | 2.6000 | 20 | 3539.5 | 84.9 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 69 | 629.5 | 99.58 |
| Cloudflare | unknown | 1048576 | 1.3200 | 3.9600 | 39 | 3195 | 99.72 |
| DigitalOcean | unknown | 1048576 | 1.3200 | 3.9600 | 40 | 1030 | 99.28 |
| Fireworks | unknown | 1048576 | 1.3200 | 3.9600 | 65 | 1366 | 99.91 |
| Novita | fp8 | 1048576 | 1.3200 | 3.9600 | 45 | 1307 | 98.17 |
| Parasail | fp8 | 1048576 | 1.3200 | 3.9600 | 63 | 721 | 98.46 |
| SiliconFlow | fp8 | 1048576 | 1.3200 | 3.9600 | 49 | 1118.5 | 99.77 |
| Together | unknown | 1048576 | 1.3200 | 3.9600 | 47 | 7572 | 95.2 |
| Phala | unknown | 1048576 | 1.4500 | 4.3600 | 58 | 1705.5 | 97.36 |

## Modelo: `qwen/qwen3.8-flash` — alternativa agente (barata)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 49 | 3756.5 | 99.99 |

## Modelos auxiliares

### `google/gemini-2.5-flash-lite`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.0500 | 0.2000 | 75 | 1487.5 | 99.78 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 132 | 427 | 99.65 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 128 | 417 | 99.75 |
| Google AI Studio | unknown | 1048576 | 0.1000 | 0.4000 | 185 | 411 | 99.78 |
| Google AI Studio | unknown | 1048576 | 0.1800 | 0.7200 | None | None | 99.78 |

### `google/gemini-2.5-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.1500 | 1.2500 | 3 | 2313 | 99.97 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 66 | 813.5 | 99.6 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 83 | 622 | 98.4 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 62 | 1366 | 66.4 |
| Google AI Studio | unknown | 1048576 | 0.3000 | 2.5000 | 87 | 778 | 99.97 |
| Google | unknown | 1048576 | 0.5400 | 4.5000 | 42 | 1300 | 99.6 |
| Google AI Studio | unknown | 1048576 | 0.5400 | 4.5000 | 41 | 371 | 99.97 |

### `google/gemini-3.6-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google | unknown | 1048576 | 0.3750 | 1.8750 | 30.5 | 8162 | 99.6 |
| Google AI Studio | unknown | 1048576 | 0.3750 | 1.8750 | 101 | 1908 | 99.42 |
| Google | unknown | 1048576 | 0.7500 | 3.7500 | 128 | 2030.5 | 99.6 |
| Google AI Studio | unknown | 1048576 | 0.7500 | 3.7500 | 99 | 1797 | 99.42 |
| Google | unknown | 1048576 | 0.8250 | 4.1250 | 65 | 878 | 100 |
| Google | unknown | 1048576 | 1.3500 | 6.7500 | 54 | 1813 | 99.6 |
| Google AI Studio | unknown | 1048576 | 1.3500 | 6.7500 | 59 | 1330 | 99.42 |

### `openai/gpt-4o-mini`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Azure | unknown | 128000 | 0.1500 | 0.6000 | 26 | 1374 | 99.86 |
| OpenAI | unknown | 128000 | 0.1500 | 0.6000 | 42 | 533 | 99.97 |
| Azure | unknown | 128000 | 0.1650 | 0.6600 | None | None | 100 |

### `deepseek/deepseek-v4-flash-0731`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp4 | 1048576 | 0.0300 | 0.1000 | 9 | 2150 | 99.98 |
| Relace | fp4 | 1048576 | 0.0500 | 0.1000 | 68 | 959.5 | 99.82 |
| Baidu | fp8 | 1048576 | 0.0599 | 0.1198 | 120 | 709 | 99.92 |
| Ambient | fp4 | 1048576 | 0.0800 | 0.1800 | 51 | 571 | 99.06 |
| DeepInfra | fp8 | 1048576 | 0.0800 | 0.1800 | 40 | 575 | 98.57 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 31 | 560 | 99.58 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 99 | 598 | 92.56 |
| Morph | bf16 | 1048576 | 0.0987 | 0.2780 | 10 | 2400 | 93.97 |
| GMICloud | fp8 | 1048575 | 0.1120 | 0.2240 | 47 | 2397 | 97.68 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 42 | 667 | 96.85 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 111 | 420 | 99.97 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 66 | 596 | 99.72 |
| AkashML | fp8 | 1048576 | 0.1400 | 0.2800 | 46 | 926 | 99.75 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 41 | 827 | 97.99 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 56 | 631 | 99.61 |
| Mancer 2 | fp8 | 1048576 | 0.1500 | 0.4500 | 40 | 670.5 | 98.06 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 40 | 863 | 97.1 |
| Alibaba | unknown | 1000000 | 0.1760 | 0.5280 | 30 | 1296 | 99.99 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 80 | 1166 | 99.99 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 48 | 713.5 | 99.62 |
| Phala | unknown | 1048576 | 0.2200 | 0.6600 | 58 | 1754 | 97.68 |
| Reka | fp4 | 262144 | 0.2200 | 0.6600 | 126 | 582 | 98.23 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 46 | 1594 | 99.18 |
| StreamLake | fp8 | 1024000 | 0.2200 | 0.6600 | 39 | 977 | 99.9 |
| Wafer | unknown | 1048576 | 0.2800 | 0.5600 | 139 | 1414 | 99.18 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 47 | 1957 | 98.48 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 85 | 902 | 99.97 |
| NextBit | fp8 | 1048576 | 0.4400 | 1.3200 | 25 | 2206.5 | 99.39 |
| Novita | fp8 | 1048576 | 0.4400 | 1.3200 | 75 | 1476 | 99.89 |

### `qwen/qwen3.8-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 49 | 3756.5 | 99.99 |

## Recomendação por necessidade

> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).

| Necessidade | Modelo recomendado | Melhor subprovedor |
|-------------|--------------------|--------------------|
| Título (title) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 94, $p 0.1000, 185 t/s, 411ms) |
| Compressão (compression) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 94, $p 0.1000, 185 t/s, 411ms) |
| Visão (vision) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 94, $p 0.1000, 185 t/s, 411ms) |
