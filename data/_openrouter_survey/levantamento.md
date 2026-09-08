# Levantamento OpenRouter — subprovedores e recomendação

Gerado: 2026-09-08 08:00 (automático, 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).

## Modelo: `deepseek/deepseek-v4-flash-0731` — DEFAULT atual (agente)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0500 | 0.1600 | 15 | 3442 | 98.57 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 24 | 910 | 99.43 |
| Relace | fp4 | 1048576 | 0.0650 | 0.1800 | 71 | 728.5 | 96.82 |
| Sail Research | fp4 | 1048576 | 0.0650 | 0.1800 | 26 | 1404.5 | 99.84 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 22 | 652.5 | 99.89 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 43 | 939 | 96.24 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 88 | 613 | 98.37 |
| Reka | fp4 | 262144 | 0.1100 | 0.6600 | 95 | 635 | 99.16 |
| Morph | bf16 | 1048576 | 0.1234 | 0.3475 | 7 | 1966.5 | 99.51 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 54 | 800 | 99.69 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 42 | 727 | 99.69 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 74 | 645 | 99.88 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 49 | 631 | 99.08 |
| StreamLake | fp8 | 1024000 | 0.1320 | 0.3960 | 88 | 1193 | 99.84 |
| Baidu | fp8 | 1048576 | 0.1400 | 0.2800 | 124 | 843.5 | 99.34 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 48 | 672 | 99.83 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 54 | 612 | 99.7 |
| Mancer 2 | fp8 | 1048576 | 0.1650 | 0.5000 | 26 | 781 | 95.52 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 36 | 1031 | 98.27 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 87 | 995 | 99.99 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 67 | 956 | 98.81 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 67 | 1554 | 99.6 |
| GMICloud | fp8 | 1048575 | 0.2860 | 0.8580 | 65 | 1858 | 70.27 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 76 | 987 | 99.76 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 89 | 2282 | 99.94 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 70 | 1692 | 99.99 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 39 | 1278 | 99.91 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 39 | 1565 | 99.94 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 47 | 1039.5 | 87.29 |

## Modelo: `deepseek/deepseek-v4-pro-0813` — alternativa agente (qualidade/raciocínio)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| DeepSeek | unknown | 1048576 | 0.6600 | 1.9800 | 22 | 1308 | 100.0 |
| Novita | fp8 | 1048576 | 0.9900 | 2.9700 | 42 | 1353 | 99.96 |
| StreamLake | unknown | 1024000 | 1.0494 | 3.1482 | 48 | 3793.5 | 99.77 |
| GMICloud | fp8 | 1048575 | 1.0560 | 3.1680 | 41 | 5914 | 99.64 |
| Ionstream | fp4 | 1048576 | 1.1000 | 3.3000 | 81 | 789 | 99.92 |
| Baidu | fp8 | 1048576 | 1.1194 | 3.3581 | 47 | 1005.5 | 99.95 |
| Alibaba | unknown | 1000000 | 1.1220 | 3.3660 | 49 | 1469.5 | 99.96 |
| NextBit | fp8 | 1048576 | 1.1220 | 3.3660 | 36 | 2499.5 | 99.77 |
| DeepInfra | fp8 | 1048576 | 1.3000 | 2.6000 | 58 | 979.5 | 99.68 |
| CoreWeave | fp8 | 1048576 | 1.3100 | 3.9600 | 35 | 1125 | 99.37 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 57 | 627 | 99.81 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 35 | 463 | 99.81 |
| Cloudflare | unknown | 1048576 | 1.3200 | 3.9600 | 54 | 1582 | 99.24 |
| DigitalOcean | unknown | 1048576 | 1.3200 | 3.9600 | 45 | 1158 | 98.89 |
| Fireworks | unknown | 1048576 | 1.3200 | 3.9600 | 65 | 1239.5 | 99.84 |
| Parasail | fp8 | 1048576 | 1.3200 | 3.9600 | 49 | 1532.5 | 99.67 |
| Sail Research | fp4 | 1048576 | 1.3200 | 3.9600 | 82 | 1995 | 99.92 |
| SiliconFlow | fp8 | 1048576 | 1.3200 | 3.9600 | 47 | 1456 | 100 |
| Together | unknown | 1048576 | 1.3200 | 3.9600 | 85 | 903 | 99.63 |
| Phala | unknown | 1048576 | 1.4500 | 4.3600 | 55 | 1508 | 99.74 |

## Modelo: `qwen/qwen3.8-flash` — alternativa agente (barata)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 45 | 2523 | 99.97 |

