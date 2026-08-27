# Otimização de roteamento OpenRouter — levantamento de subprovedores

Data: 2026-08-27 · Fonte: OpenRouter `/api/v1/models/<slug>/endpoints` (métricas 30min)

## Modelo default atual: `deepseek/deepseek-v4-flash-0731`

| # | Provedor | Quant | Ctx | \$prompt/M | \$comp/M | thr50 t/s | lat50 ms | up 1d % | score |
|---|----------|-------|-----|-----------|----------|-----------|----------|---------|-------|
| 1 | Reka | fp4 | 262144 | 0.220 | 0.660 | 152 | 506 | 98.23 | 91.8 |
| 2 | CoreWeave | fp8 | 262144 | 0.130 | 0.280 | 117 | 403 | 99.97 | 87.5 |
| 3 | Baidu | fp8 | 1048576 | 0.060 | 0.120 | 124 | 741 | 99.92 | 85.1 |
| 4 | Makora | unknown | 1000000 | 0.090 | 0.195 | 101 | 514 | 92.6 | 82.0 |
| 5 | Wafer | unknown | 1048576 | 0.280 | 0.560 | 135 | 1165 | 99.19 | 80.7 |
| 6 | Inceptron | fp4 | 1048576 | 0.130 | 0.280 | 66 | 592.5 | 99.72 | 74.9 |
| 7 | Cloudflare | unknown | 1310720 | 0.440 | 1.320 | 86 | 842 | 99.97 | 74.0 |
| 8 | Ambient | fp4 | 1048576 | 0.080 | 0.180 | 52 | 521 | 99.05 | 73.1 |
| 9 | Relace | fp4 | 1048576 | 0.050 | 0.100 | 66 | 933 | 99.81 | 71.1 |
| 10 | DeepSeek | unknown | 1048576 | 0.220 | 0.660 | 81 | 1102 | 99.99 | 70.8 |
| 11 | DeepInfra | fp8 | 1048576 | 0.080 | 0.180 | 41 | 552.5 | 98.56 | 70.5 |
| 12 | Together | unknown | 1048576 | 0.140 | 0.280 | 46 | 670 | 99.6 | 69.9 |

## Alternativa: `deepseek/deepseek-v4-pro-0813`

| # | Provedor | Quant | Ctx | \$prompt/M | \$comp/M | thr50 t/s | lat50 ms | up 1d % | score |
|---|----------|-------|-----|-----------|----------|-----------|----------|---------|-------|
| 1 | BaseTen | fp4 | 1048576 | 1.320 | 3.960 | 89.5 | 567.5 | 99.59 | 76.0 |
| 2 | Parasail | fp8 | 1048576 | 1.320 | 3.960 | 64 | 738 | 98.45 | 68.6 |
| 3 | SiliconFlow | fp8 | 1048576 | 1.320 | 3.960 | 49 | 1105 | 99.77 | 61.2 |
| 4 | DigitalOcean | unknown | 1048576 | 1.320 | 3.960 | 39 | 956 | 99.3 | 61.0 |
| 5 | Fireworks | unknown | 1048576 | 1.320 | 3.960 | 66 | 1415 | 99.91 | 60.7 |
| 6 | Alibaba | unknown | 1000000 | 0.581 | 1.742 | 50 | 1424 | 99.96 | 59.1 |
| 7 | Novita | fp8 | 1048576 | 1.320 | 3.960 | 46 | 1310 | 98.17 | 57.8 |
| 8 | DeepSeek | unknown | 1048576 | 0.660 | 1.980 | 36 | 1348 | 100.0 | 57.0 |
| 9 | Phala | unknown | 1048576 | 1.450 | 4.360 | 59 | 1685.5 | 97.36 | 55.3 |
| 10 | StreamLake | unknown | 1024000 | 0.660 | 1.980 | 47.5 | 3968.5 | 99.85 | 51.1 |
| 11 | GMICloud | fp8 | 1048575 | 1.122 | 3.366 | 49 | 4254 | 99.08 | 50.2 |
| 12 | Cloudflare | unknown | 1048576 | 1.320 | 3.960 | 39 | 3204 | 99.72 | 48.0 |

## Auxiliar: `google/gemini-2.5-flash`

| # | Provedor | Quant | Ctx | \$prompt/M | \$comp/M | thr50 t/s | lat50 ms | up 1d % | score |
|---|----------|-------|-----|-----------|----------|-----------|----------|---------|-------|
| 1 | Google AI Studio | unknown | 1048576 | 0.300 | 2.500 | 90 | 750 | 99.97 | 75.1 |
| 2 | Google | unknown | 1048576 | 0.300 | 2.500 | 81 | 632 | 98.41 | 74.6 |
| 3 | Google AI Studio | unknown | 1048576 | 0.540 | 4.500 | 50.5 | 370 | 99.97 | 70.8 |
| 4 | Google | unknown | 1048576 | 0.300 | 2.500 | 62 | 924 | 99.59 | 67.3 |
| 5 | Google | unknown | 1048576 | 0.540 | 4.500 | 42 | 1293 | 99.59 | 57.5 |
| 6 | Google | unknown | 1048576 | 0.300 | 2.500 | 63 | 1529 | 66.62 | 55.0 |
| 7 | Google AI Studio | unknown | 1048576 | 0.150 | 1.250 | 3 | 2326 | 99.97 | 43.3 |

## Notas
- **score** = 30% custo + 30% throughput + 25% latência + 15% uptime (heurística local p/ ranquear)
- **quantização**: fp8/fp4 = menor precisão/menor custo; bf16 = alta precisão; unknown = não divulgado
- Métricas de throughput/latência são p50 de 30min; podem variar com carga
- `provider_routing` no Hermes mapeia para o objeto `provider` do OpenRouter (sort/only/ignore/order/data_collection)

Arquivo bruto: `data/_openrouter_survey/endpoints.json`