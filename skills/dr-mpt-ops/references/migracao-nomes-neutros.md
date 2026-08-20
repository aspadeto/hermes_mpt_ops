# Migração de Nomes Neutros — Refatoração Estrutural

Contexto: ago/2026 — repos `dr_mpt_kb`/`dr_mpt_ops` renomeados para `hermes_mpt_kb`/`hermes_mpt_ops` (estrutura neutra, replicável a outras Regionais). O usuário decidiu: **nada antigo é apagado** (repos antigos ficam como backup), pastas locais seguem o nome do repo.

## Quando aplicar

- Usuário quer renomear pastas/repos/scripts para nomes neutros (distribuição)
- Qualquer refatoração estrutural que toque caminhos referenciados em MUITOS lugares
- Princípio do usuário: "fazer mudanças estruturais cedo — com o tempo há cada vez mais links para corrigir"

## Ordem de execução (validada na migração real)

1. **Repos novos no GitHub criados pelo usuário** — esperar o endereço antes de mexer local
2. **`mv` das pastas locais** (`mv wiki hermes_mpt_kb`) — o `.git` interno continua válido
3. **Remotes**: `git remote set-url origin <novo-url>` nos dois repos
4. **Scripts**: renomear + `sed -i` em massa por caminhos/variáveis (ver tabela)
5. **`.bashrc`** + wrappers `~/.hermes/scripts/` (renomear wrapper do auto-commit junto)
6. **Cron jobs**: atualizar `script:` e prompts que citam caminhos/nomes (cronjob action=update)
7. **Skills**: `sed -i` nas skills que citam caminhos antigos
8. **Memória persistente**: `memory` replace nas entradas com caminhos antigos
9. **README + runbook**: `sed -i` dos nomes
10. **Testar** scripts (pendencia, consultar, importar, auto-commit) e push

## Mapeamento da migração (ago/2026)

| De | Para |
|----|------|
| `/opt/data/hermes-data/wiki` | `/opt/data/hermes-data/hermes_mpt_kb` |
| `/opt/data/hermes-data/dr_mpt_ops` | `/opt/data/hermes-data/hermes_mpt_ops` |
| `aspadeto/dr_mpt_kb` | `aspadeto/hermes_mpt_kb` |
| `aspadeto/dr_mpt_ops` | `aspadeto/hermes_mpt_ops` |
| `prt14.db` | `regional-orcamento.db` (+ arquivo de dados `demandas-orcamento-prt14-*.html.md` → `demandas-orcamento-regional-*.html.md`) |
| `WIKI_PATH` | `KB_PATH` |
| `pdf2wiki.py` | `pdf2kb.py` |
| `wiki-auto-commit.sh` | `kb-auto-commit.sh` |

## Sed em massa (comandos usados)

```bash
# Em scripts (todos .py/.sh)
sed -i \
  -e 's|/opt/data/hermes-data/wiki|/opt/data/hermes-data/hermes_mpt_kb|g' \
  -e 's|/opt/data/hermes-data/dr_mpt_ops|/opt/data/hermes-data/hermes_mpt_ops|g' \
  -e 's|prt14\.db|regional-orcamento.db|g' \
  -e 's|WIKI_PATH|KB_PATH|g' \
  *.py *.sh

# Depois conferir restantes com grep (sempre sobram casos manuais:
# DATA_EXCLUDE no backup, labels cosméticos, URLs do bootstrap, nomes de arquivo de dados)
grep -rn "dr_mpt_ops\|hermes-data/wiki\|prt14" *.py *.sh
```

## Pitfalls específicos da migração

- **`sed` NÃO pega tudo**: `DATA_EXCLUDE` no hermes-backup.py, labels de log (`ok "dr_mpt_ops clonado"`), URLs no bootstrap.sh, nome do arquivo de dados no importar-demandas.py — verificar com grep após o sed em massa.
- **Git detecta rename**: `git add -A` mostra `R` com % de similaridade — histórico preservado (99% no caso real). Não precisa de `git mv` prévio.
- **O auto-commit de 10min roda durante a migração** — ele pode commitar/pushar o rename do KB antes do commit manual do OPS. Verificar com `git log --oneline -3` antes de estranhar.
- **Cron job de lint/lembrete cita caminhos nos PROMPTS** (não só no `script:`) — atualizar ambos via `cronjob(action='update', prompt=...)`.
- **Wrappers do cron**: renomear o wrapper junto com o script real (`mv wiki-auto-commit.sh kb-auto-commit.sh` + `sed` interno) e atualizar o campo `script:` do cron job.
- **`.bashrc` do container** tem env vars de caminho — atualizar junto (é de onde vêm os env viciados).

## Verificação final (checklist)

```bash
ls -d /opt/data/hermes-data/hermes_mpt_*        # pastas
git -C <repo> remote get-url origin             # remotes novos
git -C <repo> status --short                    # limpo = push ok
grep -rn "nome_antigo" <repo> --include="*.py" --include="*.sh" --include="*.md"  # limpo
```
