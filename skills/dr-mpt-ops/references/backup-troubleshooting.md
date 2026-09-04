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

> `invalid_grant` = token **revocado/expirou** → reautorizar OAuth. NÃO é bug do script — é setup que só o usuário desbloqueia. Sem autenticação, nem `drive search` roda.

### Reauth OAuth entre 2 etapas (setup.py — o script é esse)

O script de reauth é `setup.py` do skill google-workspace (**`google_setup.py` NÃO existe mais**):
```bash
GSETUP="/opt/data/hermes-data/.google-venv/bin/python \
  /home/hermes/.hermes/skills/productivity/google-workspace/scripts/setup.py"
env -i HOME=/home/hermes PATH=/usr/bin:/bin $GSETUP --check        # TOKEN_REVOKED se precisa reauth
# 1) gera URL (já cobre gmail/calendar/drive/sheets/docs/contacts), o pendente fica salvo p/ o passo 2:
env -i HOME=/home/hermes PATH=/usr/bin:/bin $GSETUP --auth-url
# 2) usuário autoriza no navegador, a página de redirect http://localhost:1 FALHA (esperado),
#    ele copia a URL inteira da barra e cola; conclui a troca de código→token:
env -i HOME=/home/hermes PATH=/usr/bin:/bin $GSETUP --auth-code "http://localhost:1/?state=...&code=4/0ATs..."
env -i HOME=/home/hermes PATH=/usr/bin:/bin $GSETUP --check        # AUTHENTICATED
```
Estado: `setup.py --check` → `TOKEN_REVOKED` vs `AUTHENTICATED`; `google_api.py drive search` valida ponta-a-ponta.

## ⚠️ Drive trash conta CONTRA a quota (causa oculta de cota cheia)

`storageQuotaExceeded` NÃO é só tar grande: a **lixeira do Drive conta contra os 15GB**. Neste
execício a conta estava com 14.3GB em uso (quase cheia) apesar de só ~3GB de arquivos reais —
os outros **11.8GB estavam na lixeira** (`usageInDriveTrash`). Logo, mesmo depois de enxugar o tar
(2.46GB→507MB), a quota continua no limite até a lixeira ser esvaziada. **Sempre checar a cota
ANTES e DEPOIS de enxugar o tar**:
```bash
# cota completa (limit / usage / usageInDriveTrash) — google_api.py não expõe, usar build direto:
/opt/data/hermes-data/.google-venv/bin/python -c "
import json, pathlib
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
c=Credentials.from_authorized_user_info(json.loads(pathlib.Path('/home/hermes/.hermes/google_token.json').read_text()))
s=build('drive','v3',credentials=c,static_discovery=False)
a=s.about().get(fields='storageQuota,user').execute()
print(a['storageQuota'], a['user']['emailAddress'])"
```
Se `usageInDriveTrash` for alto: esvaziar a lixeira é **permanente e irreversível** (sem recuperação)
→ pedir decisão explícita do usuário antes de limpar, ou ele mesmo limpa no site do Drive.

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
