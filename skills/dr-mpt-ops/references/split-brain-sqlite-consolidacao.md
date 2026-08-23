# Split-brain SQLite + env viciada — diagnóstico e consolidação (23/08/2026)

Quando um mesmo artefato (ex: `pendencias.db`) existe em DOIS lugares e os scripts
passam a usar o "errado", a causa raiz costuma ser **env var `OPS_PATH`/`KB_PATH`
viciada apontando para o caminho legado**, ou um **wrapper de cron que não seta o
`sys.path`**. Este é o roteiro validado para detectar, consolidar e eliminar a
divergência sem perder dados.

## Sintomas (um OU mais)

- Usuário diz "sinto falta de pendências" / "há duas listas".
- `pendencia.py list` mostra um conjunto, mas o usuário lembra de outras.
- Cron job de pendência com `last_status: error`.
- Pastas órfãs `/opt/data/hermes-data/hermes_mpt_*` (sem `mpt_workspace`) criadas
  pelo `mkdir` do `ops_paths.py` no import.

## Passo 1 — achar TODOS os bancos duplicados

```bash
find /opt/data /home/hermes -name "pendencias.db" 2>/dev/null
# ex: .../mpt_workspace/hermes_mpt_ops/data/pendencias.db  (canônico)
#     .../hermes_mpt_ops/data/pendencias.db               (órfão, caminho legado)
```

## Passo 2 — descobrir QUAL path cada script resolve

`ops_paths.py` tem precedência: **env var > default**. Se `OPS_PATH` estiver no
ambiente (ou num `.bashrc` do HOME efetivo), o script usa esse — não o default.

```bash
env | grep -iE "OPS_PATH|KB_PATH|HERMES_DATA"
grep -n "OPS_PATH\|KB_PATH" ~/.bashrc              # HOME efetivo = /home/hermes/.hermes/home
# confirmar qual path ops_paths resolve:
python -c "import sys; sys.path.insert(0,'/opt/data/.../scripts'); import ops_paths; print(ops_paths.PENDENCIAS_DB)"
```

**Nota sobre HOME efetivo:** se `HOME=/home/hermes/.hermes/home`, o `~/.bashrc`
que vale é `/home/hermes/.hermes/home/.bashrc` (NÃO `/home/hermes/.bashrc`).
O gateway/cron usa `HOME=/home/hermes` (default do ops_paths = correto), mas o
terminal do agente herda o `.bashrc` viciado → scripts via terminal divergem dos
via cron.

## Passo 3 — comparar conteúdo dos dois bancos

```python
import sqlite3
for p in [".../mpt_workspace/.../pendencias.db", ".../legado/.../pendencias.db"]:
    c = sqlite3.connect(p)
    print(p, "total:", c.execute("SELECT COUNT(*) FROM pendencias").fetchone()[0])
    print("  ids:", [r[0] for r in c.execute("SELECT id FROM pendencias")])
```
O banco com MAIS registros (ex: 24 antigos + históricos) é o canônico; o que só
tem os recém-criados é o órfão.

## Passo 4 — BACKUP antes de qualquer escrita

```bash
mkdir -p /tmp/consolidacao_bkp
cp -v <canonico> /tmp/consolidacao_bkp/canonico_antes.db
cp -v <orfao>    /tmp/consolidacao_bkp/orfao_antes.db
cp -v ~/.bashrc  /tmp/consolidacao_bkp/bashrc_antes
```

## Passo 5 — migrar registros do órfão para o canônico

Inserir no canônico os registros ausentes (dedupe por `titulo`), preservando
`tipo/prioridade/status/criada_em/resolvida_em`. **Não copiar `id`** — deixar o
autoincrement do canônico.

```python
existentes = {r[1] for r in cc.execute("SELECT id,titulo FROM pendencias")}
for r in rows_orfaos:
    d = dict(zip(cols, r))
    if d["titulo"] in existentes: continue
    cc.execute("INSERT INTO pendencias (titulo,contexto,tipo,prioridade,status,criada_em,resolvida_em) VALUES (?,?,?,?,?,?,?)",
               (d["titulo"],d["contexto"],d["tipo"],d["prioridade"],d["status"],d["criada_em"],d["resolvida_em"]))
```

## Passo 6 — corrigir a FONTE (não só o sintoma)

1. **`.bashrc` do HOME efetivo:** apontar para `mpt_workspace`.
2. **Wrappers de cron** (`~/.hermes/scripts/*.py` que usam `runpy.run_path`):
   forçar env + `sys.path` ANTES do runpy (ver pitfall no SKILL.md):
   ```python
   os.environ["OPS_PATH"] = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops"
   os.environ["KB_PATH"] = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb"
   OPS_SCRIPTS = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/scripts"
   sys.path.insert(0, OPS_SCRIPTS)
   ```
3. **Testar como o cron roda** (env limpa, fora do OPS):
   ```bash
   env -i HOME=/home/hermes PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
     /opt/data/hermes-data/.tool-venv/bin/python /home/hermes/.hermes/scripts/pendencia-remind.py
   ```

## Passo 7 — remover órfãos e validar

- Confirmar que as pastas órfãs estão vazias (ou só contêm o banco já migrado),
  com backup feito.
- Remover pastas órfãs + `.db` duplicado na raiz legada.
- Validar: `pendencia.py stats` via wrapper (env limpa) deve mostrar o total
  consolidado (ex: `18 ativas | 13 resolvidas | 3 canceladas | 34 total`).
- Conferir o cron com `cronjob action=list` → `last_status: ok` após correção.

## Por que NÃO ignorar

Este ambiente já teve MÚLTIPLOS episódios de path drift (Docker→VM em 07/08,
renomeações de repo, env `KB_PATH` viciada). O padrão é recorrente — sempre que
mexer em caminhos, rodar este roteiro em vez de confiar em um único banco.
