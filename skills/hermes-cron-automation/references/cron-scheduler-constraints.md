# Evidências do Código-Fonte — Cron Scheduler

Fonte: `/opt/hermes/cron/scheduler.py`, função de execução de script (linhas ~2233-2264).
Verificado em 2026-08-01.

## Guard de segurança (symlink escape / path traversal)

```python
scripts_dir = _get_hermes_home() / "scripts"
scripts_dir.mkdir(parents=True, exist_ok=True)
scripts_dir_resolved = scripts_dir.resolve()

raw = Path(script_path).expanduser()
if raw.is_absolute():
    path = raw.resolve()
else:
    path = (scripts_dir / raw).resolve()

# Guard against path traversal, absolute path injection, and symlink
# escape — scripts MUST reside within HERMES_HOME/scripts/.
try:
    path.relative_to(scripts_dir_resolved)
except ValueError:
    return False, (
        f"Blocked: script path resolves outside the scripts directory "
        f"({scripts_dir_resolved}): {script_path!r}"
    )

if not path.exists():
    return False, f"Script not found: {path}"
if not path.is_file():
    return False, f"Script path is not a file: {path}"
```

## Interpreter por extensão (shebang ignorado)

```python
suffix = path.suffix.lower()
if suffix in {".sh", ".bash"}:
    argv = [_bash, str(path)]
else:
    argv = [python_exe, str(path)]
```

- `.sh`/`.bash` → bash (resolvido dinamicamente via `shutil.which`)
- qualquer outra extensão → python
- o shebang do arquivo é **deliberadamente ignorado** (superfície pequena e auditável)

## Erros reais observados (2026-08-01, ambiente PRT14)

| Erro | Causa |
|------|-------|
| `Blocked: script path resolves outside the scripts directory (...): 'wiki-auto-commit.sh'` | O cron tinha `script: wiki-auto-commit.sh` que era **symlink** para `/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/...` — o resolve() seguiu o symlink e o guard bloqueou |
| `Script not found: /home/hermes/.hermes/scripts/pendencia.py remind` | Campo `script` com **argumento** — o cron tratou `"pendencia.py remind"` como nome de arquivo inteiro |
| `Script path must be relative to ~/.hermes/scripts/. Got absolute path: '/opt/data/...'` | Campo `script` com **caminho absoluto** (rejeitado na validação do cronjob tool) |

## Conclusões operacionais

1. Cron só aceita: **nome de arquivo relativo**, **arquivo real** (não symlink),
   **sem argumentos** — tudo dentro de `~/.hermes/scripts/`.
2. Solução para scripts versionados (repo hermes_mpt_ops): wrapper fino real em
   `~/.hermes/scripts/` que delega (`exec` para shell, `runpy.run_path` para python).
3. Wrappers com modo fixo (ex: `pendencia-remind.py`) quando o script real precisa
   de argumentos que o cron não pode passar.
