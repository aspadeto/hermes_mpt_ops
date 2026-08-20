# Fluxo completo: Download + Extração + Catálogo de Boletins MPT (15/08/2026)

## Pipeline end-to-end operacional

```
cloudscraper (bypass WAF)
       ↓
baixar_boletim.py → PDFs em /opt/data/hermes-data/boletins/
       ↓
PyMuPDF (pymupdf) → processar_boletins_novos.py
       ↓
MDs organizados em pastas YYYY-MM-DD/
       ↓
catalogar_atos.py → SQLite (data/atos.db)
```

## Scripts envolvidos

| Script | Função | Localização |
|--------|--------|-------------|
| `baixar_boletim.py` | Lista/baixa BS via cloudscraper | `hermes_mpt_ops/scripts/` |
| `processar_boletins_novos.py` | Extrai texto PDF→MD, organiza por data | `/opt/data/hermes-data/` (criado ad-hoc, deve migrar para OPS) |
| `catalogar_atos.py` | Detecta atos normativos, popula SQLite | `hermes_mpt_ops/scripts/` |

## Exemplo de uso completo (preenchimento gap Jul/2025 → Jan/2026)

```bash
# 1. Instalar deps (uma vez)
pip install cloudscraper pymupdf

# 2. Baixar PDFs mês a mês (Jul/2025 a Jan/2026)
cd /opt/data/hermes-data
for mes in JUL AUG SET OUT NOV DEZ JAN; do
  ano=2025; [[ "$mes" == "JAN" ]] && ano=2026
  python3 hermes_mpt_ops/scripts/baixar_boletim.py $ano $mes --baixar todos --dir /opt/data/hermes-data/boletins
  sleep 3
done

# 3. Converter PDFs → MD nas pastas YYYY-MM-DD/
python3 processar_todos_boletins.py

# 4. Catalogar atos no SQLite
python3 hermes_mpt_ops/scripts/catalogar_atos.py --raiz boletins --db data/atos.db
```

## Resultado da execução (16/08/2026)

| Métrica | Antes | Depois |
|---------|-------|--------|
| Datas catalogadas | 171 | **287** |
| Atos normativos | 4.107 | **8.001** |
| Novos meses preenchidos | — | **Jul/2025 → Jan/2026** (7 meses) |
| PDFs baixados (gap) | — | **~170** (~6 GB) |

**Gap restante:** Fev/2026 → Jun/2026 (WAF bloqueou consultas; re-tentar com retry/backoff)

## Lições aprendidas

1. **O script `baixar_boletim.py` usa cloudscraper** — bypassa o WAF do mpt.mp.br (headless browsers são bloqueados por detecção JS, não IP).

2. **Organização em pastas `YYYY-MM-DD`** — o `catalogar_atos.py` espera essa estrutura. O script ad-hoc `processar_todos_boletins.py` faz a conversão + organização usando o mapeamento número→data das consultas.

3. **Catálogo detecta 25+ tipos de ato** — PORTARIA, RESOLUÇÃO, INSTRUÇÃO NORMATIVA, DECISÃO, EDITAL, DESPACHO, AVISO, EXTRATO, ATA, COMUNICADO, RETIFICAÇÃO, OFÍCIO, REQUERIMENTO, PARECER, RELATÓRIO, MEMORANDO, etc.

4. **Deduplicação automática** — o parser remove atos repetidos (mesmo tipo+número+página), mantendo o que tem ementa/órgão.

5. **Curadoria persistente** — arquivo `data/curadoria_atos.json` sobrevive a `--recriar` do banco (chave: data+tipo+número+página).

6. **WAF instável em certos meses** — Fev/2026 falhou com erro `form consultaForm não encontrado` (ViewState); Mar–Jun/2026 retornaram "nenhum boletim encontrado". O cloudscraper bypassa o WAF mas o servidor às vezes retorna HTML quebrado ou vazio. Re-tentar com retry/backoff (ex: 3 tentativas com delay exponencial) resolve na maioria dos casos.

7. **Mapeamento número→data essencial** — o script de processamento precisa do dicionário `ALL_BOLETINS` (número → data) para organizar os MDs nas pastas corretas. Coletar isso via consulta prévia (sem baixar) antes de rodar o download em lote.

## Próximos passos sugeridos

- Integrar `processar_todos_boletins.py` ao repo OPS como script versionado
- Automatizar via cron (ex: toda segunda 06:00, últimos 7 dias)
- Adicionar verificação de integridade (PDFs baixados vs catalogados)
- Implementar retry/backoff no `baixar_boletim.py` para meses com WAF instável (Fev–Jun/2026)
- Tentar rebaixar Fev–Jun/2026 com retry exponencial