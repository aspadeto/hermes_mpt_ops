# Levantamento OpenRouter — subprovedores e recomendação

Gerado: 2026-09-11 08:00 (automático, 2x/semana). Fonte: OpenRouter `/models/<slug>/endpoints` (métricas 30min).

## Modelo: `deepseek/deepseek-v4-flash-0731` — DEFAULT atual (agente)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0500 | 0.1600 | 18 | 1638 | 99.51 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 32 | 951 | 99.25 |
| Relace | fp4 | 1048576 | 0.0650 | 0.1800 | 60 | 820 | 99.53 |
| Sail Research | fp4 | 1048576 | 0.0650 | 0.3000 | 22 | 4648 | 99.77 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 17 | 1065.5 | 99.75 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 109 | 262 | 97.7 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 112 | 449 | 99.53 |
| Reka | fp4 | 262144 | 0.1100 | 0.6600 | 97 | 776 | 99.86 |
| StreamLake | fp8 | 1024000 | 0.1188 | 0.3564 | 37 | 1593.5 | 98.52 |
| Inceptron | fp4 | 1048576 | 0.1226 | 0.3305 | 17 | 950 | 99.86 |
| Morph | bf16 | 1048576 | 0.1234 | 0.3475 | 4 | 2125 | 99.96 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 30 | 5985.5 | 88.66 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 25 | 6032.5 | 88.24 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 89 | 488 | 99.97 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 33 | 1015 | 99.82 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 54 | 695 | 99.75 |
| Mancer 2 | fp8 | 1048576 | 0.1650 | 0.5000 | 35 | 824.5 | 98.55 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 34 | 1175 | 98.19 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 51 | 992 | 97.24 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 36 | 1718 | 99.31 |
| GMICloud | fp4 | 1048576 | 0.2860 | 0.8580 | 56 | 2709 | 99.38 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 62 | 1122 | 99.99 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 60 | 1758 | 99.82 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 84 | 1888 | 99.95 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 55 | 1530 | 99.39 |
| Baidu | fp8 | 1048576 | 0.4400 | 1.3200 | 138 | 863 | 99.98 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 50 | 735.5 | 99.96 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 35 | 771 | 98.83 |

## Modelo: `deepseek/deepseek-v4-pro-0813` — alternativa agente (qualidade/raciocínio)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| DeepSeek | unknown | 1048576 | 0.6600 | 1.9800 | 18 | 1216 | 99.99 |
| Ionstream | unknown | 1048576 | 0.6600 | 1.9800 | 42 | 1761 | 99.76 |
| Novita | fp8 | 1048576 | 0.9900 | 2.9700 | 49 | 1465 | 99.99 |
| StreamLake | unknown | 1024000 | 1.0494 | 3.1482 | 52 | 4815 | 99.82 |
| GMICloud | fp8 | 1048575 | 1.0560 | 3.1680 | 49 | 2815 | 99.77 |
| Alibaba | unknown | 1000000 | 1.1220 | 3.3660 | 56 | 1153 | 99.99 |
| NextBit | fp8 | 1048576 | 1.1220 | 3.3660 | 30 | 2985 | 99.74 |
| DeepInfra | fp8 | 1048576 | 1.3000 | 2.6000 | 17 | 8918 | 99.49 |
| CoreWeave | fp8 | 1048576 | 1.3100 | 3.9600 | 96 | 677 | 99.85 |
| Baidu | fp8 | 1048576 | 1.3200 | 3.9600 | 58 | 957 | 99.84 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 51 | 598 | 99.78 |
| BaseTen | fp4 | 1048576 | 1.3200 | 3.9600 | 35 | 498 | 99.64 |
| Cloudflare | unknown | 1048576 | 1.3200 | 3.9600 | 62 | 1086.5 | 99.64 |
| DigitalOcean | unknown | 1048576 | 1.3200 | 3.9600 | 31 | 686 | 99.3 |
| Fireworks | unknown | 1048576 | 1.3200 | 3.9600 | 62 | 1054 | 99.78 |
| Parasail | fp8 | 1048576 | 1.3200 | 3.9600 | 67 | 753 | 99.82 |
| Sail Research | fp4 | 1048576 | 1.3200 | 3.9600 | 78.5 | 1522 | 99.84 |
| SiliconFlow | fp8 | 1048576 | 1.3200 | 3.9600 | 37 | 1353 | 99.98 |
| Together | unknown | 1048576 | 1.3200 | 3.9600 | 93 | 783 | 99.35 |
| Phala | unknown | 1048576 | 1.4500 | 4.3600 | 48 | 1496 | 99.75 |

## Modelo: `qwen/qwen3.8-flash` — alternativa agente (barata)

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 46 | 1313.5 | 99.63 |
| Makora | fp4 | 262144 | 0.1500 | 0.4700 | 110 | 631 | 99.64 |

## Modelos auxiliares

### `google/gemini-2.5-flash-lite`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.0500 | 0.2000 | 158 | 554 | 99.98 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 75 | 520.5 | 99.83 |
| Google | unknown | 1048576 | 0.1000 | 0.4000 | 52 | 1078 | 99.26 |
| Google AI Studio | unknown | 1048576 | 0.1000 | 0.4000 | 132 | 598.5 | 97.43 |
| Google AI Studio | unknown | 1048576 | 0.1800 | 0.7200 | 75.5 | 476 | 98.99 |

### `google/gemini-2.5-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google AI Studio | unknown | 1048576 | 0.1500 | 1.2500 | 2 | 3700 | 100.0 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 95 | 619 | 99.42 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 67 | 793 | 99.61 |
| Google | unknown | 1048576 | 0.3000 | 2.5000 | 39 | 1830.5 | 84.34 |
| Google AI Studio | unknown | 1048576 | 0.3000 | 2.5000 | 45 | 499 | 99.9 |
| Google | unknown | 1048576 | 0.5400 | 4.5000 | 54 | 551 | 99.93 |
| Google AI Studio | unknown | 1048576 | 0.5400 | 4.5000 | 35 | 641 | 100 |

