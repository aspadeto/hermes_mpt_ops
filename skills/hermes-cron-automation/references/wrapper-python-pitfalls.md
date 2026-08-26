# Pitfalls de Wrappers Python do Cron (runpy) + Jobs Unpinned

Registrado em 2026-08-25 a partir de duas correções reais no ambiente
hermes_mpt (baixar_boletins_novos.py e "Lint semanal KB").

## 1. `runpy.run_path` NÃO adiciona o dir do script ao `sys.path`

**Sintoma:** `ModuleNotFoundError: No module named 'ops_paths'` ao rodar um
wrapper do cron.

**Causa:** o wrapper chama `runpy.run_path(f"{OPS}/baixar_boletins_novos.py")`
e o script real faz `from ops_paths import OPS_PATH, ...`. Como `runpy.run_path`
não insere o diretório do arquivo em `sys.path` (diferente de um `python
script.py` normal), o módulo irmão `ops_paths.py` — que vive na MESMA pasta
`scripts/` — não é encontrável.

**Correção obrigatória no wrapper (antes do run_path):**
```python
import runpy, sys
OPS_SCRIPTS = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/scripts"
sys.argv = ["baixar_boletins_novos.py"]
sys.path.insert(0, OPS_SCRIPTS)          # <- esta linha estava faltando
runpy.run_path(f"{OPS_SCRIPTS}/baixar_boletins_novos.py", run_name="__main__")
```

**Como detectar facilmente:** comparar o wrapper quebrado com um wrapper que
funciona (`sync_skills_ops.py` tem a linha e documenta o porquê no docstring).

**Verificação:** rodar o wrapper num venv que tenha as deps do script (ex:
`hermes_mpt_ops/.venv-bol` tem `cloudscraper 1.2.71`; o venv do hermes-agent
`~/.hermes/hermes-agent/venv` também). Testar com `--dry-run` quando o script
tiver esse modo, para não executar efeitos colaterais (downloads).

## 2. Jobs de cron AGENT-DRIVEN unpinned são bloqueados por `drift_skip`

**Sintoma:** job agendado (ex: "Lint semanal KB") falha com
`RuntimeError: [drift_skip:silent] ... global inference config drifted since
this job was created (model 'X' -> 'Y'), and this job is unpinned. No inference
call was made.` — `last_status: error`, 0 API calls.

**Causa:** o job não tem modelo/provider fixos (unpinned). Quando a config
global de inferência muda (ex: `nvidia/nemotron-...` -> `deepseek/...`), o
scheduler recusa rodar um job unpinned para evitar gasto não intencional. Não
é bug do script — o agente nunca chega a rodar.

**Correção (pin explícito no job):**
```bash
hermes cron edit bc95d2240dd8 --provider openrouter --model deepseek/deepseek-v4-flash-0731
```
Depois `cronjob action=run` e confirmar que os campos `model`/`provider`
aparecem preenchidos no job (e que o agente de fato roda dessa vez).

**Distinção no `cronjob action=list`:**
- `no_agent: true` + `script` → executa só o script (stdout entregue, custo zero)
- `skill: <skill>` sem script → **agent-driven**: o scheduler constrói um
  `AIAgent`, injeta o conteúdo da skill no prompt (`_build_job_prompt`) e roda
  um loop de ferramentas real (gasta tokens). Este é o caso que sofre drift_skip.
