# Levantamento OpenRouter — subprovedores e recomendação

Gerado: 2026-08-28 08:00 (automático, 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).

## Modelo: `deepseek/deepseek-v4-flash-0731` — DEFAULT atual (agente)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp4 | 1048576 | 0.0300 | 0.1000 | 9 | 661 | 99.99 |
| Relace | fp4 | 1048576 | 0.0700 | 0.1400 | 73 | 977 | 99.83 |
| Ambient | fp4 | 1048576 | 0.0800 | 0.1800 | 66 | 937 | 98.76 |
| DeepInfra | fp8 | 1048576 | 0.0800 | 0.1800 | 46 | 634 | 99.0 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 51 | 1027 | 95.28 |
| Morph | bf16 | 1048576 | 0.0987 | 0.2780 | 13 | 1445 | 98.28 |
| AkashML | fp8 | 1048576 | 0.1000 | 0.2800 | 29 | 1223 | 99.61 |
| GMICloud | fp8 | 1048575 | 0.1120 | 0.2240 | 54 | 1954 | 95.7 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 58 | 508 | 95.6 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 127 | 737.5 | 99.97 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 62 | 652 | 99.66 |
| Baidu | fp8 | 1048576 | 0.1400 | 0.2800 | 107 | 856 | 99.9 |
| DigitalOcean | unknown | 1048576 | 0.1400 | 0.2800 | 30 | 536 | 99.71 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 35 | 730 | 97.77 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 56 | 636 | 99.7 |
| Mancer 2 | fp8 | 1048576 | 0.1600 | 0.4500 | 24 | 874.5 | 98.04 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 44 | 1094 | 97.93 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 81 | 1069 | 99.97 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 48 | 672 | 98.55 |
| Phala | unknown | 1048576 | 0.2200 | 0.6600 | 47 | 662 | 96.62 |
| Reka | fp4 | 262144 | 0.2200 | 0.6600 | 167 | 482 | 96.78 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 59 | 1438.5 | 99.73 |
| StreamLake | fp8 | 1024000 | 0.2200 | 0.6600 | 55 | 1102 | 99.87 |
| Wafer | unknown | 1048576 | 0.2800 | 0.5600 | 107 | 1606 | 96.57 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 89 | 1136 | 99.99 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 42 | 1978 | 99.77 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 100 | 788 | 99.96 |
| NextBit | fp8 | 1048576 | 0.4400 | 1.3200 | 45.5 | 2568.5 | 99.17 |
| Novita | fp8 | 1048576 | 0.4400 | 1.3200 | 73 | 1599 | 99.9 |

## Modelo: `deepseek/deepseek-v4-pro-0813` — alternativa agente (qualidade/raciocínio)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| DeepSeek | unknown | 1048576 | 0.6600 | 1.9800 | 39 | 1395 | 100.0 |
| StreamLake | unknown | 1024000 | 1.1154 | 3.3462 | 44 | 3768 | 99.93 |
| Alibaba | unknown | 1000000 | 1.1220 | 3.3660 | 48 | 1272.5 | 99.97 |
| GMICloud | fp8 | 1048575 | 1.1220 | 3.3660 | 34 | 4650.5 | 98.69 |
| DeepInfra | fp8 | 1048576 | 1.3000 | 2.6000 | 31 | 1955 | 90.96 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 111 | 911 | 99.66 |
| Cloudflare | unknown | 1048576 | 1.3200 | 3.9600 | 35 | 3520.5 | 99.83 |
| DigitalOcean | unknown | 1048576 | 1.3200 | 3.9600 | 38 | 1383 | 99.21 |
| Fireworks | unknown | 1048576 | 1.3200 | 3.9600 | 67 | 1551 | 99.86 |
| Novita | fp8 | 1048576 | 1.3200 | 3.9600 | 58 | 1178 | 99.83 |
| Parasail | fp8 | 1048576 | 1.3200 | 3.9600 | 45 | 983 | 98.63 |
| SiliconFlow | fp8 | 1048576 | 1.3200 | 3.9600 | 45 | 1336 | 99.94 |
| Together | unknown | 1048576 | 1.3200 | 3.9600 | 25 | 7137 | 94.98 |
| Phala | unknown | 1048576 | 1.4500 | 4.3600 | 31 | 1942 | 99.84 |

## Modelo: `qwen/qwen3.8-flash` — alternativa agente (barata)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 37 | 3849 | 99.98 |

## Modelos auxiliares

### `google/gemini-2.5-flash-lite`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.0500 | 0.2000 | 73 | 660.5 | 99.68 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 87 | 441 | 99.75 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 74 | 520 | 99.61 |
| Google AI Studio | unknown | 1048576 | 0.1000 | 0.4000 | 174 | 587 | 99.68 |
| Google AI Studio | unknown | 1048576 | 0.1800 | 0.7200 | None | None | 99.68 |

