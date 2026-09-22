# Levantamento OpenRouter — subprovedores e recomendação

Gerado: 2026-09-22 08:00 (automático, 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).

## Modelo: `deepseek/deepseek-v4-flash-0731` — DEFAULT atual (agente)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0300 | 1.0000 | 24 | 1250 | 99.54 |
| Sail Research | fp4 | 1048576 | 0.0380 | 0.5500 | 27 | 1358 | 99.64 |
| Relace | fp4 | 1048576 | 0.0400 | 0.6400 | 68 | 507 | 99.73 |
| StreamLake | fp8 | 1024000 | 0.0528 | 0.1584 | 30 | 32372.5 | 98.36 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 38 | 1080 | 99.66 |
| Inceptron | fp4 | 1048576 | 0.0600 | 0.3000 | 16 | 72943.5 | 99.44 |
| Reka | fp4 | 262144 | 0.0880 | 0.5280 | 29 | 2383 | 98.94 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 36 | 1137.5 | 97.41 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 65 | 890 | 99.98 |
| DigitalOcean | unknown | 1048576 | 0.1190 | 0.2380 | 27 | 20443.5 | 99.9 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 184 | 1188.5 | 99.98 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 151 | 646 | 99.96 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 90 | 537 | 99.99 |
| Nebius | fp8 | 1024000 | 0.1400 | 0.2800 | 66 | 44510 | 41.51 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 67 | 6572.5 | 99.59 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 49 | 11922.5 | 99.59 |
| Morph | unknown | 1048576 | 0.1420 | 0.3996 | 8 | 2467 | 95.02 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 40 | 1081 | 98.98 |
| Mancer 2 | fp8 | 1048576 | 0.2000 | 0.6000 | 32 | 1038.5 | 98.99 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 42 | 835 | 97.82 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 26 | 1728 | 98.17 |
| GMICloud | fp8 | 1048575 | 0.2860 | 0.8580 | 57 | 2494 | 99.93 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 39 | 950 | 99.99 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 60 | 3416 | 99.06 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 36 | 977 | 100.0 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 61 | 1355 | 99.81 |
| Baidu | fp8 | 1048576 | 0.4400 | 1.3200 | 84 | 963 | 99.49 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 58 | 1032.5 | 99.99 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 58 | 1928 | 99.79 |

## Modelo: `deepseek/deepseek-v4-pro-0813` — alternativa agente (qualidade/raciocínio)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Ionstream | unknown | 1048576 | 0.6240 | 2.8800 | 28 | 2840 | 99.61 |
| DeepSeek | unknown | 1048576 | 0.6600 | 1.9800 | 55 | 1494 | 100.0 |
| Wafer | unknown | 1048576 | 0.6700 | 2.9000 | 55 | 1327 | 98.89 |
| StreamLake | unknown | 1024000 | 0.6987 | 2.0960 | 48 | 2809.5 | 99.78 |
| Sail Research | fp4 | 1048576 | 0.7000 | 2.9600 | 17 | 2156 | 99.74 |
| Sail Research | fp4 | 1048576 | 0.7000 | 2.9600 | 16 | 2159 | 99.79 |
| Novita | fp8 | 1048576 | 0.9900 | 2.9700 | 50 | 1854 | 99.99 |
| GMICloud | fp8 | 1048575 | 1.0560 | 3.1680 | 44 | 3401 | 99.87 |
| Alibaba | unknown | 1000000 | 1.1220 | 3.3660 | 63 | 1331.5 | 99.98 |
| NextBit | fp8 | 1048576 | 1.1220 | 3.3660 | 45 | 2598.5 | 97.19 |
| DeepInfra | fp8 | 1048576 | 1.3000 | 2.6000 | 49 | 1297 | 99.48 |
| CoreWeave | fp8 | 1048576 | 1.3100 | 3.9600 | 91 | 598 | 97.87 |
| AtlasCloud | fp8 | 1048576 | 1.3200 | 3.9600 | 58 | 47598 | 99.63 |
| Baidu | fp8 | 1048576 | 1.3200 | 3.9600 | 49 | 1166.5 | 99.98 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 65 | 932 | 97.16 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 76 | 702 | 96.15 |
| Cloudflare | unknown | 1048576 | 1.3200 | 3.9600 | 31 | 2070 | 97.67 |
| DigitalOcean | unknown | 1048576 | 1.3200 | 3.9600 | 21 | 1285 | 99.78 |
| Fireworks | unknown | 1048576 | 1.3200 | 3.9600 | 53 | 1152 | 99.43 |
| Parasail | fp8 | 1048576 | 1.3200 | 3.9600 | 63 | 811 | 99.71 |
| SiliconFlow | fp8 | 1048576 | 1.3200 | 3.9600 | 50 | 2059 | 98.23 |
| Together | unknown | 1048576 | 1.3200 | 3.9600 | 78 | 1085.5 | 99.65 |
| Phala | unknown | 1048576 | 1.4500 | 4.3600 | 49.5 | 1837 | 99.71 |
| Venice | unknown | 1000000 | 1.6500 | 4.9500 | 77.5 | 834.5 | 97.86 |

