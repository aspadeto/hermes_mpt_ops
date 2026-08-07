# Backup & Restauração — VM hermes-01 (Drive)

> **Objetivo:** documentar o que o backup diário cobre, o de-para dos arquivos
> e o procedimento de restauração (DR). Atualizado em 07/08/2026 (VM nativa,
> pós-migração do Docker).

## 1. Como roda

- **Cron:** diário às 03:00 UTC → `~/.hermes/scripts/hermes-backup.py` (wrapper)
- **Script real:** `hermes_mpt_ops/scripts/hermes-backup.py` (versionado)
- **Destino:** Google Drive, pasta **HermesBackup** (ID `1lfeKjyVdiNiDPsPJvWXdy6tvb-gtGTKN`)
- **Rotação:** mantém 7 diários + 1 por semana (os mais antigos são apagados)

## 2. O que está incluso (de-para)

O backup gera `hermes-backup-<data>.tar.gz` com **3 áreas**:

### Área 1 — `~/.hermes` → `.hermes/` (config, skills, memória, tokens)

| Origem (host) | Dentro do tar | O que é |
|---------------|---------------|---------|
| `~/.hermes` | `.hermes/` | config.yaml, memória, skills, cron, sessions, tokens de providers (Nous/OpenRouter), `google_token.json`, `google_client_secret.json`, `webui/` (estado) |

**Excluído de `.hermes/`** (não vai ao Drive): `cache/`, `home/`, `.ssh/` (chaves privadas), `audio_cache/`, `image_cache/`, `logs/`, `sessions/`, `webui/` (dados de sessão), `kanban.db`, `response_store.db`, `state.db`, `verification_evidence.db`, `.skills_prompt_snapshot.json`

### Área 2 — `/opt/data/hermes-data` → `data/` (repos + bancos)

| Origem (host) | Dentro do tar | O que é |
|---------------|---------------|---------|
| `hermes-data/hermes_mpt_ops/data/` | `data/...` | `pendencias.db`, `processos.db`, `regional-orcamento.db`, `auditorias/` |
| `hermes-data/` (demais) | `data/...` | arquivos soltos, backups de segredos etc. |

**Excluído de `data/`:** `.google-venv` (ambiente), `hermes_mpt_kb` + `hermes_mpt_ops` (**repos git — já no GitHub**), `backups/` (alvo da rotação)

### Área 3 — `host-secrets/` (NOVO — ago/2026, pendência #14)

Segredos/config do host **fora** dos 2 diretórios padrão — essenciais para DR:

| Origem (host) | Dentro do tar | O que é |
|---------------|---------------|---------|
| `~/hermes-webui/.env` | `host-secrets/webui.env` | Senha do WebUI (`HERMES_WEBUI_PASSWORD`) |
| `~/.config/himalaya/` | `host-secrets/himalaya/` | Config de email + senha app Gmail (`config.toml`, `get-password.sh`, `.gmail-app-password`) |
| `~/.git-credentials` | `host-secrets/git-credentials` | Credenciais GitHub (push KB/OPS) |
| `~/GITHUB_TOKEN.txt` | `host-secrets/GITHUB_TOKEN.txt` | Token GitHub |

> ⚠️ **Não vai ao backup (de propósito):** chaves SSH privadas (`~/.ssh/`,
> `~/.hermes/home/.ssh/`), token do Cloudflare Tunnel (está **só no dashboard**
> Cloudflare — recriar manualmente). O token do cloudflared vive em
> `/etc/cloudflared/token` e **não migra em backup**.

## 3. Como restaurar (DR)

### Pré-requisitos
- VM Ubuntu nova com `hermes` (UID 1000), `git`, `uv`, `python3`, `cloudflared`
- Último backup baixado do Drive (pasta HermesBackup)

### Passo a passo

```bash
# 1. Extrair o backup (ex: hermes-backup-20260807_192228.tar.gz)
mkdir -p ~/restore && tar xzf hermes-backup-*.tar.gz -C ~/restore
# → cria ~/restore/.hermes, ~/restore/data, ~/restore/host-secrets

# 2. Restaurar ~/.hermes (config, memória, skills, tokens)
cp -a ~/restore/.hermes ~/.hermes

# 3. Restaurar dados (repos: clonar do GitHub — não vêm no backup)
mkdir -p /opt/data/hermes-data
cp -a ~/restore/data/. /opt/data/hermes-data/
git clone https://github.com/aspadeto/hermes_mpt_ops.git /opt/data/hermes-data/hermes_mpt_ops
git clone https://github.com/aspadeto/hermes_mpt_kb.git /opt/data/hermes-data/hermes_mpt_kb

# 4. Restaurar segredos do host (área 3)
mkdir -p ~/.config/himalaya
cp -a ~/restore/host-secrets/himalaya/. ~/.config/himalaya/
chmod 700 ~/.config/himalaya/get-password.sh
chmod 600 ~/.config/himalaya/.gmail-app-password
cp ~/restore/host-secrets/webui.env ~/hermes-webui/.env
cp ~/restore/host-secrets/git-credentials ~/.git-credentials
cp ~/restore/host-secrets/GITHUB_TOKEN.txt ~/GITHUB_TOKEN.txt
chmod 600 ~/.git-credentials ~/GITHUB_TOKEN.txt

# 5. Apontar credential.helper dos repos para o caminho restaurado
git -C /opt/data/hermes-data/hermes_mpt_kb config credential.helper "store --file=/home/hermes/.git-credentials"
git -C /opt/data/hermes-data/hermes_mpt_ops config credential.helper "store --file=/home/hermes/.git-credentials"

# 6. Serviços (systemd --user — sem sudo)
systemctl --user daemon-reload
systemctl --user enable --now hermes-gateway hermes-webui

# 7. Cloudflare Tunnel (token NÃO está no backup — pegar no dashboard)
#    dash.cloudflare.com → Zero Trust → Networks → Tunnels → webui-tunnel → Install and run
sudo cloudflared service install <TOKEN>

# 8. Validar
systemctl --user status hermes-gateway hermes-webui
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8787   # 302 = WebUI ok
git -C /opt/data/hermes-data/hermes_mpt_kb ls-remote origin HEAD  # push/leitura GitHub
python3 /opt/data/hermes-data/hermes_mpt_ops/scripts/pendencia.py stats
```

### Verificação pós-restauração
- [ ] `himalaya envelope list` — email lendo (IMAP)
- [ ] `git push` num repo — GitHub escrevendo
- [ ] `https://webui-01.asideia.net` — túnel + Access + senha
- [ ] Backup diário roda (3h UTC)

## 4. O que NÃO depende do backup (fonte externa)

| Item | Onde obter |
|------|-----------|
| Repos KB/OPS | GitHub `aspadeto/*` (clone) |
| Token Cloudflare Tunnel | Dashboard Cloudflare |
| Senhas app / credenciais do gerenciador | Gerenciador de senhas do usuário |
