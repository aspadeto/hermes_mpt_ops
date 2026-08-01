# RUNBOOK — Recuperação de Desastre do Ambiente Hermes PRT14

**Objetivo:** reativar o ambiente completo (Hermes Agent + WebUI + Telegram + backups)
em um host novo, quando o computador da VM atual falhar.

**Princípio:** `git` + `backup do Google Drive` cobrem 100% do ambiente.
- `dr_mpt_ops` (este repo) → engenharia (scripts, docker, bancos)
- `dr_mpt_kb` → conhecimento (wiki)
- **Backup do Drive** → identidade (config, memória, tokens, sessões)

**Tempo estimado:** 1-2 horas (a maior parte é download/instalação).

---

## FASE 0 — Pré-requisitos

| Item | Onde obter |
|------|-----------|
| Acesso ao GitHub (token) | Repositórios privados `aspadeto/dr_mpt_ops` e `aspadeto/dr_mpt_kb` |
| Acesso ao Google Drive | Pasta `HermesBackup` (backups diários) |
| Conta Tailscale | `as7-hermes-docker` (mesma tailnet) |
| Docker + Docker Compose | Instalar no host novo |
| Conta no Telegram | O bot precisa do token (ver Fase 2) |

---

## FASE 1 — Instalar base no host novo

```bash
# 1.1 Docker (Ubuntu 24.04)
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 1.2 Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up        # autenticar com a mesma conta

# 1.3 Ferramentas
sudo apt install -y git curl python3-venv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## FASE 2 — Clonar repositórios

```bash
# 2.1 Token GitHub (ver "Segredos" abaixo para criar)
export GITHUB_TOKEN=$(cat GITHUB_TOKEN.txt)  # ou cole o token

# 2.2 Clonar
mkdir -p ~/hermes-data && cd ~/hermes-data
git clone https://github.com/aspadeto/dr_mpt_ops.git
git clone https://github.com/aspadeto/dr_mpt_kb.git

# 2.3 Credencial git (para push automático)
git config --global credential.helper "store --file=/opt/data/hermes-data/.git-credentials"
# O arquivo .git-credentials é criado no primeiro push autenticado
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
#     CUIDADO: não sobrescrever skills/repos clonados se preferir
cp -a restore/.hermes ~/.hermes

# 3.4 Restaurar tokens na raiz do hermes-data
cp -a restore/data/GITHUB_TOKEN.txt ~/hermes-data/
cp -a restore/data/.git-credentials ~/hermes-data/
```

---

## FASE 4 — Criar o .env do Docker

```bash
cd ~/hermes-data/dr_mpt_ops/docker
cp .env-default .env
# Editar .env com os valores reais (ver "Segredos" abaixo):
#   - HERMES_WEBUI_PASSWORD
#   - API_SERVER_KEY
nano .env
```

---

## FASE 5 — Subir o ambiente

```bash
cd ~/hermes-data/dr_mpt_ops/docker
docker compose up -d

# Verificar
docker compose ps
curl -s http://localhost:8787 -o /dev/null -w "%{http_code}"   # espera 200
```

---

## FASE 6 — Restaurar conectividade

```bash
# 6.1 Tailscale serve (HTTPS do WebUI)
sudo tailscale serve --bg http://127.0.0.1:8787

# 6.2 Tailscale SSH
sudo tailscale up --ssh

# 6.3 Verificar acesso remoto
#     https://as7-hermes-docker.tail15f7e7.ts.net  → WebUI
#     ssh usuario@as7-hermes-docker                 → SSH
```

---

## FASE 7 — Pós-restauração (verificações)

| Check | Comando | Esperado |
|-------|---------|----------|
| WebUI | `curl -s http://localhost:8787` | 200 |
| Telegram | enviar mensagem ao bot | responde |
| API | `curl -s http://localhost:8642/health` | OK |
| Backup | rodar `~/hermes-data/dr_mpt_ops/scripts/hermes-backup.py` | upload OK |
| Pendências | `pendencia.py stats` | mostra banco |
| Wiki | `git -C ~/hermes-data/dr_mpt_kb status` | limpo |
| Cron | `hermes cron list` | jobs ativos |

---

# SEGREDOS — Como criar/obter cada um

