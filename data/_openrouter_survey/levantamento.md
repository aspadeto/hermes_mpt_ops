# Levantamento OpenRouter — subprovedores e recomendação

Gerado: 2026-09-15 08:00 (automático, 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).

## Modelo: `deepseek/deepseek-v4-flash-0731` — DEFAULT atual (agente)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0400 | 0.1000 | 20 | 1494.5 | 99.26 |
| Inceptron | fp4 | 1048576 | 0.0549 | 0.1734 | 12 | 1076 | 99.88 |
| StreamLake | fp8 | 1024000 | 0.0572 | 0.1716 | 33.5 | 2423.5 | 97.14 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 44 | 771 | 99.87 |
| Relace | fp4 | 1048576 | 0.0600 | 0.1200 | 45 | 940 | 98.95 |
| Sail Research | fp4 | 1048576 | 0.0741 | 0.3420 | 43 | 1206 | 98.83 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 101 | 445 | 96.53 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 104 | 382 | 97.88 |
| Reka | fp4 | 262144 | 0.1100 | 0.6600 | 77 | 682 | 97.47 |
| DigitalOcean | unknown | 1048576 | 0.1190 | 0.2380 | 32 | 942 | 99.86 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 135 | 491 | 99.96 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 118 | 455 | 99.97 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 76 | 444 | 99.98 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 33 | 818 | 98.32 |
| Morph | bf16 | 1048576 | 0.1420 | 0.3996 | 5 | 2085 | 99.97 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 39 | 984 | 99.45 |
| Mancer 2 | fp8 | 1048576 | 0.2000 | 0.6000 | 67 | 768.5 | 99.19 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 62 | 1092 | 97.32 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 54 | 2703 | 92.33 |
| GMICloud | fp8 | 1048575 | 0.2860 | 0.8580 | 73 | 1778 | 99.9 |
| Phala | unknown | 1048576 | 0.3080 | 0.9240 | 53 | 1666 | 99.59 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 71 | 1136.5 | 100.0 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 56 | 1752 | 99.93 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 61 | 1377 | 99.97 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 70 | 962 | 99.94 |
| Baidu | fp8 | 1048576 | 0.4400 | 1.3200 | 102 | 736 | 99.8 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 57 | 934 | 99.95 |

## Modelo: `deepseek/deepseek-v4-pro-0813` — alternativa agente (qualidade/raciocínio)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| DeepSeek | unknown | 1048576 | 0.6600 | 1.9800 | 39 | 1591 | 99.96 |
| Ionstream | unknown | 1048576 | 0.9600 | 2.8800 | 18 | 3667 | 98.8 |
| StreamLake | unknown | 1024000 | 0.9834 | 2.9502 | 56 | 2589 | 99.31 |
| Novita | fp8 | 1048576 | 0.9900 | 2.9700 | 46 | 2115 | 99.89 |
| Phala | unknown | 1048576 | 1.0150 | 3.0520 | 35 | 3022.5 | 99.76 |
| GMICloud | fp8 | 1048575 | 1.0560 | 3.1680 | 47 | 2774 | 99.75 |
| Alibaba | unknown | 1000000 | 1.1220 | 3.3660 | 39 | 1351 | 99.88 |
| NextBit | fp8 | 1048576 | 1.1220 | 3.3660 | 26 | 3978 | 99.66 |
| DeepInfra | fp8 | 1048576 | 1.3000 | 2.6000 | 50 | 1027 | 99.6 |
| CoreWeave | fp8 | 1048576 | 1.3100 | 3.9600 | 115 | 608 | 99.93 |
| Baidu | fp8 | 1048576 | 1.3200 | 3.9600 | 57 | 779 | 99.91 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 73 | 716 | 99.45 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 49 | 484.5 | 99.34 |
| Cloudflare | unknown | 1048576 | 1.3200 | 3.9600 | 39 | 1665 | 93.17 |
| DigitalOcean | unknown | 1048576 | 1.3200 | 3.9600 | 26 | 938 | 99.48 |
| Fireworks | unknown | 1048576 | 1.3200 | 3.9600 | 47 | 1184 | 99.78 |
| Parasail | fp8 | 1048576 | 1.3200 | 3.9600 | 58 | 903 | 98.69 |
| Sail Research | fp4 | 1048576 | 1.3200 | 3.9600 | 7 | 1765 | 99.6 |
| SiliconFlow | fp8 | 1048576 | 1.3200 | 3.9600 | 29 | 1684.5 | 96.53 |
| Together | unknown | 1048576 | 1.3200 | 3.9600 | 145 | 697 | 97.62 |
| Venice | unknown | 1000000 | 1.6500 | 4.9500 | 67 | 1318 | 97.17 |

## Modelo: `qwen/qwen3.8-flash` — alternativa agente (barata)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 47 | 1673.5 | 99.73 |
| Makora | fp4 | 262144 | 0.1500 | 0.4700 | 94 | 776 | 98.96 |

