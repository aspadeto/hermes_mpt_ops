# Padrão de Wrapper para Cron do Hermes

## Restrições do cron (verificadas em 01/08/2026)

O campo `script` de um cron job (`no_agent=true`) exige:
- **Arquivo REAL** em `~/.hermes/scripts/` (resolvido por nome, sem caminho absoluto)
- **SEM symlinks** apontando para fora → erro: `Blocked: script path resolves outside the scripts directory`
- **SEM argumentos** no campo script → `pendencia.py remind` vira `Script not found: .../pendencia.py remind`

## Motivo da arquitetura

O código REAL dos scripts vive versionado em `hermes_mpt_ops/scripts/` (repo git). O cron não consegue apontar para lá diretamente, então `~/.hermes/scripts/` contém **wrappers** que executam o código versionado. Wrappers NÃO são versionados (são atalhos de ambiente).

## Modelos

### 1. Wrapper bash (script shell)

```bash
#!/bin/bash
# Wrapper — executa o script versionado no hermes_mpt_ops.
exec /opt/data/hermes-data/hermes_mpt_ops/scripts/meu-script.sh "$@"
```

### 2. Wrapper python (sem argumentos)

```python
#!/usr/bin/env python3
"""Wrapper — executa o script versionado no hermes_mpt_ops."""
import runpy
import sys

sys.argv[0] = "/opt/data/hermes-data/hermes_mpt_ops/scripts/meu-script.py"
runpy.run_path("/opt/data/hermes-data/hermes_mpt_ops/scripts/meu-script.py", run_name="__main__")
```

### 3. Wrapper python com argumento FIXO (ex: modo remind)

Cron não aceita args — criar wrapper DEDICADO que injeta o argv antes do runpy:

```python
#!/usr/bin/env python3
"""Wrapper dedicado para o cron de LEMBRETE."""
import runpy
import sys

sys.argv = ["pendencia.py", "remind"]
runpy.run_path("/opt/data/hermes-data/hermes_mpt_ops/scripts/pendencia.py", run_name="__main__")
```

## ⚠️ Pitfall crítico: write_file segue symlink

Se `~/.hermes/scripts/foo.py` for um **symlink** para o código versionado e você usar `write_file` nele, o conteúdo do **arquivo real no OPS é sobrescrito** (o symlink é seguido). Recuperação: `git checkout -- <arquivo>` no repo OPS.

Regras:
- Sempre `ls -la` antes de escrever em `~/.hermes/scripts/`
- Para criar/editar wrapper: escrever em `/opt/data/` (safe root) e `cp` via terminal
- Código real só muda via edit no OPS + commit

## Verificação pós-instalação

```bash
# Testar wrapper manualmente
/home/hermes/.hermes/scripts/meu-script.py

# Rodar cron job na hora
cronjob(action='run', job_id='...')  # conferir execution_success: true
```
