# Levantamento OpenRouter — subprovedores e recomendação

Gerado: 2026-09-18 08:00 (automático, 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).

## Modelo: `deepseek/deepseek-v4-flash-0731` — DEFAULT atual (agente)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Inceptron | fp4 | 1048576 | 0.0558 | 0.1767 | 13.5 | 1330 | 89.32 |
| StreamLake | fp8 | 1024000 | 0.0596 | 0.1787 | 28 | 1937 | 97.47 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 36 | 856 | 99.78 |
| Relace | fp4 | 1048576 | 0.0600 | 0.1200 | 45 | 941 | 99.65 |
| Sail Research | fp4 | 1048576 | 0.0741 | 0.3420 | 24 | 2085 | 96.4 |
| Sail Research | fp4 | 1048576 | 0.0741 | 0.3420 | 26 | 1429.5 | 96.59 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 75 | 450 | 99.11 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 107 | 410 | 99.93 |
| Reka | fp4 | 262144 | 0.1100 | 0.6600 | 98 | 614 | 99.86 |
| DigitalOcean | unknown | 1048576 | 0.1190 | 0.2380 | 45 | 658 | 99.91 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 152 | 544 | 99.94 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 117 | 448 | 99.94 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 85 | 429 | 99.99 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 55 | 626 | 99.71 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 41 | 1109 | 99.69 |
| Morph | bf16 | 1048576 | 0.1420 | 0.3996 | 8 | 2872 | 97.52 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 45 | 1212 | 99.45 |
| Mancer 2 | fp8 | 1048576 | 0.2000 | 0.6000 | 29 | 795 | 99.43 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 19 | 1172.5 | 97.27 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 23 | 1447 | 99.63 |
| GMICloud | fp8 | 1048575 | 0.2860 | 0.8580 | 55 | 2002.5 | 99.88 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 13 | 854 | 100.0 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 41 | 3206 | 99.22 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 35 | 1513 | 99.98 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 76 | 1062 | 99.85 |
| Baidu | fp8 | 1048576 | 0.4400 | 1.3200 | 122 | 744 | 99.96 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 38 | 692 | 99.99 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 54 | 2076 | 99.81 |

## Modelo: `deepseek/deepseek-v4-pro-0813` — alternativa agente (qualidade/raciocínio)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| DeepSeek | unknown | 1048576 | 0.6600 | 1.9800 | 43 | 1341.5 | 100.0 |
| Sail Research | fp4 | 1048576 | 0.7000 | 2.9600 | 12 | 2981.5 | 99.5 |
| Sail Research | fp4 | 1048576 | 0.7000 | 2.9600 | 12 | 2893 | 99.56 |
| Ionstream | unknown | 1048576 | 0.8800 | 2.8800 | 26 | 2170.5 | 98.51 |
| StreamLake | unknown | 1024000 | 0.9834 | 2.9502 | 54 | 2135 | 99.41 |
| Novita | fp8 | 1048576 | 0.9900 | 2.9700 | 66 | 1728 | 99.99 |
| GMICloud | fp8 | 1048575 | 1.0560 | 3.1680 | 38 | 4230 | 99.86 |
| Alibaba | unknown | 1000000 | 1.1220 | 3.3660 | 54 | 1292 | 100.0 |
| NextBit | fp8 | 1048576 | 1.1220 | 3.3660 | 39 | 4305 | 98.97 |
| DeepInfra | fp8 | 1048576 | 1.3000 | 2.6000 | 40 | 905 | 99.23 |
| CoreWeave | fp8 | 1048576 | 1.3100 | 3.9600 | 41 | 817 | 99.93 |
| AtlasCloud | fp8 | 1048576 | 1.3200 | 3.9600 | 51 | 1240 | 100 |
| Baidu | fp8 | 1048576 | 1.3200 | 3.9600 | 45.5 | 2621.5 | 99.99 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 85 | 562 | 98.57 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 60 | 597 | 98.54 |
| Cloudflare | unknown | 1048576 | 1.3200 | 3.9600 | 49 | 1614 | 93.24 |
| DigitalOcean | unknown | 1048576 | 1.3200 | 3.9600 | 26 | 863 | 99.8 |
| Fireworks | unknown | 1048576 | 1.3200 | 3.9600 | 54.5 | 1318.5 | 99.26 |
| Parasail | fp8 | 1048576 | 1.3200 | 3.9600 | 53 | 897 | 99.74 |
| SiliconFlow | fp8 | 1048576 | 1.3200 | 3.9600 | 47 | 1885 | 98.65 |
| Together | unknown | 1048576 | 1.3200 | 3.9600 | 86 | 824 | 99.55 |
| Phala | unknown | 1048576 | 1.4500 | 4.3600 | 52 | 1987 | 99.79 |
| Venice | unknown | 1000000 | 1.6500 | 4.9500 | 81 | 628 | 98.57 |

## Modelo: `qwen/qwen3.8-flash` — alternativa agente (barata)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 50 | 1652 | 100.0 |

