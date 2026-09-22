---
name: pesquisa-boletins-inteligente
description: "Pesquisa híbrida em boletins MPT (índice + full-text)."
version: 1.0.0
author: HAL 9000
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [pesquisa, boletins, mpt, indice, full-text]
    category: produtividade
---

# Pesquisa Inteligente em Boletins do MPT

Estratégia híbrida:
- **Índice** (CSV/TSV/TOML/MD): fatos diretos (número, tipo, data, órgão)
- **Full-text** (MDs planos): contexto/ementa

Classificador rule-based em `pesquisar_boletins.py`.