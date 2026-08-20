---
name: container-host-ssh
description: "Operar o host via SSH a partir do container Hermes."
version: 1.0.0
author: HAL 9000
platforms: [linux]
metadata:
  hermes:
    tags: [ssh, host, docker, container, operacao, reboot, ed25519]
    category: hermes-ops
---

# Acesso SSH do Container Hermes ao Host

Como dar ao container `hermes-agent` (Docker) capacidade de executar comandos
no **host** via SSH — status/restart dos containers, reboot do host — sem
senha e com segurança (chave fora do backup, sudo mínimo).

## Quando Ativar

- O container não tem docker.sock e o usuário quer que o agente reinicie docker/host
- Precisar rodar comandos no host a partir do container (diagnóstico, manutenção)
- Configurar chave SSH ed25519 para acesso automatizado (sem passphrase)

> ⚠️ **Escopo mínimo (desde ago/2026):** o host é uma **VM** e o acesso do agente a ele é
> **só para docker/reboot**. Para ler/editar OPS e KB **NÃO usar ssh** — o container
> `hermes-webui` monta `hermes-data` em `/opt/data/hermes-data` (patch no docker-compose,
> ago/2026) e enxerga `hermes_mpt_ops`/`hermes_mpt_kb` **diretamente**. O WebUI roda o
> agente localmente (não é só frontend); o `hermes-agent` roda o gateway (Telegram).
> Ambos compartilham o estado via bind `~/.hermes`.

## Topologia

```
┌─ CONTAINER hermes-agent ──────────┐      ┌─ HOST ──────────────────────┐
│  chave privada + config SSH       │ SSH  │  authorized_keys + sudoers  │
│  ssh host → <gateway>:22          │─────▶│  usuário no grupo docker    │
└───────────────────────────────────┘      └─────────────────────────────┘
```

- O container alcança o host pelo **gateway da rede Docker**: `ip route | grep default`
  (ex: `172.19.0.1`). Testar: `ssh -o ConnectTimeout=4 172.19.0.1 "echo ok"`.

## ⚠️ Descoberta crítica: HOME do SSH ≠ HOME do shell

O processo SSH do agente usa **`/opt/data` como HOME** (cwd padrão do agente),
NÃO `$HOME` do shell (`/home/hermes/.hermes/home`). Consequências:

- `ssh -G host` mostra `identityfile ~/.ssh/id_rsa` → resolve para `/opt/data/.ssh/`
- **O config em `~/.ssh/config` do shell NÃO é lido pelo ssh do agente**
- **O config que vale é `/opt/data/.ssh/config`** (com `IdentityFile` apontando
  para o caminho real ou um symlink)
- Diagnosticar com: `ssh -v 172.19.0.1 "echo x" 2>&1 | grep -i "identity file"`

## Passo a Passo

### 1. Criar a chave (no container)

```bash
mkdir -p /home/hermes/.hermes/home/.ssh && chmod 700 /home/hermes/.hermes/home/.ssh
ssh-keygen -t ed25519 -f /home/hermes/.hermes/home/.ssh/hermes_host_key \
  -N "" -C "hermes-agent-container@$(hostname)"
chmod 600 /home/hermes/.hermes/home/.ssh/hermes_host_key
chmod 644 /home/hermes/.hermes/home/.ssh/hermes_host_key.pub
```

Local persistente (`~/.hermes` é volume) + **fora de qualquer repo git**.

### 2. Config no HOME real do ssh (`/opt/data/.ssh/`)

```bash
mkdir -p /opt/data/.ssh && chmod 700 /opt/data/.ssh
ln -sf /home/hermes/.hermes/home/.ssh/hermes_host_key /opt/data/.ssh/hermes_host_key
ln -sf /home/hermes/.hermes/home/.ssh/hermes_host_key.pub /opt/data/.ssh/hermes_host_key.pub
cat > /opt/data/.ssh/config << 'EOF'
Host host
    HostName 172.19.0.1          # ← gateway (ver topologia)
    User hermes                  # ← usuário do host
    IdentityFile /opt/data/.ssh/hermes_host_key
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
EOF
chmod 600 /opt/data/.ssh/config
```

### 3. Autorizar a chave pública no host (MANUAL — usuário)

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
echo "<CHAVE_PUBLICA>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 4. Sudo NOPASSWD mínimo (MANUAL — usuário, via visudo)

```bash
sudo visudo -f /etc/sudoers.d/hermes-reboot
# conteúdo:
# hermes ALL=(ALL) NOPASSWD: /sbin/reboot, /usr/sbin/reboot, /bin/systemctl reboot
```

⚠️ Sempre `visudo` (valida sintaxe). Liberar **apenas** o que for necessário
(princípio do menor privilégio) — nunca `ALL` genérico.