## Modelos auxiliares

### `google/gemini-2.5-flash-lite`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.0500 | 0.2000 | 88 | 790 | 99.98 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 74 | 513 | 99.87 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 54 | 1058 | 98.8 |
| Google AI Studio | unknown | 1048576 | 0.1000 | 0.4000 | 112 | 515.5 | 99.29 |
| Google AI Studio | unknown | 1048576 | 0.1800 | 0.7200 | 28.5 | 626 | 99.7 |

### `google/gemini-2.5-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.1500 | 1.2500 | 5 | 2721 | 99.99 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 89 | 535 | 99.43 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 73 | 656 | 99.37 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 60 | 1843 | 84.22 |
| Google AI Studio | unknown | 1048576 | 0.3000 | 2.5000 | 77 | 493 | 99.94 |
| Google | unknown | 1048576 | 0.5400 | 4.5000 | 18 | 789 | 99.9 |
| Google AI Studio | unknown | 1048576 | 0.5400 | 4.5000 | 130.5 | 357.5 | 99.62 |

### `google/gemini-3.6-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google | unknown | 1048576 | 0.3750 | 1.8750 | 49 | 8410 | 85.98 |
| Google AI Studio | unknown | 1048576 | 0.3750 | 1.8750 | 136.5 | 2478.5 | 99.99 |
| Google | unknown | 1048576 | 0.7500 | 3.7500 | 137 | 1667.5 | 99.75 |
| Google AI Studio | unknown | 1048576 | 0.7500 | 3.7500 | 42 | 1282 | 99.79 |
| Google | unknown | 1048576 | 0.8250 | 4.1250 | None | None | 100 |
| Google | unknown | 1048576 | 1.3500 | 6.7500 | 101.5 | 1520.5 | 99.97 |
| Google AI Studio | unknown | 1048576 | 1.3500 | 6.7500 | 48 | 754 | 99.93 |

### `openai/gpt-4o-mini`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Azure | unknown | 128000 | 0.1500 | 0.6000 | 26 | 1749 | 98.41 |
| OpenAI | unknown | 128000 | 0.1500 | 0.6000 | 53 | 526 | 99.95 |
| Azure | unknown | 128000 | 0.1650 | 0.6600 | 71 | 807 | 100 |

### `deepseek/deepseek-v4-flash-0731`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Inceptron | fp4 | 1048576 | 0.0558 | 0.1767 | 13.5 | 1330 | 89.32 |
| StreamLake | fp8 | 1024000 | 0.0596 | 0.1787 | 28 | 1937 | 97.47 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 36 | 856 | 99.78 |
| Relace | fp4 | 1048576 | 0.0600 | 0.1200 | 45 | 941 | 99.65 |
| Sail Research | fp4 | 1048576 | 0.0741 | 0.3420 | 24 | 2085 | 96.4 |
| Sail Research | fp4 | 1048576 | 0.0741 | 0.3420 | 26 | 1429.5 | 96.59 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 75 | 450 | 99.11 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 107 | 410 | 99.93 |
| Reka | fp4 | 262144 | 0.1100 | 0.6600 | 98 | 614 | 99.86 |
| DigitalOcean | unknown | 1048576 | 0.1190 | 0.2380 | 45 | 658 | 99.91 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 152 | 544 | 99.94 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 117 | 448 | 99.94 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 85 | 429 | 99.99 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 55 | 626 | 99.71 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 41 | 1109 | 99.69 |
| Morph | bf16 | 1048576 | 0.1420 | 0.3996 | 8 | 2872 | 97.52 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 45 | 1212 | 99.45 |
| Mancer 2 | fp8 | 1048576 | 0.2000 | 0.6000 | 29 | 795 | 99.43 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 19 | 1172.5 | 97.27 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 23 | 1447 | 99.63 |
| GMICloud | fp8 | 1048575 | 0.2860 | 0.8580 | 55 | 2002.5 | 99.88 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 13 | 854 | 100.0 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 41 | 3206 | 99.22 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 35 | 1513 | 99.98 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 76 | 1062 | 99.85 |
| Baidu | fp8 | 1048576 | 0.4400 | 1.3200 | 122 | 744 | 99.96 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 38 | 692 | 99.99 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 54 | 2076 | 99.81 |

### `qwen/qwen3.8-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 51 | 1594 | 100.0 |

## Recomendação por necessidade

> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).

| Necessidade | Modelo recomendado | Melhor subprovedor |
|-------------|--------------------|--------------------|
| Título (title) | `google/gemini-2.5-flash` | Google AI Studio (visão) (score 87, $p 0.5400, 130.5 t/s, 357.5ms) |
| Compressão (compression) | `deepseek/deepseek-v4-flash-0731` | BaseTen (score 92, $p 0.1300, 152 t/s, 544ms) |
| Visão (vision) | `google/gemini-2.5-flash` | Google AI Studio (visão) (score 87, $p 0.5400, 130.5 t/s, 357.5ms) |
