# Wrapper de cron — convenção de paths (ago/2026)

## Convenção de paths no wrapper (preferência do usuário)

O usuário rejeitou explicitamente centralizar paths em `ops_paths.py` ou `.env`.
Quer cada wrapper **autocontido**: variável no cabeçalho, corpo aponta para a variável.

Modelo python:
```python
#!/usr/bin/env python3
import runpy, sys
# --- Paths ---
OPS_SCRIPTS = "/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/scripts"
sys.argv = ["script.py"]
sys.path.insert(0, OPS_SCRIPTS)   # se o script real importar módulo irmão (ex: ops_paths)
runpy.run_path(f"{OPS_SCRIPTS}/script.py", run_name="__main__")
```

Modelo bash:
```bash
#!/bin/bash
# --- Paths ---
OPS_SCRIPTS="/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/scripts"
exec "$OPS_SCRIPTS/script.sh" "$@"
```

Se a path mudar de novo, editar **uma linha** (a variável) — não grep no meio do código.

## Pitfall: `runpy.run_path` não adiciona o diretório do script ao sys.path

Quando o script real importa um módulo irmão da mesma pasta (ex: `from ops_paths import ...`),
rodar via `runpy.run_path` falha com:

```
ModuleNotFoundError: No module named 'ops_paths'
```

mesmo que o script funcione rodado direto (`cd scripts && python3 script.py`).
Causa: `runpy.run_path(<caminho de arquivo>)` **não** insere o diretório do script em
`sys.path` (só o faz quando recebe um nome de módulo/package).

**Fix no wrapper:** `sys.path.insert(0, OPS_SCRIPTS)` **antes** do `runpy`.

Bug real: `sync-skills-ops.py` (ago/2026) — o wrapper `~/.hermes/scripts/sync-skills-ops.py`
falhava com `ModuleNotFoundError: No module named 'ops_paths'` até adicionarmos o insert.
A corretude do próprio script real não era o problema; era o wrapper não expor a pasta.

## Pitfall: `find /` + `2>/dev/null` esconde a causa real

No ambiente hermes-01 o usuário `hermes` **não tem permissão de leitura sobre a raiz `/`**
(`find: '/': Permission denied`). `find / ...` falha **na entrada**, não alcança subárvores.
Pior, `find / ... 2>/dev/null` engole o erro e parece "nada encontrado".

- Sempre buscar a partir de subárvores acessíveis: `/opt`, `/home`, `/etc`, `/var` — não da raiz.
- NÃO suprimir stderr com `2>/dev/null` quando estiver investigando localização de arquivos —
  ele esconde a causa real (permission vs. inexistente).
- Repos MPT vivem em `/opt/data/hermes-data/mpt_workspace/{hermes_mpt_ops,hermes_mpt_kb}`
  (layout antigo direto em `/opt/data/hermes-data/` foi removido).
