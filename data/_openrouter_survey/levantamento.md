# Levantamento OpenRouter — subprovedores e recomendação

Gerado: 2026-09-01 08:00 (automático, 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).

## Modelo: `deepseek/deepseek-v4-flash-0731` — DEFAULT atual (agente)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0500 | 0.1600 | 16 | 659 | 99.98 |
| AkashML | fp8 | 1048576 | 0.0650 | 0.1800 | 9 | 2751.5 | 95.82 |
| Relace | fp4 | 1048576 | 0.0650 | 0.1800 | 48 | 916.5 | 98.8 |
| Sail Research | fp4 | 1048576 | 0.0650 | 0.1800 | 19 | 1732 | 99.85 |
| Ambient | fp4 | 1048576 | 0.0800 | 0.1800 | 16 | 1563 | 91.84 |
| DeepInfra | fp8 | 1048576 | 0.0800 | 0.1800 | 28 | 715 | 99.32 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 10 | 893 | 99.42 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 49 | 795.5 | 97.04 |
| Morph | bf16 | 1048576 | 0.0987 | 0.2780 | 51 | 903 | 88.17 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 55 | 545 | 97.86 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 24 | 1721 | 99.91 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 14 | 2113 | 99.19 |
| Baidu | fp8 | 1048576 | 0.1400 | 0.2800 | 95 | 870 | 99.65 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 44 | 609 | 99.53 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 39 | 1084 | 99.11 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 39 | 962 | 97.46 |
| Mancer 2 | fp8 | 1048576 | 0.1850 | 0.5000 | 29 | 933 | 99.03 |
| Wafer | unknown | 1048576 | 0.2000 | 0.2500 | 65 | 1911 | 97.95 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 86 | 1053 | 99.98 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 39 | 823 | 97.27 |
| Reka | fp4 | 262144 | 0.2200 | 0.6600 | 24 | 2301 | 99.88 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 53 | 1326 | 99.76 |
| StreamLake | fp8 | 1024000 | 0.2200 | 0.6600 | 57 | 1592 | 99.46 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 39 | 1620 | 99.98 |
| GMICloud | fp8 | 1048575 | 0.3520 | 1.0560 | 56 | 2336 | 95.45 |
| NextBit | fp8 | 1048576 | 0.4000 | 1.2000 | 23 | 3200 | 98.24 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 61 | 1556 | 99.86 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 44 | 1668 | 99.85 |
| Novita | fp8 | 1048576 | 0.4400 | 1.3200 | 58 | 887 | 99.97 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 26 | 1526 | 97.6 |

## Modelo: `deepseek/deepseek-v4-pro-0813` — alternativa agente (qualidade/raciocínio)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| DeepSeek | unknown | 1048576 | 0.6600 | 1.9800 | 33 | 1346 | 99.99 |
| StreamLake | unknown | 1024000 | 1.1154 | 3.3462 | 51 | 3102 | 99.86 |
| Alibaba | unknown | 1000000 | 1.1220 | 3.3660 | 50 | 1044 | 99.94 |
| GMICloud | fp8 | 1048575 | 1.1220 | 3.3660 | 38 | 4112 | 98.04 |
| NextBit | fp8 | 1048576 | 1.1500 | 3.4000 | 52 | 3096.5 | 98.23 |
| DeepInfra | fp8 | 1048576 | 1.3000 | 2.6000 | 36 | 3397.5 | 93.41 |
| CoreWeave | fp8 | 1048576 | 1.3100 | 3.9600 | 97 | 803 | 99.59 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 71 | 472 | 99.37 |
| Cloudflare | unknown | 1048576 | 1.3200 | 3.9600 | 43 | 2066 | 99.85 |
| DigitalOcean | unknown | 1048576 | 1.3200 | 3.9600 | 42 | 1403 | 99.84 |
| Fireworks | unknown | 1048576 | 1.3200 | 3.9600 | 65 | 1042 | 99.87 |
| Novita | fp8 | 1048576 | 1.3200 | 3.9600 | 43 | 1336 | 99.98 |
| Parasail | fp8 | 1048576 | 1.3200 | 3.9600 | 47 | 642 | 99.55 |
| Sail Research | fp4 | 1048576 | 1.3200 | 3.9600 | 86 | 858 | 99.84 |
| SiliconFlow | fp8 | 1048576 | 1.3200 | 3.9600 | 47 | 1230 | 99.98 |
| Together | unknown | 1048576 | 1.3200 | 3.9600 | 54 | 1063 | 96.56 |
| Phala | unknown | 1048576 | 1.4500 | 4.3600 | 41 | 1299.5 | 99.98 |

## Modelo: `qwen/qwen3.8-flash` — alternativa agente (barata)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 45 | 1226.5 | 99.99 |

## Modelos auxiliares

### `google/gemini-2.5-flash-lite`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.0500 | 0.2000 | 81 | 638 | 100.0 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 86 | 438 | 99.93 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 81 | 1200 | 98.55 |
| Google AI Studio | unknown | 1048576 | 0.1000 | 0.4000 | 147 | 618 | 98.54 |
| Google AI Studio | unknown | 1048576 | 0.1800 | 0.7200 | 39 | 583 | 99.8 |

