# RUNBOOK — Recuperação de Desastre do Ambiente Hermes

**Objetivo:** reativar o ambiente completo (Hermes Agent + Gateway + WebUI + Dashboard + Telegram + backups)
em um host novo, quando a VM atual falhar.

**Princípio:** `git` + `backup do Google Drive` cobrem 100% do ambiente.
- `hermes_mpt_ops` (este repo) → engenharia (scripts, bancos)
- `hermes_mpt_kb` → conhecimento (wiki)
- **Backup do Drive** → identidade (config, memória, tokens, sessões)

> ⚠️ **Modelo atual (desde 07/08/2026): VM nativa** — SEM Docker, SEM Tailscale.
> O agente roda como user service do systemd; a WebUI como daemon próprio; o acesso
> remoto via Cloudflare Tunnel. Este runbook reflete esse modelo. O fluxo antigo
> (containers) ficou no histórico dos commits.

**Tempo estimado:** 1-2 horas (a maior parte é download/instalação).

---

## FASE 0 — Pré-requisitos

| Item | Onde obter |
|------|-----------|
| Acesso ao GitHub (token) | Repositórios privados `aspadeto/hermes_mpt_ops` e `aspadeto/hermes_mpt_kb` |
| Acesso ao Google Drive | Pasta `HermesBackup` (backups diários) |
| Conta Cloudflare | Dashboard com o **token do tunnel** (não migra em backup) |
| Conta no Telegram | O bot precisa do token (ver Fase 4) |

---

## FASE 1 — Instalar base no host novo

```bash
# 1.1 Ferramentas (Ubuntu 24.04)
sudo apt update && sudo apt install -y git curl python3-venv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 1.2 Cloudflared (túnel) — binário oficial
curl -sL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
sudo install -m755 cloudflared /usr/local/bin/cloudflared

# 1.3 (Opcional) Email via Himalaya — binário pré-compilado (não existe no apt/snap)
curl -sL https://github.com/pimalaya/himalaya/releases/download/v2.0.0/himalaya.x86_64-linux.tgz -o h.tgz
tar xzf h.tgz && install -m755 himalaya ~/.local/bin/himalaya
```

---

## FASE 2 — Clonar repositórios

```bash
# 2.1 Token GitHub (ver "Segredos" abaixo para criar)
export GITHUB_TOKEN=$(cat GITHUB_TOKEN.txt)  # ou cole o token

# 2.2 Clonar
mkdir -p /opt/data && cd /opt/data
git clone https://github.com/aspadeto/hermes_mpt_ops.git
git clone https://github.com/aspadeto/hermes_mpt_kb.git
mv hermes_mpt_ops hermes-data && mv hermes_mpt_kb hermes-data/  # layout final: /opt/data/hermes-data/{hermes_mpt_ops,hermes_mpt_kb}
```

> Layout de referência: `/opt/data/hermes-data/` contém `hermes_mpt_kb/`,
> `hermes_mpt_ops/`, `hermes-webui/workspace/` (balcão da WebUI), `.tool-venv/`,
> `.google-venv/`.

```bash
# 2.3 Credencial git (push automático do cron)
mkdir -p /home/hermes
git config --global credential.helper "store --file=/home/hermes/.git-credentials"
# O .git-credentials é criado no primeiro push autenticado
```

---

## FASE 3 — Restaurar identidade (backup do Drive)

**Este passo é o mais importante** — sem ele, o Hermes sobe mas sem
configuração, memória, skills personalizadas nem credenciais de providers.

```bash
# 3.1 Baixar o backup mais recente da pasta HermesBackup no Google Drive
#     (manual: https://drive.google.com — pasta "HermesBackup")

# 3.2 Extrair
mkdir -p ~/restore && cd ~/restore
tar xzf hermes-backup-*.tar.gz

# 3.3 Restaurar ~/.hermes (config, memória, skills, tokens)
#     CUIDADO: o tar preserva estrutura aninhada (.hermes/home/...) — usar --strip-components
cp -a restore/.hermes ~/.hermes

# 3.4 Restaurar tokens e credenciais (fora do hermes-data, por segurança)
cp -a restore/.../GITHUB_TOKEN.txt /home/hermes/GITHUB_TOKEN.txt
cp -a restore/.../.git-credentials /home/hermes/.git-credentials
chmod 600 /home/hermes/GITHUB_TOKEN.txt /home/hermes/.git-credentials

# 3.5 Config do email (Himalaya) — caminhos ajustados da migração
mkdir -p ~/.config/himalaya
cp -a restore/.../.config/himalaya/* ~/.config/himalaya/   # config.toml + get-password.sh + .gmail-app-password
chmod 700 ~/.config/himalaya/get-password.sh
```