## 1. GITHUB_TOKEN.txt
- **Local:** `~/hermes-data/GITHUB_TOKEN.txt` (raiz, fora do git)
- **Como obter:** GitHub → Settings → Developer settings → Personal access tokens → Generate new token
  - Scope: `repo` (acesso a repos privados)
  - Expiração: 1 ano
- **Uso:** autenticação em `git clone`/`git push` dos repos privados
- **Renovação:** lembrete agendado no Hermes (cron) antes de expirar

## 2. .git-credentials
- **Local:** `~/hermes-data/.git-credentials`
- **Como criar:**
  ```bash
  git config --global credential.helper "store --file=/opt/data/hermes-data/.git-credentials"
  # no primeiro push autenticado, o git grava: https://usuario:TOKEN@github.com
  ```
- **Uso:** push automático (cron) dos repos KB e OPS

## 3. HERMES_WEBUI_PASSWORD (senha do WebUI)
- **Local:** `~/hermes-data/dr_mpt_ops/docker/.env` (linha `HERMES_WEBUI_PASSWORD=`)
- **Como criar:** senha forte própria (ex: gerar com `openssl rand -base64 24`)
- **Uso:** login no WebUI (obrigatória quando exposto além de localhost)
- **⚠️ Importante:** guardar em gerenciador de senhas — sem ela, não há acesso ao WebUI

## 4. API_SERVER_KEY (chave da API do Hermes)
- **Local:** `~/hermes-data/dr_mpt_ops/docker/.env` (linha `API_SERVER_KEY=`)
- **Como criar:** é uma chave local de API — gerar com `openssl rand -hex 32`
- **Uso:** autenticação entre WebUI e Agent (env var interpolada pelo compose)
- **⚠️ Importante:** se trocar, atualizar também onde o WebUI referencia a API

## 5. TELEGRAM_BOT_TOKEN (+ ALLOWED_USERS, HOME_CHANNEL)
- **Local:** `~/.hermes/.env`
- **Como obter:** falar com [@BotFather](https://t.me/BotFather) no Telegram → `/newbot` → copiar o token
- **TELEGRAM_ALLOWED_USERS:** seu user ID (pedir ao @userinfobot ou usar o canal Home)
- **TELEGRAM_HOME_CHANNEL:** ID do canal/chat de entrega (ex: `5019194495`)
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
- **Uso:** envio de emails via CLI (Himalaya) — conta `eusouhal9000@gmail.com`

## 10. Tailscale (identidade da tailnet)
- **Não é um arquivo** — é a conta Tailscale
- **Como obter:** `sudo tailscale up` → login com a mesma conta Google
- **Uso:** acesso remoto (WebUI HTTPS, SSH)
- **⚠️ Se perder a tailnet:** recriar e reaplicar os grants (ver `wiki/referencias/tailscale-acesso-remoto.md`)

---

# MATRIZ DE SEGREDOS — Resumo rápido

| Segredo | Local | Backup Drive? | Como renovar |
|---------|-------|---------------|--------------|
| GITHUB_TOKEN | `hermes-data/GITHUB_TOKEN.txt` | ✅ | GitHub → Developer settings |
| .git-credentials | `hermes-data/.git-credentials` | ✅ | automático no push |
| WEBUI_PASSWORD | `docker/.env` | ❌ (manual) | gerar nova + editar .env |
| API_SERVER_KEY | `docker/.env` | ❌ (manual) | `openssl rand -hex 32` |
| TELEGRAM_BOT_TOKEN | `~/.hermes/.env` | ✅ | BotFather → /newbot |
| OPENROUTER_KEY | `~/.hermes/.env` | ✅ | openrouter.ai/keys |
| auth.json (Nous) | `~/.hermes/auth.json` | ✅ | `hermes auth login` |
| Google OAuth | `~/.hermes/google_*` | ✅ | Google Cloud Console |
| Himalaya (Gmail) | `~/.config/himalaya/` | ✅ (no .hermes? verificar) | Google App passwords |
| Tailscale | conta online | — | `tailscale up` |

> **Nota importante:** os segredos marcados como "❌ (manual)" (WEBUI_PASSWORD e
> API_SERVER_KEY) **não estão no backup** porque vivem no `.env` do docker, que é
> local por design. **Guarde-os em um gerenciador de senhas** (ex: Bitwarden,
> Keepass) — são os únicos 2 que você precisa ter na cabeça/lixeira em caso de desastre.
