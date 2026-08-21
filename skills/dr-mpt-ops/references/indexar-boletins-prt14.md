# Indexador de Boletins PRT14 — 07/08/2026

## Contexto
Pipeline de teste pesado: baixou 24 boletins OUT/2025 (19MB) → PDF→MD (`audit_boletim.py`) → indexação PRT14 → SQLite → PDFs apagados.

## Script versionado
`OPS_PATH/scripts/indexar_boletins_prt14.py`

**Entrada:** diretório com MDs extraídos (`audit_boletim.py` gera headers `## TIPO Nº X`)

**Saída:** SQLite (`boletins_idx.db`) com tabela `atos`:
```sql
CREATE TABLE atos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    boletim TEXT NOT NULL,
    data_bs TEXT,
    tipo TEXT,
    numero TEXT,
    titulo TEXT,
    relevante INTEGER DEFAULT 0,  -- 0=irrelevante, 1=menciona, 2=da PRT14
    resumo TEXT
);
```

## Técnica-chave: isolamento de sub-bloco PRT14

O boletim tem uma seção `PROCURADORIAS REGIONAIS` que contém **várias regionais na mesma página** (PRT-8ª, 11ª, 13ª, 14ª...). O cabeçalho de cada ato (`## PORTARIA Nº 230`) cobre a página inteira.

**Solução:** `_subbloco_prt14(corpo)` divide o corpo do ato pelos cabeçalhos de regional (`PRT-NNª REGIÃO`) e retorna só o trecho da 14ª.

```python
cab = re.compile(
    r"PRT-?\s*(\d{1,2})[ªa]\s*REGI[ÃA]O(?:s*[–-]\s*[A-ZÇÃÉÍÓÚÊ /]+)?",
    re.IGNORECASE,
)
```

## Níveis de relevância

| Nível | Critério | Regex |
|-------|----------|-------|
| 2 (da PRT14) | Sub-bloco 14ª contém assinatura/verbos de ato | `PROCURADOR-CHEFE...14ª` ou `no uso de suas atribuições` / `RESOLVE` / `designar` |
| 1 (menciona) | Corpo menciona 14ª/RO/AC | `14ª REGIÃO` / `PORTO VELHO/RO` / `RONDÔNIA` / `ACRE` / `PRT\s*-?\s*14` |
| 0 | Irrelevante | — |

## Extração de ementa
`_ementa(sub)` pega o texto entre o número/data do ato (`N° X, DE DD DE MÊS DE AAAA`) e a assinatura (`O PROCURADOR-CHEFE` / `RESOLVE` / `Considerando`).

## Resultados OUT/2025
- 24 boletins (184 → 205.1)
- 170 atos indexados
- **14 atos nível 2 (da PRT14)**: elogios, designações, manutenção predial, segurança institucional, posse do Procurador-Chefe
- 16 atos nível 1 (mencionam)

## Uso
```bash
cd /tmp
OPS_PATH/.venv-bol-md/bin/python \
  OPS_PATH/scripts/indexar_boletins_prt14.py \
  /tmp/md-out2025/ --db /tmp/boletins_idx.db
```