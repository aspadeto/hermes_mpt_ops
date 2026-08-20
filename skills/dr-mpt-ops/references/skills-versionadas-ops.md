# Skills versionadas no OPS (convenção do ambiente)

Estabelecido pelo usuário em **20/08/2026**. Regra recorrente ao criar/editar skills.

## Fato-chave

Skills do Hermes vivem em `~/.hermes/skills/<categoria>/<skill>/` e **NÃO são
repo git** (verificado: `~/.hermes` não tem `.git`, nem `~/.hermes/skills`).
Só entram no backup do Google Drive (que inclui `.hermes`), não no git.

Para versionar as skills **customizadas** do ambiente, elas são espelhadas em
**`hermes_mpt_ops/skills/`** (repo OPS, git + auto-commit).

## Regra crítica (ao criar skill nova)

> **AO CRIAR UMA SKILL NOVA customizada, adicionar o nome à lista `CUSTOM_SKILLS`
> no topo de `hermes_mpt_ops/scripts/sync_skills_ops.py`.**
> Se não fizer, a skill não é copiada nem versionada.

## Mecânica

- **Script:** `hermes_mpt_ops/scripts/sync_skills_ops.py`
  - Lista `CUSTOM_SKILLS` = 13 skills customizadas (conhecimento MPT/DR + infra do ambiente).
  - **Só custom entram** — bundled do Hermes (github-*, creative, etc.) NÃO (poluem o repo).
  - Distinção por **lista explícita**, não por mtime/conteúdo (mtime não diferencia bundle de custom — ambos atualizados em ago/2026).
  - Estrutura: itera `~/.hermes/skills/<categoria>/<skill>/` (e skills diretas).
  - Não copia: `__pycache__`, `.archive/`, metadados `.curator_*`/`.bundled_*`; só `EXTS` (`.py .sh .bash .md .txt .toml .json .yaml .yml`).
- **Cron job:** `Sync skills → OPS` (every 10m, `no_agent`, wrapper `sync-skills-ops.py` em `~/.hermes/scripts/`). O auto-commit (10min) depois commita a pasta `skills/`.
- **Wrapper:** padrão cron do Hermes — arquivo real em `~/.hermes/scripts/` que chama o script do OPS via `runpy`.

## Lista atual (20/08/2026) — 13 skills

Conhecimento MPT/DR: `dr-mpt-ops`, `pesquisa-boletins-inteligente`,
`boletim-servico-mpt`, `analise-pgea`, `catalogar-atos-boletins`,
`compreensao-pgea`, `ingestao-pdf-wiki`, `documentos-mpt`.
Infra do ambiente: `hermes-cron-automation`, `browser-infrastructure`,
`container-host-ssh`, `selfhosted-remote-access`, `tailscale-remote-access`.

## Pitfall

- `write_file`/`patch` em `~/.hermes/scripts/<wrapper>` seguem symlink e podem
  sobrescrever o código real versionado — sempre escrever na área segura e `cp`.
- Se o repo OPS foi renomeado, atualizar os caminhos do wrapper/sync.