### 5. Proteger a chave do backup

No `hermes-backup.py`, `EXCLUDE_PATTERNS` deve conter `".ssh/"` (chave privada
NUNCA vai para o Google Drive). Já existe em `home/` mas adicionar `.ssh/`
explícito como defesa em profundidade.

### 6. Validar

```bash
ssh -o BatchMode=yes host 'hostname; whoami'      # hermes-01 / hermes
ssh host 'docker compose ps'                       # sem sudo (grupo docker)
ssh host 'sudo -n /sbin/reboot --help >/dev/null && echo OK'  # reboot NOPASSWD
```

## Scripts de operação (padrão usado)

No repo `hermes_mpt_ops/scripts/`, 3 scripts que encapsulam `ssh host`:

| Script | Função | Confirmação |
|--------|--------|-------------|
| `host-status.sh` | status docker + containers + recursos + health | — |
| `host-restart.sh` | `docker compose restart` + health check | pede s/N |
| `host-reboot.sh` | `sudo reboot` + wait + verificação | pede "REINICIAR" |

Padrões dos scripts:
- Alias `host` + `COMPOSE_DIR` via env com default
- `--force` pula a confirmação; `read -r -p` pede confirmação explícita
- Reboot pede **palavra-chave** (ex: "REINICIAR"), não só s/N
- Após reboot: loop de `ssh host 'echo up'` até voltar (até ~3 min) + health check
- **Escaping de awk dentro de ssh**: usar `awk '\''{print $3}'\''` (quotes aninhados)

## Pitfalls

- ⚠️ **Container WebUI (hermeswebui)**: não existe `/opt/data/.ssh` — o config está em
  `$HOME/.ssh/config` (`/home/hermeswebui/.hermes/home/.ssh/`), mas o ssh resolve `~`
  pelo passwd (`/home/hermeswebui/.ssh`, vazio) e **ignora o config**. Usar SEMPRE:
  `ssh -F /home/hermeswebui/.hermes/home/.ssh/config -i /home/hermeswebui/.hermes/home/.ssh/hermes_host_key host '...'`
  (funciona: user hermes, host 172.19.0.1). Não depende de alias nem de HOME.
- ⚠️ **`whois` pode não existir** no container — para checar disponibilidade de
  domínio usar RDAP: `curl -s https://rdap.org/domain/<nome>` → 404 = disponível
- ⚠️ **Escaping duplo** em `ssh host 'cmd com $var e awk'`: o `$` local expande
  ANTES do ssh — usar aspas simples externas e `'\''` para aspas internas
- ⚠️ **`docker compose` path no host** pode diferir do container — confirmar com
  `ssh host 'ls ~/hermes-data/hermes_mpt_ops/docker/docker-compose.yml'`
- ⚠️ Se a chave for **regenerada**, a pública muda → repetir o passo 3 no host
- ⚠️ Firewall do host: se `ssh 172.19.0.1` falhar com timeout, verificar
  `ufw`/`iptables` no host (a porta 22 do host precisa aceitar da rede docker)
- ⚠️ **Subnet da rede docker MUDA quando o compose recria a rede** (aconteceu
  06/08/2026: gateway `172.19.0.1` → `172.20.0.1` após `docker compose up -d`
  a partir de novo diretório). Sintoma: `ssh host` falha com *Connection timed out*
  (não é firewall — o HostName fixo no config está obsoleto). **Diagnóstico:**
  descobrir o gateway atual com `ip route` no container; testar candidatos com
  `for ip in 172.17.0.1 172.18.0.1 172.19.0.1 172.20.0.1; do timeout 3 bash -c "echo > /dev/tcp/$ip/22" 2>/dev/null && echo "$ip ABERTO"; done`.
  **Fix:** atualizar o `HostName` no config (e nos exemplos acima — `172.19.0.1`
  é ilustrativo, NÃO fixo). **Prevenção:** fixar o subnet da rede no compose
  (`networks: hermes-net: ipam: config: - subnet: 172.20.0.0/16`) para o gateway
  não flutuar entre `up`s.
- ⚠️ **WebUI container: o ssh usa o config do host atual** — no WebUI, o caminho
  que funciona é `-F /home/hermeswebui/.hermes/home/.ssh/config -i .../hermes_host_key`
  (ver pitfall acima); após mudança de subnet, atualizar TAMBÉM esse config
  (o `HostName` nele aponta para o gateway antigo).

## Referências

- Runbook completo (refazer do zero): `hermes_mpt_ops/docs/RUNBOOK-SSH-HOST.md`
- Scripts de operação: `hermes_mpt_ops/scripts/host-{status,restart,reboot}.sh`
- Wiki: `referencias/cron-scripts-hermes.md` (padrão wrapper — relacionado)
