# Levantamento OpenRouter — subprovedores e recomendação

Gerado: 2026-09-25 08:00 (automático, 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).

## Modelo: `deepseek/deepseek-v4-flash-0731` — DEFAULT atual (agente)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0300 | 0.4000 | 18 | 1863.5 | 99.1 |
| Relace | fp4 | 1048576 | 0.0300 | 0.3200 | 33 | 800.5 | 99.79 |
| Sail Research | fp4 | 1048576 | 0.0300 | 0.5500 | 30 | 1493 | 99.33 |
| Sail Research | fp4 | 1048576 | 0.0300 | 0.5500 | 37.5 | 1074 | 99.23 |
| StreamLake | fp8 | 1024000 | 0.0528 | 0.1584 | 47 | 1241 | 99.78 |
| Baidu | fp8 | 1048576 | 0.0598 | 0.1795 | 128 | 728 | 99.9 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 57 | 631 | 99.91 |
| Wafer | unknown | 1048576 | 0.0800 | 0.3500 | 99 | 500 | 99.99 |
| Inceptron | fp4 | 1048576 | 0.0828 | 0.4830 | 82 | 520 | 99.9 |
| Reka | unknown | 262144 | 0.0880 | 0.5280 | 114 | 547 | 99.87 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 84 | 421 | 98.91 |
| DigitalOcean | unknown | 1048576 | 0.1190 | 0.2380 | 49 | 530 | 99.98 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 154 | 418 | 99.97 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 108 | 387 | 99.97 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 121 | 516 | 99.86 |
| Cohere | unknown | 1048576 | 0.1400 | 0.2800 | 126 | 229 | 98.93 |
| Nebius | fp8 | 1024000 | 0.1400 | 0.2800 | 41 | 1345.5 | 91.17 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 67 | 649 | 99.68 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 43 | 785 | 97.98 |
| Morph | unknown | 1048576 | 0.1420 | 0.3996 | 22 | 1246.5 | 99.54 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 64 | 851 | 99.72 |
| Mancer 2 | fp8 | 1048576 | 0.2000 | 0.6000 | 70 | 812 | 99.45 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 81 | 730 | 98.71 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 38 | 1447 | 99.54 |
| GMICloud | fp8 | 1048575 | 0.2860 | 0.8580 | 50 | 1804 | 99.77 |
| Phala | unknown | 1048576 | 0.3080 | 0.9240 | 44 | 2310 | 98.77 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 38 | 911 | 99.78 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 58 | 2160.5 | 99.98 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 95 | 1306 | 100.0 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 67 | 1015 | 97.23 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 60 | 584 | 99.99 |

## Modelo: `deepseek/deepseek-v4-pro-0813` — alternativa agente (qualidade/raciocínio)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Ionstream | unknown | 1048576 | 0.2528 | 2.8800 | 51 | 996.5 | 99.34 |
| Baidu | fp8 | 1048576 | 0.3498 | 1.0494 | 46 | 1760.5 | 99.99 |
| Wafer | unknown | 1048576 | 0.3500 | 3.5000 | 114 | 823 | 99.45 |
| Sail Research | fp4 | 1048576 | 0.4000 | 4.3000 | 4 | 1738.5 | 99.89 |
| Sail Research | fp4 | 1048576 | 0.4000 | 4.3000 | 16 | 2198.5 | 99.71 |
| StreamLake | unknown | 1024000 | 0.4620 | 1.3860 | 43 | 1797.5 | 99.72 |
| DeepSeek | unknown | 1048576 | 0.6600 | 1.9800 | 48 | 1477 | 99.96 |
| Phala | unknown | 1048576 | 0.9570 | 2.8776 | 54.5 | 3020.5 | 99.03 |
| Novita | fp8 | 1048576 | 0.9900 | 2.9700 | 63 | 1881 | 99.98 |
| GMICloud | fp8 | 1048575 | 1.0560 | 3.1680 | 53 | 3701.5 | 99.8 |
| NextBit | fp8 | 1048576 | 1.0560 | 3.1680 | 39 | 2608 | 99.98 |
| Alibaba | unknown | 1000000 | 1.1220 | 3.3660 | 54 | 1302 | 99.32 |
| DeepInfra | fp8 | 1048576 | 1.3000 | 2.6000 | 59 | 1010 | 99.8 |
| CoreWeave | fp8 | 1048576 | 1.3100 | 3.9600 | 115 | 694 | 99.76 |
| AtlasCloud | fp8 | 1048576 | 1.3200 | 3.9600 | 45.5 | 1337.5 | 99.22 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 96.5 | 653.5 | 99.32 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 101 | 613 | 99.2 |
| Cloudflare | unknown | 1048576 | 1.3200 | 3.9600 | 24 | 3144 | 98.43 |
| DigitalOcean | unknown | 1048576 | 1.3200 | 3.9600 | 47 | 1237 | 97.34 |
| Fireworks | unknown | 1048576 | 1.3200 | 3.9600 | 59 | 1453 | 99.59 |
| Parasail | fp8 | 1048576 | 1.3200 | 3.9600 | 61 | 723 | 99.73 |
| SiliconFlow | fp8 | 1048576 | 1.3200 | 3.9600 | 54 | 1593 | 99.15 |
| Together | unknown | 1048576 | 1.3200 | 3.9600 | 65 | 2488 | 98.25 |
| Venice | unknown | 1000000 | 1.6500 | 4.9500 | 71 | 1222 | 99.17 |

