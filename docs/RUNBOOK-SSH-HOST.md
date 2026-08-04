# RUNBOOK — Acesso SSH do Container Hermes ao Host

**Objetivo:** permitir que o container `hermes-agent` execute comandos no host
via SSH (docker restart, reboot do host, status), sem senha e de forma segura.

**Data de criação:** 2026-08-03
**Status:** ✅ Implementado e testado

---

## Visão Geral da Arquitetura

```
┌─ CONTAINER hermes-agent ──────────────┐      ┌─ HOST (hermes-01) ─────────────┐
│  ~/.ssh/hermes_host_key (privada)     │ SSH  │  ~/.ssh/authorized_keys        │
│  ssh host → 172.19.0.1:22             │─────▶│  usuário: hermes (uid 1000)    │
│  /opt/data/.ssh/config (alias)        │      │  grupo docker (sem sudo p/ docker)│
└───────────────────────────────────────┘      │  sudo NOPASSWD: apenas reboot  │
                                               └────────────────────────────────┘
```

**Topologia:** o container alcança o host pelo **gateway da rede Docker**
(`172.19.0.1` — varia conforme a rede; descobrir com `ip route`).

---

## Componentes

| Componente | Local (container) | Observação |
|-----------|-------------------|------------|
| Chave privada (real) | `/home/hermes/.hermes/home/.ssh/hermes_host_key` | Persistente (volume `~/.hermes`), **excluída do backup** |
| Chave pública | `/home/hermes/.hermes/home/.ssh/hermes_host_key.pub` | Vai para `authorized_keys` do host |
| Config SSH (alias) | `/opt/data/.ssh/config` | O ssh usa `/opt/data` como HOME |
| Chave (symlink) | `/opt/data/.ssh/hermes_host_key` → home persistente | Mantém 1 cópia real |
| Chave pública (host) | `/home/hermes/.ssh/authorized_keys` | Autorização |

---

## Passo a Passo (refazer do zero)

### Fase 1 — Criar a chave (no container)

```bash
# 1.1 Criar diretório persistente
mkdir -p /home/hermes/.hermes/home/.ssh
chmod 700 /home/hermes/.hermes/home/.ssh

# 1.2 Gerar a chave ed25519 (sem passphrase — o cron/agente usa sem interação)
ssh-keygen -t ed25519 -f /home/hermes/.hermes/home/.ssh/hermes_host_key \
  -N "" -C "hermes-agent-container@$(hostname)"

# 1.3 Permissões
chmod 600 /home/hermes/.hermes/home/.ssh/hermes_host_key
chmod 644 /home/hermes/.hermes/home/.ssh/hermes_host_key.pub
```

### Fase 2 — Descobrir o gateway do host

```bash
# No container: o gateway da rota padrão É o host
ip route | grep default
# Exemplo: default via 172.19.0.1 dev eth0  → host = 172.19.0.1
```

### Fase 3 — Configurar o alias SSH (no container)

**3a. Config no HOME real do ssh** (`/opt/data/.ssh/config` — porque o ssh usa `/opt/data` como HOME):

```bash
mkdir -p /opt/data/.ssh && chmod 700 /opt/data/.ssh
cat > /opt/data/.ssh/config << 'EOF'
Host host
    HostName 172.19.0.1          # ← IP do gateway (ver Fase 2)
    User hermes                  # ← usuário do host
    IdentityFile /opt/data/.ssh/hermes_host_key
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
EOF
chmod 600 /opt/data/.ssh/config

# Symlink para a chave real (persistente)
ln -sf /home/hermes/.hermes/home/.ssh/hermes_host_key /opt/data/.ssh/hermes_host_key
ln -sf /home/hermes/.hermes/home/.ssh/hermes_host_key.pub /opt/data/.ssh/hermes_host_key.pub
```

**3b. (Opcional) Config no HOME do shell** — para uso manual interativo:

```bash
cat > /home/hermes/.hermes/home/.ssh/config << 'EOF'
Host host
    HostName 172.19.0.1
    User hermes
    IdentityFile ~/.ssh/hermes_host_key
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new
EOF
chmod 600 /home/hermes/.hermes/home/.ssh/config
```

> ⚠️ **Atenção:** o processo SSH do agente usa `/opt/data` como HOME
> (verificado com `ssh -G host`). O config em `~/.ssh` do shell NÃO é lido
> pelo processo do agente — por isso o config em `/opt/data/.ssh` é o que vale.