> ⚠️ **Pitfalls conhecidos da restauração:** (1) `tar` com glob `*` não pega ocultos —
> usar `--strip-components` ou mover explícito; (2) `sed -i` em `get-password.sh`
> remove o bit de execução — refazer `chmod 700`; (3) venvs com symlink de python
> quebrado → recriar com `uv --clear`.

---

## FASE 4 — Configurar segredos

Não há mais `.env` de Docker. Os segredos vivem em arquivos locais:

| Arquivo | Conteúdo |
|---------|----------|
| `~/.hermes/.env` | `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USERS`, `TELEGRAM_HOME_CHANNEL`, `OPENROUTER_API_KEY`, `HERMES_DASHBOARD_SESSION_TOKEN` |
| `~/hermes-webui/.env` | `HERMES_WEBUI_HOST=127.0.0.1`, `HERMES_WEBUI_PORT=8787`, `HERMES_WEBUI_PASSWORD=<senha>` |
| `~/.hermes/auth.json` | credenciais Nous (restauradas no backup) |
| `~/.hermes/config.yaml` | `dashboard.basic_auth` (username, password_hash, secret) — ver seção de segredos |

```bash
# Exemplo do ~/.hermes/.env
cat >> ~/.hermes/.env << 'EOF'
TELEGRAM_BOT_TOKEN=...
TELEGRAM_ALLOWED_USERS=...
TELEGRAM_HOME_CHANNEL=...
OPENROUTER_API_KEY=...
EOF
chmod 600 ~/.hermes/.env
```

---

## FASE 5 — Subir o ambiente

```bash
# 5.1 Gateway (user service — Telegram + API)
systemctl --user enable --now hermes-gateway.service

# 5.2 WebUI (daemon próprio do hermes-webui)
cd ~/hermes-webui && ./ctl.sh start

# 5.3 Dashboard (user service — novo Web UI SPA, porta 9119)
systemctl --user enable --now hermes-dashboard.service

# 5.4 Túnel Cloudflare (serviço de sistema, root)
#     Token obtido no dashboard (Cloudflare → Zero Trust → Tunnels → seu tunnel)
sudo mkdir -p /etc/cloudflared
sudo tee /etc/cloudflared/token > /dev/null << 'EOF'
<token-do-dashboard>
EOF
sudo systemctl enable --now cloudflared

# Verificar
systemctl --user status hermes-gateway.service
~/hermes-webui/ctl.sh status
systemctl --user status hermes-dashboard.service
curl -s http://127.0.0.1:8787 -o /dev/null -w "%{http_code}"   # espera 302 (login)
curl -s http://127.0.0.1:9119 -o /dev/null -w "%{http_code}"   # espera 200
```

---

## FASE 6 — Restaurar conectividade

```bash
# 6.1 O túnel já mapeia os hostnames → serviços locais:
#     https://webui-01.asideia.net        →  http://localhost:8787
#     https://dashboard-01.asideia.net    →  http://localhost:9119
#     (conferir o ingress no dashboard; Cloudflare Access na frente)
curl -s https://webui-01.asideia.net -o /dev/null -w "%{http_code}"
curl -s https://dashboard-01.asideia.net -o /dev/null -w "%{http_code}"

# 6.2 SSH
#     porta 22 padrão; usuário hermes. (Tailscale SSH não existe mais.)
```

---

## FASE 7 — Pós-restauração (verificações)