### `google/gemini-3.6-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Google | unknown | 1048576 | 0.3750 | 1.8750 | 46 | 7779 | 91.17 |
| Google AI Studio | unknown | 1048576 | 0.3750 | 1.8750 | 78 | 843 | 100.0 |
| Google | unknown | 1048576 | 0.7500 | 3.7500 | 136 | 1606 | 98.97 |
| Google AI Studio | unknown | 1048576 | 0.7500 | 3.7500 | 58 | 1064 | 99.85 |
| Google | unknown | 1048576 | 0.8250 | 4.1250 | None | None | 100 |
| Google | unknown | 1048576 | 1.3500 | 6.7500 | 104.5 | 1426.5 | 99.64 |
| Google AI Studio | unknown | 1048576 | 1.3500 | 6.7500 | 97 | 2282 | 99.42 |

### `openai/gpt-4o-mini`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Azure | unknown | 128000 | 0.1500 | 0.6000 | 17 | 1559 | 99.63 |
| OpenAI | unknown | 128000 | 0.1500 | 0.6000 | 45 | 537 | 99.96 |
| Azure | unknown | 128000 | 0.1650 | 0.6600 | 68 | 1047 | 99.95 |

### `deepseek/deepseek-v4-flash-0731`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| OpenInference | fp8 | 1048576 | 0.0500 | 0.1600 | 18 | 1638 | 99.51 |
| DeepInfra | fp8 | 1048576 | 0.0600 | 0.1800 | 32 | 951 | 99.25 |
| Relace | fp4 | 1048576 | 0.0650 | 0.1800 | 60 | 820 | 99.53 |
| Sail Research | fp4 | 1048576 | 0.0650 | 0.3000 | 22 | 4648 | 99.77 |
| DigitalOcean | unknown | 1048576 | 0.0800 | 0.2520 | 17 | 1065.5 | 99.75 |
| Makora | unknown | 1000000 | 0.0900 | 0.1950 | 109 | 262 | 97.7 |
| Wafer | unknown | 1048576 | 0.1000 | 0.2500 | 112 | 449 | 99.53 |
| Reka | fp4 | 262144 | 0.1100 | 0.6600 | 97 | 776 | 99.86 |
| StreamLake | fp8 | 1024000 | 0.1188 | 0.3564 | 37 | 1593.5 | 98.52 |
| Inceptron | fp4 | 1048576 | 0.1226 | 0.3305 | 17 | 950 | 99.86 |
| Morph | bf16 | 1048576 | 0.1234 | 0.3475 | 4 | 2125 | 99.96 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 30 | 5985.5 | 88.66 |
| BaseTen | fp8 | 1048576 | 0.1300 | 0.2600 | 25 | 6032.5 | 88.24 |
| CoreWeave | fp8 | 262144 | 0.1300 | 0.2800 | 89 | 488 | 99.97 |
| Parasail | fp8 | 1048576 | 0.1400 | 0.2800 | 33 | 1015 | 99.82 |
| Together | unknown | 1048576 | 0.1400 | 0.2800 | 54 | 695 | 99.75 |
| Mancer 2 | fp8 | 1048576 | 0.1650 | 0.5000 | 35 | 824.5 | 98.55 |
| Venice | unknown | 1000000 | 0.1750 | 0.3500 | 34 | 1175 | 98.19 |
| Fireworks | unknown | 1048576 | 0.2200 | 0.6600 | 51 | 992 | 97.24 |
| SiliconFlow | fp8 | 1048576 | 0.2200 | 0.6600 | 36 | 1718 | 99.31 |
| GMICloud | fp4 | 1048576 | 0.2860 | 0.8580 | 56 | 2709 | 99.38 |
| Alibaba | unknown | 1000000 | 0.3520 | 1.0560 | 62 | 1122 | 99.99 |
| NextBit | fp8 | 1048576 | 0.3520 | 1.0560 | 60 | 1758 | 99.82 |
| Novita | fp8 | 1048576 | 0.4092 | 1.2276 | 84 | 1888 | 99.95 |
| AtlasCloud | fp4 | 1048576 | 0.4400 | 1.3200 | 55 | 1530 | 99.39 |
| Baidu | fp8 | 1048576 | 0.4400 | 1.3200 | 138 | 863 | 99.98 |
| Cloudflare | unknown | 1310720 | 0.4400 | 1.3200 | 50 | 735.5 | 99.96 |
| Phala | unknown | 1048576 | 0.4400 | 1.3200 | 35 | 771 | 98.83 |

### `qwen/qwen3.8-flash`

| Provedor | Quant | Ctx | $prompt/M | $comp/M | thr50 t/s | lat50 ms | up 1d % |
|----------|-------|-----|-----------|----------|-----------|----------|---------|
| Alibaba | unknown | 1000000 | 0.1500 | 0.4700 | 46 | 1313.5 | 99.63 |
| Makora | fp4 | 262144 | 0.1500 | 0.4700 | 110 | 631 | 99.64 |

## Recomendação por necessidade

> Score = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local, maior melhor).

| Necessidade | Modelo recomendado | Melhor subprovedor |
|-------------|--------------------|--------------------|
| Título (title) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 92, $p 0.0500, 158 t/s, 554ms) |
| Compressão (compression) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 92, $p 0.0500, 158 t/s, 554ms) |
| Visão (vision) | `google/gemini-2.5-flash-lite` | Google AI Studio (visão) (score 92, $p 0.0500, 158 t/s, 554ms) |