## Modelos auxiliares

### `google/gemini-2.5-flash-lite`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.0500 | 0.2000 | 256 | 454 | 99.96 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 75 | 469 | 99.92 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 63 | 1073.5 | 98.75 |
| Google AI Studio | unknown | 1048576 | 0.1000 | 0.4000 | 146 | 598 | 98.5 |
| Google AI Studio | unknown | 1048576 | 0.1800 | 0.7200 | 32 | 522.5 | 99.6 |

### `google/gemini-2.5-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.1500 | 1.2500 | 4 | 3988.5 | 100.0 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 86 | 703 | 99.31 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 60 | 583 | 99.42 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 69 | 1598 | 87.13 |
| Google AI Studio | unknown | 1048576 | 0.3000 | 2.5000 | 60 | 464 | 99.96 |
| Google | unknown | 1048576 | 0.5400 | 4.5000 | 121 | 548 | 99.6 |
| Google AI Studio | unknown | 1048576 | 0.5400 | 4.5000 | 49.5 | 383 | 100 |

### `google/gemini-3.6-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google | unknown | 1048576 | 0.3750 | 1.8750 | 61 | 7568 | 79.8 |
| Google AI Studio | unknown | 1048576 | 0.3750 | 1.8750 | 104 | 1278 | 99.85 |
| Google | unknown | 1048576 | 0.7500 | 3.7500 | 135 | 1390 | 99.49 |
| Google AI Studio | unknown | 1048576 | 0.7500 | 3.7500 | 57 | 1225 | 99.79 |
| Google | unknown | 1048576 | 0.8250 | 4.1250 | None | None | 100 |
| Google | unknown | 1048576 | 1.3500 | 6.7500 | 74 | 1341 | 99.96 |
| Google AI Studio | unknown | 1048576 | 1.3500 | 6.7500 | 73 | 1060 | 99.67 |

### `openai/gpt-4o-mini`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Azure | unknown | 128000 | 0.1500 | 0.6000 | 23 | 1471 | 99.29 |
| OpenAI | unknown | 128000 | 0.1500 | 0.6000 | 51 | 527 | 99.98 |
| Azure | unknown | 128000 | 0.1650 | 0.6600 | 65 | 1077 | 100 |

### `deepseek/deepseek-v4-flash-0731`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0400 | 0.1000 | 20 | 1494.5 | 99.26 |
| Inceptron | fp4 | 1048576 | 0.0549 | 0.1734 | 12 | 1076 | 99.88 |
| StreamLake | fp8 | 1024000 | 0.0572 | 0.1716 | 33.5 | 2423.5 | 97.14 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 44 | 771 | 99.87 |
| Relace | fp4 | 1048576 | 0.0600 | 0.1200 | 45 | 940 | 98.95 |
| Sail Research | fp4 | 1048576 | 0.0741 | 0.3420 | 43 | 1206 | 98.83 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 101 | 445 | 96.53 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 104 | 382 | 97.88 |
| Reka | fp4 | 262144 | 0.1100 | 0.6600 | 77 | 682 | 97.47 |
| DigitalOcean | unknown | 1048576 | 0.1190 | 0.2380 | 32 | 942 | 99.86 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 135 | 491 | 99.96 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 118 | 455 | 99.97 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 76 | 444 | 99.98 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 33 | 818 | 98.32 |
| Morph | bf16 | 1048576 | 0.1420 | 0.3996 | 5 | 2085 | 99.97 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 39 | 984 | 99.45 |
| Mancer 2 | fp8 | 1048576 | 0.2000 | 0.6000 | 67 | 768.5 | 99.19 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 62 | 1092 | 97.32 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 54 | 2703 | 92.33 |
| GMICloud | fp8 | 1048575 | 0.2860 | 0.8580 | 73 | 1778 | 99.9 |
| Phala | unknown | 1048576 | 0.3080 | 0.9240 | 53 | 1666 | 99.59 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 71 | 1136.5 | 100.0 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 56 | 1752 | 99.93 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 61 | 1377 | 99.97 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 70 | 962 | 99.94 |
| Baidu | fp8 | 1048576 | 0.4400 | 1.3200 | 102 | 736 | 99.8 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 57 | 934 | 99.95 |

### `qwen/qwen3.8-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 47 | 1673.5 | 99.73 |
| Makora | fp4 | 262144 | 0.1500 | 0.4700 | 94 | 776 | 98.96 |

## Recomendação por necessidade

> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).

| Necessidade | Modelo recomendado | Melhor subprovedor |
|-------------|--------------------|--------------------|
| Título (title) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 94, $p 0.0500, 256 t/s, 454ms) |
| Compressão (compression) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 94, $p 0.0500, 256 t/s, 454ms) |
| Visão (vision) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 94, $p 0.0500, 256 t/s, 454ms) |