| Check | Comando | Esperado |
|-------|---------|----------|
| WebUI | `curl -s http://127.0.0.1:8787` | 302/200 |
| Dashboard | `curl -s http://127.0.0.1:9119` | 200 |
| WebUI remoto | `curl -s https://webui-01.asideia.net` | login (Access) |
| Dashboard remoto | `curl -s https://dashboard-01.asideia.net` | login (Access) |
| Telegram | enviar mensagem ao bot | responde |
| API | `curl -s http://127.0.0.1:20241/` | responde (404 genérico = vivo) |
| Backup | rodar `hermes_mpt_ops/scripts/hermes-backup.py` | upload OK |
| Pendências | `pendencia.py stats` | mostra banco |
| Repos | `git -C /opt/data/hermes-data/hermes_mpt_kb status` | limpo |
| Cron | `hermes cron list` | jobs ativos |
| Git push | `git -C /opt/data/hermes-data/hermes_mpt_ops ls-remote origin HEAD` | autentica |

---

# SEGREDOS — Como criar/obter cada um

## 1. GITHUB_TOKEN.txt
- **Local:** `/home/hermes/GITHUB_TOKEN.txt` (fora do hermes-data)
- **Como obter:** GitHub → Settings → Developer settings → Personal access tokens → Generate new token
  - Scope: `repo` (acesso a repos privados)
  - Expiração: 1 ano
- **Uso:** autenticação em `git clone`/`git push` dos repos privados
- **Renovação:** lembrete agendado no Hermes (cron) antes de expirar

## 2. .git-credentials
- **Local:** `/home/hermes/.git-credentials` (fora do hermes-data)
- **Como criar:**
  ```bash
  git config --global credential.helper "store --file=/home/hermes/.git-credentials"
  # no primeiro push autenticado, o git grava: https://usuario:TOKEN@github.com
  ```
- **Uso:** push automático (cron) dos repos KB e OPS

## 3. HERMES_WEBUI_PASSWORD (senha do WebUI)
- **Local:** `~/hermes-webui/.env` (linha `HERMES_WEBUI_PASSWORD=`)
- **Como criar:** senha forte própria (ex: gerar com `openssl rand -base64 24`)
- **Uso:** login no WebUI (obrigatória quando exposto além de localhost)
- **⚠️ Importante:** fora do backup do Drive — **guardar em gerenciador de senhas**.
  Sem ela, não há acesso ao WebUI após um desastre.

## 4. HERMES_DASHBOARD_SESSION_TOKEN (token de sessão do dashboard)
- **Local:** `~/.hermes/.env` (linha `HERMES_DASHBOARD_SESSION_TOKEN=`)
- **Como criar:** `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` — token único, forte
- **Uso:** autentica chamadas de API sensíveis (`/api/env/reveal`) no loopback via header
  `X-Hermes-Session-Token`; fixa o token de sessão da app (sem ele, o dashboard gera um
  efêmero a cada restart, invalidando sessões do Hermes Desktop)
- **⚠️ Importante:** fora do backup do Drive — **guardar em gerenciador de senhas**.
  Sem ele, o Hermes Desktop não mantém sessão após reiniciar o serviço.
- **Relacionado — `dashboard.basic_auth` (config.yaml):** `username` + `password_hash`
  (scrypt) + `secret` (HMAC de assinatura de sessão, 32 bytes) + `session_ttl_seconds=43200`.
  Só é exigido quando o bind é **não-loopback** (`0.0.0.0`). No modelo atual
  (loopback via tunnel) o Cloudflare Access é a camada auth externa.

