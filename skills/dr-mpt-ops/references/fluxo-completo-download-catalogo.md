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
| `extrair_md_boletins.py` | Extrai texto PDF→MD plano (frontmatter + páginas) | `hermes_mpt_ops/scripts/` |
| `catalogar_atos.py` | Detecta atos normativos, popula SQLite | `hermes_mpt_ops/scripts/` |

> ⚠️ Os scripts ad-hoc `processar_boletins_novos.py` e `processar_todos_boletins.py`
> foram **substituídos** pelo versionado `extrair_md_boletins.py` e removidos
> (limpeza 20/08/2026). Para converter PDFs→MD, usar o script do OPS.

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

# 3. Converter PDFs → MD (script versionado)
python3 hermes_mpt_ops/scripts/extrair_md_boletins.py \
  --orig hermes_mpt_kb/raw/boletins --dest hermes_mpt_kb/boletins

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

2. **Organização em pastas `YYYY-MM-DD`** — o `catalogar_atos.py` espera essa estrutura. O script versionado `extrair_md_boletins.py` faz a conversão + organização usando a data extraída do PDF (CIRCULAÇÃO/cabeçalho).

3. **Catálogo detecta 25+ tipos de ato** — PORTARIA, RESOLUÇÃO, INSTRUÇÃO NORMATIVA, DECISÃO, EDITAL, DESPACHO, AVISO, EXTRATO, ATA, COMUNICADO, RETIFICAÇÃO, OFÍCIO, REQUERIMENTO, PARECER, RELATÓRIO, MEMORANDO, etc.

4. **Deduplicação automática** — o parser remove atos repetidos (mesmo tipo+número+página), mantendo o que tem ementa/órgão.

5. **Curadoria persistente** — arquivo `data/curadoria_atos.json` sobrevive a `--recriar` do banco (chave: data+tipo+número+página).

6. **WAF instável em certos meses** — Fev/2026 falhou com erro `form consultaForm não encontrado` (ViewState); Mar–Jun/2026 retornaram "nenhum boletim encontrado". O cloudscraper bypassa o WAF mas o servidor às vezes retorna HTML quebrado ou vazio. Re-tentar com retry/backoff (ex: 3 tentativas com delay exponencial) resolve na maioria dos casos.

7. **Mapeamento número→data** — o `extrair_md_boletins.py` extrai a data direto do PDF (CIRCULAÇÃO/cabeçalho da capa), não depende de dicionário manual.

## Próximos passos sugeridos

- Automatizar via cron (ex: toda segunda 06:00, últimos 7 dias)
- Adicionar verificação de integridade (PDFs baixados vs catalogados)
- Implementar retry/backoff no `baixar_boletim.py` para meses com WAF instável (Fev–Jun/2026)
- Tentar rebaixar Fev–Jun/2026 com retry exponencial