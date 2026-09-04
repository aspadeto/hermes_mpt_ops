# Backup Google Drive — Diagnóstico de Falha e Exclusões

Guia para quando o `hermes-backup.py` falha ou o tar fica grande demais.

## Como o cron registra a falha (diagnosticar primeiro)

O job de backup roda `no_agent` e grava a saída em:
`~/.hermes/cron/output/<job_id>/*.md` (job_id `13adb255dd91`).
Cada arquivo traz `**Status:** script failed` + `stderr` (traceback completo) +
`stdout` (o progresso até onde parou). Ler **o .md mais recente** antes de
qualquer coisa — mostra se a falha foi no import, no tar ou no upload.

Para simular o run do cron sem env herdada (valida wrapper):
```bash
env -i HOME=/home/hermes PATH=/usr/bin:/bin python3 ~/.hermes/scripts/hermes-backup.py
```

## Cadeia real de falha (ago/2026) — sintomas distintos

| Sintoma | Causa provável | Onde vê no output .md |
|---|---|---|
| `ModuleNotFoundError: No module named 'ops_paths'` | wrapper esqueceu `sys.path.insert(OPS_SCRIPTS)` + forçar `OPS_PATH`/`KB_PATH` | stderr, antes de qualquer stdout |
| `FileNotFoundError: .../hermes_mpt_ops/...` | wrapper aponta caminho antigo (sem `mpt_workspace`) | stderr |
| `ResumableUploadError ... storageQuotaExceeded` | quota do Drive (15GB free) estourou | stderr + stdout mostra o `💾 Size` do tar |
| `RefreshError: invalid_grant` no `drive search` | token Google (`google_token.json`) precisa reauth | stderr antes do main |

> `invalid_grant` = reautorizar OAuth (`google_setup.py --auth-url/--auth-code`,
> como no checklist pós-migração). NÃO é bug do script — é setup que só o
> usuário desbloqueia. Sem autenticação, nem `drive search` roda.

## ⚠️ Exclusões do backup ficam OBSOLETAS → tar infla → estoura quota

O tar passou de ~94MB (meta) para **~2230MB** porque diretórios **regeneráveis**
entraram no backup sem serem adicionados a `EXCLUDE`/`DATA_EXCLUDE`. Numa conta
Google gratuita isso estoura os 15GB após alguns backups (rotação guarda 7
recentes → ~2.2GB × 7 = 15.4GB).

Antes de ativar/religar o backup, dimensionar o que entra e conferir contra as
listas de exclusão (`EXCLUDE_PATTERNS` em `.hermes`, `DATA_EXCLUDE` em data/):
```bash
du -sh ~/.hermes/* | sort -rh | head      # .hermes inteiro
# regeneráveis típicos que DEVEM estar excluídos:
#   hermes-agent/ (código+venv, reinstalável), home/ (já excluído),
#   node/, lsp/, bin/, profiles/ (recriáveis), backups/ (loop: backup antigo)
du -sh --exclude=mpt_workspace --exclude=.google-venv --exclude=backups /opt/data/hermes-data/*
#   .tool-venv (5.5G!) e demais venvs NÃO estão em DATA_EXCLUDE por padrão — só .google-venv
```
Regra: **venv/`__pycache__`/node_modules/código-binário reinstalável não vão ao
backup** (recriáveis com `uv`/instalador). Incluir em `EXCLUDE`/`DATA_EXCLUDE` o
que for regenerável. Depois, conferir o `💾 Size:` num backup de teste antes de
religar — deve voltar à ordem de ~100-200MB, não GB.

## Ordem de verificação ao religar um backup pausado

1. `env -i` rodar o wrapper → descarta problemas de wrapper/import.
2. Autenticação Google OK? (`drive search` sem `invalid_grant`).
3. `du -sh` dimensionar o que entraria → conferir exclusões antes do tar.
4. Testar tar+upload manual (ou `cronjob run` em background) e conferir `Size`.
5. Só então religar o agendamento e confirmar `last_status: ok`.
