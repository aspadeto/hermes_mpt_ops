# Levantamento OpenRouter — subprovedores e recomendação

Gerado: 2026-09-04 08:00 (automático, 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).

## Modelo: `deepseek/deepseek-v4-flash-0731` — DEFAULT atual (agente)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0500 | 0.1600 | 16 | 656 | 99.81 |
| AkashML | fp8 | 1048576 | 0.0650 | 0.1800 | 17 | 1341 | 95.49 |
| Relace | fp4 | 1048576 | 0.0650 | 0.1800 | 53 | 1109 | 98.37 |
| Sail Research | fp4 | 1048576 | 0.0650 | 0.1800 | 19 | 1714.5 | 99.73 |
| DeepInfra | fp8 | 1048576 | 0.0800 | 0.1800 | 26 | 795 | 99.36 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 33 | 567 | 99.59 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 58 | 943 | 96.84 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 95 | 1193 | 95.89 |
| Reka | fp4 | 262144 | 0.1100 | 0.6600 | 74 | 747 | 99.77 |
| Morph | bf16 | 1048576 | 0.1234 | 0.3475 | 47 | 1047 | 85.77 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 70 | 558.5 | 96.36 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 62 | 545 | 96.1 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 118 | 821 | 99.9 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 23 | 1402 | 99.04 |
| StreamLake | fp8 | 1024000 | 0.1320 | 0.3960 | 104 | 1437 | 99.17 |
| Baidu | fp8 | 1048576 | 0.1400 | 0.2800 | 108 | 1028 | 99.78 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 55 | 668 | 99.83 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 49 | 919 | 99.03 |
| Mancer 2 | fp8 | 1048576 | 0.1750 | 0.5000 | 26 | 801 | 97.72 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 38 | 1137 | 96.92 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 68 | 612 | 100.0 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 43 | 1194 | 92.56 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 58 | 1556 | 99.6 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 67 | 1398.5 | 99.94 |
| GMICloud | fp8 | 1048575 | 0.3520 | 1.0560 | 71 | 2799 | 87.11 |
| NextBit | fp8 | 1048576 | 0.4000 | 1.2000 | 54 | 2442.5 | 98.85 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 93 | 1285 | 99.94 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 49 | 1357 | 99.47 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 45 | 837 | 99.85 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 30 | 649 | 93.59 |

## Modelo: `deepseek/deepseek-v4-pro-0813` — alternativa agente (qualidade/raciocínio)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| DeepSeek | unknown | 1048576 | 0.6600 | 1.9800 | 21 | 1181 | 99.99 |
| Novita | fp8 | 1048576 | 1.1088 | 3.3264 | 45 | 1378.5 | 99.94 |
| StreamLake | unknown | 1024000 | 1.1154 | 3.3462 | 51 | 4037.5 | 99.93 |
| Alibaba | unknown | 1000000 | 1.1220 | 3.3660 | 39 | 1708 | 99.93 |
| GMICloud | fp8 | 1048575 | 1.1220 | 3.3660 | 45 | 4329.5 | 98.48 |
| DeepInfra | fp8 | 1048576 | 1.3000 | 2.6000 | 69 | 794 | 99.57 |
| CoreWeave | fp8 | 1048576 | 1.3100 | 3.9600 | 105 | 803 | 99.86 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 46 | 448 | 99.84 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 39 | 432 | 99.73 |
| Cloudflare | unknown | 1048576 | 1.3200 | 3.9600 | 58 | 1561 | 99.54 |
| DigitalOcean | unknown | 1048576 | 1.3200 | 3.9600 | 47 | 996.5 | 99.7 |
| Fireworks | unknown | 1048576 | 1.3200 | 3.9600 | 61 | 1345.5 | 98.86 |
| NextBit | fp8 | 1048576 | 1.3200 | 3.9600 | 53 | 3885 | 99.3 |
| Parasail | fp8 | 1048576 | 1.3200 | 3.9600 | 71 | 701 | 99.66 |
| Sail Research | fp4 | 1048576 | 1.3200 | 3.9600 | 97 | 801.5 | 99.89 |
| SiliconFlow | fp8 | 1048576 | 1.3200 | 3.9600 | 47 | 1460 | 100.0 |
| Together | unknown | 1048576 | 1.3200 | 3.9600 | 61.5 | 1080 | 99.05 |
| Phala | unknown | 1048576 | 1.4500 | 4.3600 | 51 | 1325 | 99.92 |

## Modelo: `qwen/qwen3.8-flash` — alternativa agente (barata)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 52 | 2294.5 | 100.0 |

## Modelos auxiliares

