# Acesso SSH Container → Host (refazer do zero)

Runbook completo versionado no repo: `hermes_mpt_ops/docs/RUNBOOK-SSH-HOST.md`.
Este arquivo é o resumo operacional para o agente.

## Arquitetura

```
CONTAINER hermes-agent                    HOST (hermes-01)
  ~/.hermes/home/.ssh/hermes_host_key  →  ~/.ssh/authorized_keys (usuário hermes)
  ssh host → 172.19.0.1:22                grupo docker (sem sudo p/ docker)
  /opt/data/.ssh/config (alias)           sudo NOPASSWD: só reboot
```

## Fatos verificados (ago/2026)

- Host: `hermes-01`, usuário `hermes` (uid 1000), hostname do host via `ssh host 'hostname'`
- Gateway Docker = IP do host: descobrir com `ip route | grep default`
- Docker funciona SEM sudo (usuário no grupo `docker`)
- `sudo reboot` liberado via `/etc/sudoers.d/hermes-reboot` (NOPASSWD só reboot)
- Fingerprint da chave: `SHA256:BIOZtm9NLHcW6+Uy4zqW6qYNV1kDsbBKnrdtLyG7/SY`

## O quirk crítico (o que mais custou achar)

O **processo ssh do agente usa `/opt/data` como HOME**, não `$HOME` do shell.
Prova: `ssh -G host` mostra `identityfile /opt/data/.ssh/id_rsa` — ele procura
chaves/config em `/opt/data/.ssh/`, ignorando `~/.ssh` do shell.

Por isso:
- Config funcional → `/opt/data/.ssh/config` (alias `host`, IdentityFile absoluto `/opt/data/.ssh/hermes_host_key`)
- Chave real (persistente, fora do backup) → `/home/hermes/.hermes/home/.ssh/hermes_host_key`
- Symlinks em `/opt/data/.ssh/` apontam para a chave real

Sintoma quando o config está errado: `ssh host` → `Could not resolve hostname host`.

## Validação rápida

```bash
ssh -o BatchMode=yes host 'hostname; whoami'      # hermes-01 / hermes
ssh host 'docker compose -f ~/hermes-data/hermes_mpt_ops/docker/docker-compose.yml ps'
ssh host 'sudo -n /sbin/reboot --help >/dev/null 2>&1 && echo OK'   # validar NOPASSWD
ssh-keygen -lf /home/hermes/.hermes/home/.ssh/hermes_host_key.pub   # fingerprint
```

## Segurança

- Chave privada: 600, `.ssh`: 700, config: 600
- Chave privada NUNCA no backup Drive (`EXCLUDE_PATTERNS` do hermes-backup.py inclui `.ssh/`)
- Chave privada NUNCA em repo git (vive em `~/.hermes/home/.ssh/`, fora dos repos)
- Sudo mínimo: apenas `reboot` (princípio do menor privilégio)
- Se a chave for regenerada, a pública muda → refazer authorized_keys no host (Fase 4 do runbook)
