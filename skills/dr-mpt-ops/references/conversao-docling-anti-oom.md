# Conversão Docling de boletins — lições da conversão 2024-2025 (ago/2026)

Pipeline para gerar markdown **estruturado** (headings/tabelas reais) dos boletins
MPT via Docling — usado em Chunkless RAG / `pesquisar_docling.py`. Script:
`hermes_mpt_ops/scripts/converter_docling.py`, saída em `hermes_mpt_kb/boletins_docling/`.

## ⚠️ Anti-OOM — SEMPRE `--jobs 1` (lição principal, validada em produção)

Rodar `--jobs 3` numa VM de 11GB fez o kernel **matar o processo python** por OOM
(`oom_score_adj=200`, `global_oom`) **e derrubar de quebra o `hermes-webui`**
(OOM kill em cascata). O processo OOM foi encontrado no journal:
`journalctl --since ... | grep -iE "oom|killed process"`.

**Em VM com o WebUI/outros serviços**: **nunca** `--jobs > 1`. Sequencial
(`--jobs 1`) é estável:
- ~5 min/boletim em CPU (os `.1`/extraordinários ~1 min)
- ~1h por ~12 boletins, ~23h/273 boletins
- Verificar `free -h` antes/durante; worker Docling ~2,6GB RSS.

## Retomar parcial (não reprocessar)

Comparar os PDFs-fonte com os MDs já gerados e passar `--pdf` só com os faltantes:

```bash
python3 - <<'EOF'
from pathlib import Path
RAIZ = Path('hermes_mpt_kb/raw/boletins'); DOCL = Path('hermes_mpt_kb/boletins_docling')
pdfs = sorted(RAIZ.glob('BS-*.pdf')); feito = {p.stem for p in DOCL.glob('*.md')}
falta = [p.stem for p in pdfs if p.stem not in feito]
Path('/tmp/faltantes.txt').write_text('\n'.join(falta))
EOF
# depois: converter_docling.py --pdf $(cat /tmp/faltantes.txt) --jobs 1
```

## `--pdf` aceita nome com ou sem `.pdf`

Bug corrigido ago/2026: o modo `--pdf` montava `RAIZ/pdf\stem` **sem extensão** →
`p.exists()` falso → "Convertendo 0 PDFs". Agora aceita `BS-009-2025` ou
`BS-009-2025.pdf`. Sintoma de regressão: `Convertendo 0 PDFs` sem erro.

## Datas de circulação ≠ numeração

Boletins numerados `2025` podem **circular em dez/2024** (`data: 2024-12-30`).
Classificar lote de conversão pelo **`data:` do frontmatter do MD plano**, não pelo
ano no nome do arquivo.

## Background wrapper

Wrapper em **`/opt/data/hermes-data/`** (não `/tmp/` — `write_file` grava fora do
`HERMES_WRITE_SAFE_ROOT`) chamando o script com `--jobs 1`; disparar com
`terminal(background=True, notify_on_complete=True)`. Monitorar progresso contando
MDs gerados; usar o `notify_on_complete` para sabem quando terminou (evita loop de
`poll`). Avisos `NNPACK: Unsupported hardware` são inofensivos (roda em CPU).