### `google/gemini-2.5-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.1500 | 1.2500 | 2 | 3771.5 | 99.94 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 73 | 718.5 | 99.66 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 75 | 809 | 98.6 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 80 | 2136 | 66.56 |
| Google AI Studio | unknown | 1048576 | 0.3000 | 2.5000 | 117 | 688 | 99.94 |
| Google | unknown | 1048576 | 0.5400 | 4.5000 | 41 | 1273 | 99.66 |
| Google AI Studio | unknown | 1048576 | 0.5400 | 4.5000 | 70 | 372 | 99.94 |

### `google/gemini-3.6-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google | unknown | 1048576 | 0.3750 | 1.8750 | None | None | 99.63 |
| Google AI Studio | unknown | 1048576 | 0.3750 | 1.8750 | 104.5 | 3295.5 | 99.14 |
| Google | unknown | 1048576 | 0.7500 | 3.7500 | 126 | 1790 | 99.63 |
| Google AI Studio | unknown | 1048576 | 0.7500 | 3.7500 | 122 | 1777.5 | 99.14 |
| Google | unknown | 1048576 | 0.8250 | 4.1250 | None | None | 100 |
| Google | unknown | 1048576 | 1.3500 | 6.7500 | 93 | 1043 | 99.63 |
| Google AI Studio | unknown | 1048576 | 1.3500 | 6.7500 | 42 | 1531 | 99.14 |

### `openai/gpt-4o-mini`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Azure | unknown | 128000 | 0.1500 | 0.6000 | 29 | 1338 | 99.89 |
| OpenAI | unknown | 128000 | 0.1500 | 0.6000 | 54 | 502 | 99.97 |
| Azure | unknown | 128000 | 0.1650 | 0.6600 | None | None | 100 |

### `deepseek/deepseek-v4-flash-0731`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp4 | 1048576 | 0.0300 | 0.1000 | 9 | 661 | 99.99 |
| Relace | fp4 | 1048576 | 0.0700 | 0.1400 | 73 | 977 | 99.83 |
| Ambient | fp4 | 1048576 | 0.0800 | 0.1800 | 66 | 937 | 98.76 |
| DeepInfra | fp8 | 1048576 | 0.0800 | 0.1800 | 46 | 634 | 99.0 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 51 | 1027 | 95.28 |
| Morph | bf16 | 1048576 | 0.0987 | 0.2780 | 13 | 1445 | 98.28 |
| AkashML | fp8 | 1048576 | 0.1000 | 0.2800 | 29 | 1223 | 99.61 |
| GMICloud | fp8 | 1048575 | 0.1120 | 0.2240 | 54 | 1954 | 95.7 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 58 | 508 | 95.6 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 127 | 737.5 | 99.97 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 62 | 652 | 99.66 |
| Baidu | fp8 | 1048576 | 0.1400 | 0.2800 | 107 | 856 | 99.9 |
| DigitalOcean | unknown | 1048576 | 0.1400 | 0.2800 | 30 | 536 | 99.71 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 35 | 730 | 97.77 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 56 | 636 | 99.7 |
| Mancer 2 | fp8 | 1048576 | 0.1600 | 0.4500 | 24 | 874.5 | 98.04 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 44 | 1094 | 97.93 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 81 | 1069 | 99.97 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 48 | 672 | 98.55 |
| Phala | unknown | 1048576 | 0.2200 | 0.6600 | 47 | 662 | 96.62 |
| Reka | fp4 | 262144 | 0.2200 | 0.6600 | 167 | 482 | 96.78 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 59 | 1438.5 | 99.73 |
| StreamLake | fp8 | 1024000 | 0.2200 | 0.6600 | 55 | 1102 | 99.87 |
| Wafer | unknown | 1048576 | 0.2800 | 0.5600 | 107 | 1606 | 96.57 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 89 | 1136 | 99.99 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 42 | 1978 | 99.77 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 100 | 788 | 99.96 |
| NextBit | fp8 | 1048576 | 0.4400 | 1.3200 | 45.5 | 2568.5 | 99.17 |
| Novita | fp8 | 1048576 | 0.4400 | 1.3200 | 73 | 1599 | 99.9 |

### `qwen/qwen3.8-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 37 | 3849 | 99.98 |

## Recomendação por necessidade

> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).

| Necessidade | Modelo recomendado | Melhor subprovedor |
|-------------|--------------------|--------------------|
| Título (title) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 92, $p 0.1000, 174 t/s, 587ms) |
| Compressão (compression) | `deepseek/deepseek-v4-flash-0731` | Reka (score 92, $p 0.2200, 167 t/s, 482ms) |
| Visão (vision) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 92, $p 0.1000, 174 t/s, 587ms) |