## Modelo: `qwen/qwen3.8-flash` — alternativa agente (barata)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 57 | 2098 | 99.9 |

## Modelos auxiliares

### `google/gemini-2.5-flash-lite`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.0500 | 0.2000 | 109 | 634 | 99.99 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 89 | 489.5 | 99.86 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 63 | 1030 | 98.83 |
| Google AI Studio | unknown | 1048576 | 0.1000 | 0.4000 | 80 | 522 | 99.97 |
| Google AI Studio | unknown | 1048576 | 0.1800 | 0.7200 | 330 | 1237 | 100 |

### `google/gemini-2.5-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.1500 | 1.2500 | 224 | 453 | 100.0 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 86 | 616 | 99.56 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 65 | 748 | 99.55 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 75 | 1283 | 88.63 |
| Google AI Studio | unknown | 1048576 | 0.3000 | 2.5000 | 62 | 492 | 99.97 |
| Google | unknown | 1048576 | 0.5400 | 4.5000 | 43 | 674 | 99.98 |
| Google AI Studio | unknown | 1048576 | 0.5400 | 4.5000 | None | None | None |

### `google/gemini-3.6-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google | unknown | 1048576 | 0.3750 | 1.8750 | 52 | 8994 | 99.63 |
| Google AI Studio | unknown | 1048576 | 0.3750 | 1.8750 | 118 | 1631 | 100 |
| Google | unknown | 1048576 | 0.7500 | 3.7500 | 138 | 1488 | 99.83 |
| Google AI Studio | unknown | 1048576 | 0.7500 | 3.7500 | 41 | 1163 | 99.88 |
| Google | unknown | 1048576 | 0.8250 | 4.1250 | 115.5 | 1296 | 100 |
| Google | unknown | 1048576 | 1.3500 | 6.7500 | 173 | 2425 | 97.64 |
| Google AI Studio | unknown | 1048576 | 1.3500 | 6.7500 | 177 | 1742 | 99.92 |

### `openai/gpt-4o-mini`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Azure | unknown | 128000 | 0.1500 | 0.6000 | 35 | 1395 | 99.96 |
| OpenAI | unknown | 128000 | 0.1500 | 0.6000 | 53 | 646.5 | 99.82 |
| Azure | unknown | 128000 | 0.1650 | 0.6600 | 77 | 929.5 | 100 |

### `deepseek/deepseek-v4-flash-0731`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0300 | 0.4000 | 18 | 1863.5 | 99.1 |
| Relace | fp4 | 1048576 | 0.0300 | 0.3200 | 33 | 800.5 | 99.79 |
| Sail Research | fp4 | 1048576 | 0.0300 | 0.5500 | 30 | 1493 | 99.33 |
| Sail Research | fp4 | 1048576 | 0.0300 | 0.5500 | 37.5 | 1074 | 99.23 |
| StreamLake | fp8 | 1024000 | 0.0528 | 0.1584 | 47 | 1241 | 99.78 |
| Baidu | fp8 | 1048576 | 0.0598 | 0.1795 | 128 | 728 | 99.9 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 57 | 631 | 99.91 |
| Wafer | unknown | 1048576 | 0.0800 | 0.3500 | 99 | 500 | 99.99 |
| Inceptron | fp4 | 1048576 | 0.0828 | 0.4830 | 82 | 520 | 99.9 |
| Reka | unknown | 262144 | 0.0880 | 0.5280 | 114 | 547 | 99.87 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 84 | 421 | 98.91 |
| DigitalOcean | unknown | 1048576 | 0.1190 | 0.2380 | 49 | 530 | 99.98 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 154 | 418 | 99.97 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 108 | 387 | 99.97 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 121 | 516 | 99.86 |
| Cohere | unknown | 1048576 | 0.1400 | 0.2800 | 126 | 229 | 98.93 |
| Nebius | fp8 | 1024000 | 0.1400 | 0.2800 | 41 | 1345.5 | 91.17 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 67 | 649 | 99.68 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 43 | 785 | 97.98 |
| Morph | unknown | 1048576 | 0.1420 | 0.3996 | 22 | 1246.5 | 99.54 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 64 | 851 | 99.72 |
| Mancer 2 | fp8 | 1048576 | 0.2000 | 0.6000 | 70 | 812 | 99.45 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 81 | 730 | 98.71 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 38 | 1447 | 99.54 |
| GMICloud | fp8 | 1048575 | 0.2860 | 0.8580 | 50 | 1804 | 99.77 |
| Phala | unknown | 1048576 | 0.3080 | 0.9240 | 44 | 2310 | 98.77 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 38 | 911 | 99.78 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 58 | 2160.5 | 99.98 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 95 | 1306 | 100.0 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 67 | 1015 | 97.23 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 60 | 584 | 99.99 |

### `qwen/qwen3.8-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 57 | 2098 | 99.9 |

## Recomendação por necessidade

> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).

| Necessidade | Modelo recomendado | Melhor subprovedor |
|-------------|--------------------|--------------------|
| Título (title) | `google/gemini-2.5-flash` | Google AI Studio (visão) (score 92, $p 0.1500, 224 t/s, 453ms) |
| Compressão (compression) | `deepseek/deepseek-v4-flash-0731` | BaseTen (score 94, $p 0.1300, 154 t/s, 418ms) |
| Visão (vision) | `google/gemini-2.5-flash` | Google AI Studio (visão) (score 92, $p 0.1500, 224 t/s, 453ms) |