### `google/gemini-2.5-flash-lite`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.0500 | 0.2000 | 60 | 676 | 100.0 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 90 | 521 | 99.83 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 63 | 1091 | 99.64 |
| Google AI Studio | unknown | 1048576 | 0.1000 | 0.4000 | 152 | 665 | 97.57 |
| Google AI Studio | unknown | 1048576 | 0.1800 | 0.7200 | 189.5 | 473 | 100 |

### `google/gemini-2.5-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.1500 | 1.2500 | 3 | 3749 | 100.0 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 87 | 578 | 99.32 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 55 | 974 | 99.69 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 52 | 1172 | 97.6 |
| Google AI Studio | unknown | 1048576 | 0.3000 | 2.5000 | 68 | 538 | 99.9 |
| Google | unknown | 1048576 | 0.5400 | 4.5000 | 44 | 1181 | 99.61 |
| Google AI Studio | unknown | 1048576 | 0.5400 | 4.5000 | 44 | 413.5 | 99.66 |

### `google/gemini-3.6-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google | unknown | 1048576 | 0.3750 | 1.8750 | 52 | 9253 | 91.11 |
| Google AI Studio | unknown | 1048576 | 0.3750 | 1.8750 | 144 | 2228 | 99.95 |
| Google | unknown | 1048576 | 0.7500 | 3.7500 | 115 | 1681 | 99.68 |
| Google AI Studio | unknown | 1048576 | 0.7500 | 3.7500 | 52 | 1026 | 99.84 |
| Google | unknown | 1048576 | 0.8250 | 4.1250 | None | None | 100 |
| Google | unknown | 1048576 | 1.3500 | 6.7500 | 37 | 945 | 99.7 |
| Google AI Studio | unknown | 1048576 | 1.3500 | 6.7500 | 110.5 | 791.5 | 99.96 |

### `openai/gpt-4o-mini`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Azure | unknown | 128000 | 0.1500 | 0.6000 | 21 | 1382.5 | 99.76 |
| OpenAI | unknown | 128000 | 0.1500 | 0.6000 | 49 | 553.5 | 99.97 |
| Azure | unknown | 128000 | 0.1650 | 0.6600 | 78 | 1074.5 | 100 |

### `deepseek/deepseek-v4-flash-0731`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0500 | 0.1600 | 16 | 656 | 99.81 |
| AkashML | fp8 | 1048576 | 0.0650 | 0.1800 | 17 | 1341 | 95.49 |
| Relace | fp4 | 1048576 | 0.0650 | 0.1800 | 53 | 1109 | 98.37 |
| Sail Research | fp4 | 1048576 | 0.0650 | 0.1800 | 19 | 1714.5 | 99.73 |
| DeepInfra | fp8 | 1048576 | 0.0800 | 0.1800 | 26 | 795 | 99.36 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 33 | 567 | 99.59 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 58 | 943 | 96.84 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 95 | 1193 | 95.89 |
| Reka | fp4 | 262144 | 0.1100 | 0.6600 | 74 | 747 | 99.77 |
| Morph | bf16 | 1048576 | 0.1234 | 0.3475 | 47 | 1047 | 85.77 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 70 | 558.5 | 96.36 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 62 | 545 | 96.1 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 118 | 821 | 99.9 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 23 | 1402 | 99.04 |
| StreamLake | fp8 | 1024000 | 0.1320 | 0.3960 | 104 | 1437 | 99.17 |
| Baidu | fp8 | 1048576 | 0.1400 | 0.2800 | 108 | 1028 | 99.78 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 55 | 668 | 99.83 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 49 | 919 | 99.03 |
| Mancer 2 | fp8 | 1048576 | 0.1750 | 0.5000 | 26 | 801 | 97.72 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 38 | 1137 | 96.92 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 68 | 612 | 100.0 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 43 | 1194 | 92.56 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 58 | 1556 | 99.6 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 67 | 1398.5 | 99.94 |
| GMICloud | fp8 | 1048575 | 0.3520 | 1.0560 | 71 | 2799 | 87.11 |
| NextBit | fp8 | 1048576 | 0.4000 | 1.2000 | 54 | 2442.5 | 98.85 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 93 | 1285 | 99.94 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 49 | 1357 | 99.47 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 45 | 837 | 99.85 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 30 | 649 | 93.59 |

### `qwen/qwen3.8-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 52 | 2294.5 | 100.0 |

## Recomendação por necessidade

> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).

| Necessidade | Modelo recomendado | Melhor subprovedor |
|-------------|--------------------|--------------------|
| Título (title) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 92, $p 0.1800, 189.5 t/s, 473ms) |
| Compressão (compression) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 92, $p 0.1800, 189.5 t/s, 473ms) |
| Visão (vision) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 92, $p 0.1800, 189.5 t/s, 473ms) |