### `google/gemini-2.5-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.1500 | 1.2500 | 4 | 2368 | 100 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 55 | 849 | 99.64 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 83 | 610 | 98.99 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 53 | 1185 | 93.71 |
| Google AI Studio | unknown | 1048576 | 0.3000 | 2.5000 | 44 | 465 | 99.95 |
| Google | unknown | 1048576 | 0.5400 | 4.5000 | 42 | 1251 | 99.74 |
| Google AI Studio | unknown | 1048576 | 0.5400 | 4.5000 | 114.5 | 3481 | 98.92 |

### `google/gemini-3.6-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google | unknown | 1048576 | 0.3750 | 1.8750 | 140.5 | 7553.5 | 100 |
| Google AI Studio | unknown | 1048576 | 0.3750 | 1.8750 | 110 | 1990.5 | 99.95 |
| Google | unknown | 1048576 | 0.7500 | 3.7500 | 131.5 | 1626.5 | 99.74 |
| Google AI Studio | unknown | 1048576 | 0.7500 | 3.7500 | 130 | 2191.5 | 99.59 |
| Google | unknown | 1048576 | 0.8250 | 4.1250 | None | None | 100 |
| Google | unknown | 1048576 | 1.3500 | 6.7500 | 11.5 | 1876 | 99.96 |
| Google AI Studio | unknown | 1048576 | 1.3500 | 6.7500 | 9.5 | 1321.5 | 99.9 |

### `openai/gpt-4o-mini`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Azure | unknown | 128000 | 0.1500 | 0.6000 | 20 | 1579 | 99.72 |
| OpenAI | unknown | 128000 | 0.1500 | 0.6000 | 46 | 542 | 99.96 |
| Azure | unknown | 128000 | 0.1650 | 0.6600 | 48 | 1230 | 99.84 |

### `deepseek/deepseek-v4-flash-0731`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0500 | 0.1600 | 16 | 659 | 99.98 |
| AkashML | fp8 | 1048576 | 0.0650 | 0.1800 | 9 | 2751.5 | 95.82 |
| Relace | fp4 | 1048576 | 0.0650 | 0.1800 | 48 | 916.5 | 98.8 |
| Sail Research | fp4 | 1048576 | 0.0650 | 0.1800 | 19 | 1732 | 99.85 |
| Ambient | fp4 | 1048576 | 0.0800 | 0.1800 | 16 | 1563 | 91.84 |
| DeepInfra | fp8 | 1048576 | 0.0800 | 0.1800 | 28 | 715 | 99.32 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 10 | 893 | 99.42 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 49 | 795.5 | 97.04 |
| Morph | bf16 | 1048576 | 0.0987 | 0.2780 | 51 | 903 | 88.17 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 55 | 545 | 97.86 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 24 | 1721 | 99.91 |
| Inceptron | fp4 | 1048576 | 0.1300 | 0.2800 | 14 | 2113 | 99.19 |
| Baidu | fp8 | 1048576 | 0.1400 | 0.2800 | 95 | 870 | 99.65 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 44 | 609 | 99.53 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 39 | 1084 | 99.11 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 39 | 962 | 97.46 |
| Mancer 2 | fp8 | 1048576 | 0.1850 | 0.5000 | 29 | 933 | 99.03 |
| Wafer | unknown | 1048576 | 0.2000 | 0.2500 | 65 | 1911 | 97.95 |
| DeepSeek | unknown | 1048576 | 0.2200 | 0.6600 | 86 | 1053 | 99.98 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 39 | 823 | 97.27 |
| Reka | fp4 | 262144 | 0.2200 | 0.6600 | 24 | 2301 | 99.88 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 53 | 1326 | 99.76 |
| StreamLake | fp8 | 1024000 | 0.2200 | 0.6600 | 57 | 1592 | 99.46 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 39 | 1620 | 99.98 |
| GMICloud | fp8 | 1048575 | 0.3520 | 1.0560 | 56 | 2336 | 95.45 |
| NextBit | fp8 | 1048576 | 0.4000 | 1.2000 | 23 | 3200 | 98.24 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 61 | 1556 | 99.86 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 44 | 1668 | 99.85 |
| Novita | fp8 | 1048576 | 0.4400 | 1.3200 | 58 | 887 | 99.97 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 26 | 1526 | 97.6 |

### `qwen/qwen3.8-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 45 | 1226.5 | 99.99 |

## Recomendação por necessidade

> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).

| Necessidade | Modelo recomendado | Melhor subprovedor |
|-------------|--------------------|--------------------|
| Título (title) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 90, $p 0.1000, 147 t/s, 618ms) |
| Compressão (compression) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 90, $p 0.1000, 147 t/s, 618ms) |
| Visão (vision) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 90, $p 0.1000, 147 t/s, 618ms) |