## 5. TELEGRAM_BOT_TOKEN (+ ALLOWED_USERS, HOME_CHANNEL)
- **Local:** `~/.hermes/.env`
- **Como obter:** falar com [@BotFather](https://t.me/BotFather) no Telegram → `/newbot` → copiar o token
- **TELEGRAM_ALLOWED_USERS:** seu user ID (pedir ao @userinfobot ou usar o canal Home)
- **TELEGRAM_HOME_CHANNEL:** ID do canal/chat de entrega
- **Uso:** conexão do Hermes com o Telegram (canal principal de comunicação)
- **⚠️ Se perder:** criar bot novo no BotFather e atualizar o .env (o histórico do Telegram fica com o bot antigo)

## 6. OPENROUTER_API_KEY
- **Local:** `~/.hermes/.env`
- **Como obter:** https://openrouter.ai/keys → Create key
- **Uso:** modelos gratuitos/alternativos via OpenRouter (tarefas leves)

## 7. auth.json (credenciais Nous/OpenAI-compatível)
- **Local:** `~/.hermes/auth.json`
- **Como obter:** rodar `hermes auth login` (fluxo OAuth) ou configurar via `hermes auth`
- **Contém:** access_token, refresh_token, agent_key do provider `nous`
- **⚠️ Importante:** tokens OAuth expiram — o login deve ser refeito periodicamente
- **Backup:** incluído no tar.gz do Drive (restaurado na Fase 3)

## 8. Google Workspace (google_client_secret.json + google_token.json)
- **Local:** `~/.hermes/google_client_secret.json` e `~/.hermes/google_token.json`
- **Como obter:**
  1. Google Cloud Console → criar projeto → habilitar APIs (Drive, Gmail, Calendar, Sheets, Docs)
  2. Criar credencial OAuth Client (Desktop) → baixar `client_secret.json`
  3. Rodar o setup: `uv venv ~/hermes-data/.google-venv && uv pip install --python ~/hermes-data/.google-venv/bin/python google-api-python-client google-auth-oauthlib`
  4. `GSETUP_VENV="$HOME/hermes-data/.google-venv/bin/python $HERMES_HOME/skills/productivity/google-workspace/scripts/setup.py"` + `$GSETUP_VENV --auth-url` → autorizar no navegador → colar código
- **Uso:** backup do Drive, email, calendário, sheets
- **⚠️ Importante:** o token de refresh só pode ser gerado no primeiro fluxo OAuth — guarde o `client_secret.json`

## 9. Email (Himalaya — senha de app Gmail)
- **Local:** `~/.config/himalaya/config.toml` + script `get-password.sh`
- **Como obter:**
  1. Google Account → Security → 2-Step Verification (obrigatório)
  2. App passwords → criar senha de app para "Mail"
  3. Configurar em `~/.config/himalaya/config.toml` (conta `gmail`)
- **Uso:** envio de emails via CLI (Himalaya)

## 10. Cloudflare Tunnel (token do túnel)
- **Não é um arquivo versionável** — é o token gerado no dashboard
- **Como obter:** Cloudflare → Zero Trust → Networks → Tunnels → seu tunnel → token
  (ou recriar o tunnel apontando `webui-01.asideia.net → http://localhost:8787` e
  `dashboard-01.asideia.net → http://localhost:9119`)
- **Local no host:** `/etc/cloudflared/token` (lido pelo serviço `cloudflared.service`)
- **⚠️ Se perder:** recriar no dashboard e reinstalar o token; conferir o ingress
  (hostname → serviço) e o Access

---

# MATRIZ DE SEGREDOS — Resumo rápido

| Segredo | Local | Backup Drive? | Como renovar |
|---------|-------|---------------|--------------|
| GITHUB_TOKEN | `/home/hermes/GITHUB_TOKEN.txt` | ✅ | GitHub → Developer settings |
| .git-credentials | `/home/hermes/.git-credentials` | ✅ | automático no push |
| WEBUI_PASSWORD | `~/hermes-webui/.env` | ❌ (manual) | gerar nova + editar .env + `ctl.sh restart` |
| DASHBOARD_SESSION_TOKEN | `~/.hermes/.env` | ❌ (manual) | `secrets.token_urlsafe(48)` + restart dashboard |
| dashboard.basic_auth.secret | `~/.hermes/config.yaml` | ❌ (manual) | `secrets.token_bytes(32)` + restart dashboard |
| TELEGRAM_* | `~/.hermes/.env` | ✅ | BotFather → /newbot |
| OPENROUTER_KEY | `~/.hermes/.env` | ✅ | openrouter.ai/keys |
| auth.json (Nous) | `~/.hermes/auth.json` | ✅ | `hermes auth login` |
| Google OAuth | `~/.hermes/google_*` | ✅ | Google Cloud Console |
| Himalaya (Gmail) | `~/.config/himalaya/` | ✅ (no tgz) | Google App passwords |
| Cloudflare Tunnel | dashboard + `/etc/cloudflared/token` | ❌ (manual) | dashboard → token |

> **Nota:** no modelo VM nativo **não existe mais** `API_SERVER_KEY` nem `.env` de
> Docker — o WebUI fala com o gateway via localhost (porta interna do processo).
> A raiz do `hermes-data` foi **esvaziada de segredos** — qualquer token novo deve
> ir para `/home/hermes/`, nunca para dentro do `hermes-data`.
