---
name: hermes-cron-automation
description: "Cron do Hermes: restrições do scheduler e padrão wrapper."
version: 1.0.0
author: Hermes Agent
platforms: [linux]
metadata:
  hermes:
    tags: [hermes, cron, automacao, wrapper, watchdog]
    category: hermes-ops
---

# Automação com Cron do Hermes

Como criar e manter cron jobs do Hermes que executam scripts, incluindo o
padrão wrapper para scripts versionados em repositório (hermes_mpt_ops).

## Quando Ativar

- Criar/editar cron jobs com `script` (especialmente `no_agent=true`)
- Mover scripts para um repositório git versionado mas mantê-los executáveis pelo cron
- Diagnosticar erro de cron como `Blocked: script path resolves outside...` ou `Script not found`

## Restrições do Scheduler (verificadas no código-fonte)

Fonte: `/opt/hermes/cron/scheduler.py` (função `_run_script`). O campo `script`
do cron tem 3 restrições **innegociáveis**:

| Restrição | Erro típico | Motivo |
|-----------|-------------|--------|
| ❌ **Sem caminho absoluto** | `Script path must be relative to ~/.hermes/scripts/` | Resolve contra `HERMES_HOME/scripts/` |
| ❌ **Sem symlinks p/ fora** | `Blocked: script path resolves outside the scripts directory` | Guard anti path-traversal + anti symlink-escape |
| ❌ **Sem argumentos** | `Script not found: .../pendencia.py remind` | O campo é o nome do arquivo, nada mais |

Regras adicionais:
- O script **precisa existir** e ser arquivo (`Script not found`)
- Interpreter por **extensão**: `.sh`/`.bash` → bash, resto → python (**shebang ignorado**)
- O diretório `~/.hermes/scripts/` é criado automaticamente se não existir

## Padrão: Código Versionado + Wrapper (recomendado)

O usuário versiona scripts no repo `hermes_mpt_ops`, mas o cron só executa arquivos
reais em `~/.hermes/scripts/`. Solução: **wrapper fino** no diretório do cron
que delega para o código versionado. O wrapper é arquivo REAL (nunca symlink).

### Wrapper shell (.sh)

```bash
#!/bin/bash
# Wrapper para cron — executa o script versionado no hermes_mpt_ops.
exec /opt/data/hermes-data/hermes_mpt_ops/scripts/kb-auto-commit.sh "$@"
```

### Wrapper Python (.py)

```python
#!/usr/bin/env python3
"""Wrapper para cron — executa o script versionado no hermes_mpt_ops."""
import runpy, sys
sys.argv[0] = "/opt/data/hermes-data/hermes_mpt_ops/scripts/pendencia.py"
runpy.run_path("/opt/data/hermes-data/hermes_mpt_ops/scripts/pendencia.py", run_name="__main__")
```

### Wrapper com argumentos fixos (modo dedicado)

Cron não aceita args → crie um wrapper por modo:

```python
#!/usr/bin/env python3
"""Wrapper dedicado para o cron de LEMBRETE (modo remind)."""
import runpy, sys
sys.argv = ["pendencia.py", "remind"]
runpy.run_path("/opt/data/hermes-data/hermes_mpt_ops/scripts/pendencia.py", run_name="__main__")
```

## Padrão Watchdog (no_agent)

Cron com `no_agent=true` + script = execução sem LLM (custo zero):
- **stdout vazio** → silencioso (nada é entregue) — use para watchdogs
- **stdout não-vazio** → entregue verbatim ao usuário
- **exit != 0** → alerta de erro

```bash
# Script que só fala quando há algo a reportar
if [[ -z $(git status --porcelain) ]]; then exit 0; fi   # silêncio
echo "mudanças detectadas"                                # entrega
```

## Pitfalls

- ⚠️ **`write_file`/`patch` seguem symlinks!** Se `~/.hermes/scripts/foo.py`
  for um symlink para o repo, escrever nele **sobrescreve o código real
  versionado** (perda silenciosa). SEMPRE: escrever em área segura (ex:
  `/opt/data/wrappers/`) e copiar com `cp`; verificar com `ls -la` se é real.
- ⚠️ **Env vars obsoletas poluem scripts.** `os.environ.get('KB_PATH', default)`
  usa o valor do ambiente se existir — um `.bashrc` com caminho antigo quebra
  tudo. Em scripts de cron, **fixar caminhos absolutos** ou usar nomes de env
  únicos (ex: `OPS_PATH`) sem colisão.
- ⚠️ **Criar wrapper e testar ANTES de atualizar o cron**: `bash wrapper.sh`
  e `python wrapper.py` manuais, depois `cronjob action=run` e conferir
  `last_status: ok`.
- ⚠️ **Migração de nomes = atualizar os cron jobs**: renomear um wrapper (ex:
  `wiki-auto-commit.sh` → `kb-auto-commit.sh`) exige `cronjob action=update`
  no campo `script`; e prompts de jobs LLM que citam caminhos antigos
  (`/opt/data/.../wiki`, repos antigos) precisam de update também. Conferir
  com `cronjob action=list` (campos `script` e `prompt_preview`) após qualquer
  rename de pasta/script/repo.

## Verificação

```bash
# Teste manual
bash ~/.hermes/scripts/meu-script.sh
# Rodar o job imediatamente (verificar last_status/execution_success)
# via cronjob action=run
```

## Referências

- `references/cron-scheduler-constraints.md` — trechos do código-fonte que comprovam as restrições
- Wiki do usuário: `referencias/cron-scripts-hermes.md` (documentação completa)