### Fase 4 — Autorizar a chave no host (MANUAL — no host)

```bash
# 4.1 No host, como usuário hermes
mkdir -p ~/.ssh && chmod 700 ~/.ssh

# 4.2 Adicionar a chave pública (copiar do container)
echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIO4Dc9df2Qrre2tUAQTo5Gs6n8ioGqnuPHpMBX2gDix9 hermes-agent-container@7e0319ce35f2" >> ~/.ssh/authorized_keys

chmod 600 ~/.ssh/authorized_keys
```

> **Se a chave for REGENERADA** (Fase 1), a pública muda — repetir o passo 4.2.

### Fase 5 — Liberar reboot sem senha (MANUAL — no host, via visudo)

```bash
sudo visudo -f /etc/sudoers.d/hermes-reboot
```

Conteúdo:
```
# Container Hermes — reiniciar host sem senha (somente reboot)
hermes ALL=(ALL) NOPASSWD: /sbin/reboot, /usr/sbin/reboot, /bin/systemctl reboot
```

> ⚠️ Usar SEMPRE `visudo` (valida sintaxe). Libera APENAS reboot —
> qualquer outro `sudo` continua exigindo senha.

### Fase 6 — Proteger a chave do backup

No `hermes_mpt_ops/scripts/hermes-backup.py`, garantir que `EXCLUDE_PATTERNS`
contenha `".ssh/"` (já adicionado em 2026-08-03). Verificar:

```bash
grep -n ".ssh" /opt/data/hermes-data/hermes_mpt_ops/scripts/hermes-backup.py
# deve mostrar: ".ssh/",  # chaves privadas — nunca ir para o backup (Drive)
```

---

## Validação (testes)

```bash
# 1. Conexão básica (do container)
ssh -o BatchMode=yes host 'hostname; whoami'
# Esperado: hermes-01 / hermes

# 2. Docker sem sudo
ssh host 'docker compose -f ~/hermes-data/hermes_mpt_ops/docker/docker-compose.yml ps'
# Esperado: listagem dos containers (hermes-agent, hermes-webui)

# 3. Reboot NOPASSWD (não executar de fato — só validar permissão)
ssh host 'sudo -n /sbin/reboot --help >/dev/null 2>&1 && echo OK || echo precisa-senha'
# Esperado: OK

# 4. Fingerprint (para conferir se a chave mudou)
ssh-keygen -lf /home/hermes/.hermes/home/.ssh/hermes_host_key.pub
# Esperado: SHA256:BIOZtm9NLHcW6+Uy4zqW6qYNV1kDsbBKnrdtLyG7/SY
```

---

## Operações disponíveis (após setup)

| Operação | Comando (do container) | Sudo? |
|----------|------------------------|-------|
| Status dos containers | `ssh host 'docker compose ps'` | ❌ |
| Restart docker | `ssh host 'docker compose -f ~/hermes-data/hermes_mpt_ops/docker/docker-compose.yml restart'` | ❌ |
| Logs | `ssh host 'docker compose logs --tail 50'` | ❌ |
| Reboot do host | `ssh host 'sudo /sbin/reboot'` | ✅ (NOPASSWD) |
| Info do host | `ssh host 'uname -a; uptime'` | ❌ |

---

## Segurança

1. **Chave privada NUNCA no backup do Drive** — excluída via `EXCLUDE_PATTERNS`
2. **Chave privada NUNCA em repo git** — vive em `~/.hermes/home/.ssh/` (fora dos repos)
3. **Sudo limitado** — apenas `reboot` (princípio do menor privilégio)
4. **Docker sem sudo** — via grupo `docker` (padrão do host)
5. **Permissões:** chave 600, `.ssh` 700, config 600

## Troubleshooting

| Problema | Causa | Solução |
|----------|-------|---------|
| `Could not resolve hostname host` | config não lido (HOME errado) | Verificar `/opt/data/.ssh/config` |
| `Permission denied (publickey)` | chave não autorizada / mudou | Refazer Fase 4 com a .pub atual |
| `Temporary failure in name resolution` | alias não configurado | Usar IP direto: `ssh 172.19.0.1` |
| Sudo pede senha | sudoers não aplicado | Refazer Fase 5 com visudo |
| Porta 22 fechada | firewall do host | `sudo ufw allow 22/tcp` (ou pela tailnet) |