## Modelo: `qwen/qwen3.8-flash` — alternativa agente (barata)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 49 | 1578 | 100.0 |

## Modelos auxiliares

### `google/gemini-2.5-flash-lite`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.0500 | 0.2000 | 259 | 452 | 99.99 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 68 | 564 | 99.84 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 243 | 605 | 95.41 |
| Google AI Studio | unknown | 1048576 | 0.1000 | 0.4000 | 79 | 795 | 99.6 |
| Google AI Studio | unknown | 1048576 | 0.1800 | 0.7200 | 114.5 | 751.5 | 100 |

### `google/gemini-2.5-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.1500 | 1.2500 | 166 | 1797 | 99.99 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 89 | 571 | 99.34 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 72 | 756 | 99.45 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 68 | 1916 | 82.65 |
| Google AI Studio | unknown | 1048576 | 0.3000 | 2.5000 | 79 | 490 | 99.92 |
| Google | unknown | 1048576 | 0.5400 | 4.5000 | 175 | 551 | 99.8 |
| Google AI Studio | unknown | 1048576 | 0.5400 | 4.5000 | None | None | 99.71 |

### `google/gemini-3.6-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google | unknown | 1048576 | 0.3750 | 1.8750 | 48 | 9536 | 72.46 |
| Google AI Studio | unknown | 1048576 | 0.3750 | 1.8750 | 110 | 3155.5 | 99.81 |
| Google | unknown | 1048576 | 0.7500 | 3.7500 | 124 | 1646 | 99.81 |
| Google AI Studio | unknown | 1048576 | 0.7500 | 3.7500 | 28 | 1129 | 99.83 |
| Google | unknown | 1048576 | 0.8250 | 4.1250 | None | None | 100 |
| Google | unknown | 1048576 | 1.3500 | 6.7500 | 180 | 2519 | 99.97 |
| Google AI Studio | unknown | 1048576 | 1.3500 | 6.7500 | 77 | 1166 | 99.94 |

### `openai/gpt-4o-mini`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Azure | unknown | 128000 | 0.1500 | 0.6000 | 24 | 1458 | 99.78 |
| OpenAI | unknown | 128000 | 0.1500 | 0.6000 | 45 | 580 | 99.96 |
| Azure | unknown | 128000 | 0.1650 | 0.6600 | 61 | 1101 | 100 |

### `deepseek/deepseek-v4-flash-0731`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0300 | 1.0000 | 24 | 1250 | 99.54 |
| Sail Research | fp4 | 1048576 | 0.0380 | 0.5500 | 27 | 1358 | 99.64 |
| Relace | fp4 | 1048576 | 0.0400 | 0.6400 | 68 | 507 | 99.73 |
| StreamLake | fp8 | 1024000 | 0.0528 | 0.1584 | 30 | 32372.5 | 98.36 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 38 | 1080 | 99.66 |
| Inceptron | fp4 | 1048576 | 0.0600 | 0.3000 | 16 | 72943.5 | 99.44 |
| Reka | fp4 | 262144 | 0.0880 | 0.5280 | 29 | 2383 | 98.94 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 36 | 1137.5 | 97.41 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 65 | 890 | 99.98 |
| DigitalOcean | unknown | 1048576 | 0.1190 | 0.2380 | 27 | 20443.5 | 99.9 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 184 | 1188.5 | 99.98 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 151 | 646 | 99.96 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 90 | 537 | 99.99 |
| Nebius | fp8 | 1024000 | 0.1400 | 0.2800 | 66 | 44510 | 41.51 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 67 | 6572.5 | 99.59 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 49 | 11922.5 | 99.59 |
| Morph | unknown | 1048576 | 0.1420 | 0.3996 | 8 | 2467 | 95.02 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 40 | 1081 | 98.98 |
| Mancer 2 | fp8 | 1048576 | 0.2000 | 0.6000 | 32 | 1038.5 | 98.99 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 42 | 835 | 97.82 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 26 | 1728 | 98.17 |
| GMICloud | fp8 | 1048575 | 0.2860 | 0.8580 | 57 | 2494 | 99.93 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 39 | 950 | 99.99 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 60 | 3416 | 99.06 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 36 | 977 | 100.0 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 61 | 1355 | 99.81 |
| Baidu | fp8 | 1048576 | 0.4400 | 1.3200 | 84 | 963 | 99.49 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 58 | 1032.5 | 99.99 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 58 | 1928 | 99.79 |

### `qwen/qwen3.8-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 49 | 1578 | 100.0 |

## Recomendação por necessidade

> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).

| Necessidade | Modelo recomendado | Melhor subprovedor |
|-------------|--------------------|--------------------|
| Título (title) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 94, $p 0.0500, 259 t/s, 452ms) |
| Compressão (compression) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 94, $p 0.0500, 259 t/s, 452ms) |
| Visão (vision) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 94, $p 0.0500, 259 t/s, 452ms) |
