---
name: catalogar-atos-boletins
description: "Catalogar atos normativos de Boletins do MPT em SQLite."
version: 1.0.0
author: HAL 9000
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [boletim, mpt, sqlite, catalogo, atos-normativos]
    category: analise
    related_skills: [boletim-servico-mpt, analise-pgea]
---

# Catálogo de Atos Normativos de Boletins de Serviço (SQLite)

Constrói e mantém um **catálogo indexado dos atos publicados nos Boletins de
Serviço do MPT** num banco SQLite, com destaque para os **atos normativos que
regulamentam o funcionamento de processos administrativos**. O objetivo final:
ao analisar um processo (PGEA/IAD/etc.), localizar os atos normativos
relacionados ao assunto — abrindo o `.md` do boletim ou re-baixando o PDF.

## Quando Ativar

- Usuário pedir para "catalogar", "indexar" ou "dar destaque" aos atos de
  Boletins de Serviço do MPT
- Usuário pedir para montar um banco/índice de regulamentos de processos
  administrativos a partir dos boletins
- Mencionar pesquisa futura de "quais atos normativos regulam X assunto"

> Este pipeline assume que os PDFs já foram baixados e extraídos (skills
> `boletim-servico-mpt` + `audit_boletim.py`). Aqui o foco é o catálogo.

## Organização de arquivos

Os boletins vivem em pastas **`YYYY-MM-DD`** (data de circulação), cada uma com
PDF + `.md` extraído + `auditoria_*.md`. Raiz: `/opt/data/hermes-data/boletins/`.
O nome `YYYY-MM-DD` permite ordenação/visualização cronológica.

## Banco SQLite

`/opt/data/hermes-data/hermes_mpt_ops/data/atos.db` (versionado no git):

```
boletins(id, data "2024-11-06", numero "212/2024", pdf, md)
atos_normativos(id, boletim_id→, tipo, numero, ano, orgao, data_ato,
                pagina, secao, ementa, relevante, observacao)
```

- `relevante=1` = regulamenta funcionamento de processos administrativos.
- `atos.db` é versionado explicitamente (exceção no `.gitignore`, como
  `pendencias.db`/`processos.db`).

## Fluxo

```bash
# 1. baixar o mês (cloudscraper, da skill boletim-servico-mpt)
.venv-bol/bin/python scripts/baixar_boletim.py 2026 AUG --baixar todos --dir <pasta-dia>
# 2. extrair/auditar cada PDF → .md (na pasta do dia)
.venv-bol/bin/python scripts/audit_boletim.py <dia>/BS-XXX.pdf --saida <dia>
# 3. catalogar tudo no SQLite (raiz = dir com pastas YYYY-MM-DD)
.venv-bol/bin/python scripts/catalogar_atos.py --raiz boletins --db data/atos.db --recriar
```

Scripts canônicos em `hermes_mpt_ops/scripts/` (repo OPS — fonte da verdade).

## Curadoria persistente (IMPORTANTE)

O campo `relevante` **não** deve ser gravado só no banco: o `--recriar` dropa as
tabelas e a curadoria manual se perde. A curadoria vive num arquivo JSON
versionado e é **reaplicada automaticamente a cada execução**:

- Arquivo: `hermes_mpt_ops/data/curadoria_atos.json`
- Chave: **`data + tipo + numero` (+ página opcional) — NUNCA por ID**, pois os
  IDs mudam a cada recriação.
- O `catalogar_atos.py` lê esse JSON ao final e aplica `relevante`/`ementa`
  limpa/`observacao` via UPDATE.

Formato:
```json
[
  {"data":"2024-11-06","tipo":"RESOLUÇÃO","numero":"222","pagina":24,
   "relevante":1,"ementa":"...","observacao":"..."}
]
```

Sempre que catalogar um mês novo, **editar o `curadoria_atos.json`** adicionando
os atos normativos relevantes do mês, e commitar junto com o banco.

## O que conta como "relevante" (regulamento de processos administrativos)

- **Resoluções CSMPT** transcritas (ex: Resolução 222/2024 — organização de
  unidades, atribuições de ofícios, distribuição livre/prevenção, autuação e
  cadastramento de procedimentos finalísticos)
- **Portarias que instituem/alteram** manuais, regimentos, comitês de governança,
  normas de organização/funcionamento
- **Editais/portarias de cadastramento** (ex: reversão de bens/recursos)
- **NÃO inclui** portarias de expediente: fiscais de contrato, licenças, escalas
  de plantão, substituições de membros, designações avulsas.

## Pitfalls

- **Boletins extraordinários (`BS-NNN.1`, "BSE EXTRAORDINÁRIO"):** o
  `audit_boletim.py` detecta **0 atos** neles (tipo e número em linhas separadas:
  "EDITAIS\nNº 82, DE 4 DE NOVEMBRO DE 2024"), logo **não gera `.md`** e ficam de
  fora do catálogo. Gerar o MD manualmente com pymupdf (`fitz` → texto por página
  + `<!-- pág N -->`) antes de catalogar.
- **Regex de palavra-chave gera falsos positivos:** filtrar por
  `Institui/Altera/Regulamenta/Manual/Comitê/Regimento` no corpo captura portarias
  de expediente que apenas *citam* "regulamentares"/"Regimento" nos considerandos.
  A curadoria de relevância exige **leitura de conteúdo**, não regex.
- **A maioria do mês é expediente:** em nov/2024, apenas ~7 de 519 atos eram
  normativos; a maior concentração costuma estar num boletim que transcreve uma
  Resolução CSMPT integralmente.
- **Consulta rápida:** `sqlite3` CLI não existe no host — usar
  `.venv-bol/bin/python -c "import sqlite3; ..."`.
- **Confirmar commit:** scripts, banco e `curadoria_atos.json` devem ser
  commitados juntos; banco e JSON são versionados por exceção no `.gitignore`.

## Relacionadas

- `boletim-servico-mpt` — download (cloudscraper) + auditoria de extração.
- `analise-pgea` — análise de processos; o catálogo alimenta a busca de
  regulamentos por assunto.