## Modelos auxiliares

### `google/gemini-2.5-flash-lite`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.0500 | 0.2000 | 67 | 675 | 99.99 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 77 | 431 | 99.95 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 37 | 1131 | 99.79 |
| Google AI Studio | unknown | 1048576 | 0.1000 | 0.4000 | 165 | 473 | 97.19 |
| Google AI Studio | unknown | 1048576 | 0.1800 | 0.7200 | 38.5 | 3405.5 | 100 |

### `google/gemini-2.5-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.1500 | 1.2500 | 22 | 2838 | 100 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 94 | 520 | 99.61 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 63.5 | 715 | 99.84 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 92 | 2296 | 87.9 |
| Google AI Studio | unknown | 1048576 | 0.3000 | 2.5000 | 99 | 473 | 99.94 |
| Google | unknown | 1048576 | 0.5400 | 4.5000 | 44 | 1185 | 99.9 |
| Google AI Studio | unknown | 1048576 | 0.5400 | 4.5000 | None | None | 99.8 |

### `google/gemini-3.6-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google | unknown | 1048576 | 0.3750 | 1.8750 | 31 | 8416 | 91.0 |
| Google AI Studio | unknown | 1048576 | 0.3750 | 1.8750 | 95 | 2903.5 | 99.46 |
| Google | unknown | 1048576 | 0.7500 | 3.7500 | 128 | 1620 | 98.95 |
| Google AI Studio | unknown | 1048576 | 0.7500 | 3.7500 | 57 | 1146 | 99.81 |
| Google | unknown | 1048576 | 0.8250 | 4.1250 | None | None | 100 |
| Google | unknown | 1048576 | 1.3500 | 6.7500 | 98 | 3035.5 | 100 |
| Google AI Studio | unknown | 1048576 | 1.3500 | 6.7500 | 117 | 1664.5 | 100 |

### `openai/gpt-4o-mini`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Azure | unknown | 128000 | 0.1500 | 0.6000 | 7 | 1374 | 99.68 |
| OpenAI | unknown | 128000 | 0.1500 | 0.6000 | 24 | 584 | 99.98 |
| Azure | unknown | 128000 | 0.1650 | 0.6600 | 62 | 1187 | 100 |

### `deepseek/deepseek-v4-flash-0731`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0500 | 0.1600 | 15 | 3442 | 98.57 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 24 | 910 | 99.43 |
| Relace | fp4 | 1048576 | 0.0650 | 0.1800 | 71 | 728.5 | 96.82 |
| Sail Research | fp4 | 1048576 | 0.0650 | 0.1800 | 26 | 1404.5 | 99.84 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 22 | 652.5 | 99.89 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 43 | 939 | 96.24 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 88 | 613 | 98.37 |
| Reka | fp4 | 262144 | 0.1100 | 0.6600 | 95 | 635 | 99.16 |
| Morph | bf16 | 1048576 | 0.1234 | 0.3475 | 7 | 1966.5 | 99.51 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 54 | 800 | 99.69 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 42 | 727 | 99.69 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 74 | 645 | 99.88 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 49 | 631 | 99.08 |
| StreamLake | fp8 | 1024000 | 0.1320 | 0.3960 | 88 | 1193 | 99.84 |
| Baidu | fp8 | 1048576 | 0.1400 | 0.2800 | 124 | 843.5 | 99.34 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 48 | 672 | 99.83 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 54 | 612 | 99.7 |
| Mancer 2 | fp8 | 1048576 | 0.1650 | 0.5000 | 26 | 781 | 95.52 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 36 | 1031 | 98.27 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 87 | 995 | 99.99 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 67 | 956 | 98.81 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 67 | 1554 | 99.6 |
| GMICloud | fp8 | 1048575 | 0.2860 | 0.8580 | 65 | 1858 | 70.27 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 76 | 987 | 99.76 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 89 | 2282 | 99.94 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 70 | 1692 | 99.99 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 39 | 1278 | 99.91 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 39 | 1565 | 99.94 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 47 | 1039.5 | 87.29 |

### `qwen/qwen3.8-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 45 | 3056 | 99.97 |

## Recomendação por necessidade

> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).

| Necessidade | Modelo recomendado | Melhor subprovedor |
|-------------|--------------------|--------------------|
| Título (title) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 93, $p 0.1000, 165 t/s, 473ms) |
| Compressão (compression) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 93, $p 0.1000, 165 t/s, 473ms) |
| Visão (vision) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 93, $p 0.1000, 165 t/s, 473ms) |
