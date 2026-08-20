---
name: dr-mpt-ops
description: "Scripts, bancos, pendências, PDF→wiki e cron DR MPT."
version: 1.0.0
author: HAL 9000
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [dr-mpt-ops, scripts, sqlite, pendencias, cron, pdf2wiki, versionamento]
    category: produtividade
---

# DR MPT OPS — Repositório de Operações

Engenharia por trás da base de conhecimento: scripts, bancos SQLite, sistema de pendências, pipeline PDF→wiki e integração com o cron do Hermes.

## Quando Ativar

- Trabalhar com scripts/bancos/configs do ambiente DR MPT
- Converter PDF para a wiki (pipeline pdf2wiki)
- Criar/editar pendência para confirmação do usuário
- Criar/ajustar cron job que executa um script
- Decidir onde guardar um arquivo (KB vs OPS vs segredo)
- Decidir entre **script custom vs servidor MCP** para armazenamento/busca de dados

## Arquitetura de Repositórios

| Repo | Conteúdo | Pasta |
|------|----------|-------|
| `hermes_mpt_kb` | Conhecimento (PGEAs, artigos, referências, processos) | `/opt/data/hermes-data/hermes_mpt_kb` |
| `hermes_mpt_ops` | Engenharia (scripts, bancos, configs versionáveis) | `/opt/data/hermes-data/hermes_mpt_ops` |
| `/workspace` (WebUI) | Balcão de entrada — trânsito temporário, **lavável** | `/opt/data/hermes-data/hermes-webui/workspace` (mesma pasta física vista pelo agent) |

Regra de ouro: **documentos → KB; código/dados → OPS; segredos → em nenhum repo** (ficam na raiz de `hermes-data/`).
**Terceira zona — workspace: NUNCA é repositório.** PDF chega → auditoria roda no workspace → aprovado → migra para KB/OPS → workspace é limpo. Um artefato vive em **um único lugar**. Fluxo completo, convenção de nomes e regras: `hermes_mpt_ops/docs/FLUXO-INGESTAO.md` (PDF → auditoria → KB/OPS → git → limpeza; extração → `pgeas/pgea-XXX/extracao.md` no KB; relatório → `data/auditorias/auditoria-pgea-XXX.md` no OPS; frontmatter YAML obrigatório nas extrações).

### AGENTS.md na raiz do OPS (diretrizes comportamentais)

`hermes_mpt_ops/AGENTS.md` (criado ago/2026, adaptado do CLAUDE.md de Andrej Karpathy)
é a **constituição do ambiente** para agentes: pensar antes de agir, simplicidade,
mudanças cirúrgicas, execução orientada a objetivos, versionamento/integridade,
segurança por padrão — mais as regras do usuário (neutralidade de nomes, não alterar
arquivos em uso sem permissão, discutir antes de mudanças estruturais). **Ler ao
trabalhar no ambiente** — o Hermes injeta `AGENTS.md` do workdir automaticamente em
cron jobs com `workdir`; para o chat, carregar manualmente quando relevante.

### Neutralidade de nomes (preferência do usuário — ago/2026)

**NUNCA usar "PRT14" nem marcas de setor/órgão** em documentação, scripts, nomes de arquivos ou conversa — o ambiente será distribuído para outras regionais/servidores/chefes e deve ser **aderente a qualquer contexto**. Exemplos do que já foi corrigido: "Framework PRT14" → "Framework — Camada de Dados"; `prt14.db` → `regional-orcamento.db`; repos renomeados para `hermes_mpt_*`. Ao criar nome de arquivo/script/seção, perguntar-se: *"esse nome faria sentido em outro setor?"*. Quando o usuário corrigir um nome com marca de setor, renomear o artefato + conteúdo (sed em todo o repo) e registrar a preferência.

Stack de armazenamento (verificado ago/2026): **SEM Redis** — sessões/conversas, pendências e dados orçamentários usam SQLite; config/memória/skills em arquivos `~/.hermes/`; conhecimento em git/Markdown. Não há processo, binário ou container Redis no ambiente; as únicas menções a "redis" no código do Hermes são regras de redação de URLs (`redis://...`) no `redact.py`.

## Onde Mora o Quê

- Scripts versionados (fonte da verdade): `hermes_mpt_ops/scripts/`
- Bancos SQLite versionados: `hermes_mpt_ops/data/` (ex: `pendencias.db`)
- Relatórios de auditoria de extração (PGEA/PDF): `hermes_mpt_ops/data/auditorias/` — dado de operação, NÃO polui o KB (convenção FLUXO-INGESTAO)
- Wrappers para cron: `~/.hermes/scripts/` (NÃO versionados)
- Segredos: **fora** do hermes-data — `/home/hermes/GITHUB_TOKEN.txt`, `/home/hermes/.git-credentials`, `~/.hermes/.env`, `~/hermes-webui/.env`

## Sistema de Pendências

Fluxo assíncrono de confirmação — o usuário NÃO responde em tempo real:

1. Algo precisa de confirmação → `pendencia.py add --titulo "..." --contexto "..." --tipo confirmacao|decisao|revisao --prioridade alta|media|baixa`
2. Cron lembra 3x/dia (9h/14h/18h UTC) via `pendencia-remind.py`
3. Usuário diz **"resolver pendências"** → apresentar uma a uma; resolver com `pendencia.py resolve <id>`

CLI completa (validada em uso): `add` (criar), `list` (ativas), `list --todas` (ativas+resolvidas+canceladas — usar ao conferir quadro completo), `resolve <id>`, `cancel <id>` (usar quando a pendência é contingência futura/não acionável — ex: ação de DR documentada no runbook), `remind` (saída vazia = sem pendências), `stats`.

**Formato do `remind` (dashboard em tabela — desde ago/2026):** `## 📋 Pendências — N aguardando (X 🔴)` + tabela `| # | Prio | Tipo | Assunto |` (emoji 🔴🟡🟢, rótulo do tipo em PT, assunto truncado a 60 chars) + destaque `🔴 **N de prioridade alta** — veja primeiro` + chamada `➡️ Responda **"resolver pendências"**...`. Mapa `PRIO_EMOJI`/`TIPO_LABEL` vive no topo do `pendencia.py` — extensível se surgir tipo novo.

Banco: `/opt/data/hermes-data/hermes_mpt_ops/data/pendencias.db` (versionado).
Documentação: `hermes_mpt_kb/referencias/sistema-pendencias.md`.

## Pipeline PDF → Wiki

Converter 1 PDF por vez:

```bash
cd /opt/data/hermes-data/hermes_mpt_kb && .venv/bin/python3 scripts/pdf2kb.py <arquivo.pdf>
```

(via symlink local no KB; o script real vive em `hermes_mpt_ops/scripts/pdf2kb.py` — renomeado de `pdf2wiki.py` na migração de nomes neutros ago/2026)

Gera `raw/articles/<slug>/` (KB é vault Obsidian na raiz — **não existe subpasta `wiki/`**; o caminho antigo `wiki/raw/articles/` está obsoleto desde a migração) com `artigo.md` + `assets/` + `fonte.pdf` + `indexacao.json`.
**Sempre** apresentar o `indexacao.json` ao usuário (via pendência de confirmação) ANTES de indexar e enriquecer o frontmatter.

⚠️ **Pitfall do `--dest`:** se o destino já é a pasta do slug (ex: `--dest raw/articles/hyde-2022` com `--slug hyde-2022`), o script cria **pasta aninhada** (`hyde-2022/hyde-2022/`). Corrigir movendo os arquivos um nível acima (`mv <slug>/<slug>/* <slug>/ && rmdir <slug>/<slug>`). Para evitar: usar `--dest` SEM o slug (ou sem `--slug` quando `--dest` já é a pasta).

⚠️ **Slug pode vir do nome do arquivo com acento/número grudado** (ex: `ofício-circular-0004162026` a partir de "Ofício Circular 000416.2026.pdf"). Para documentos oficiais (portarias, ofícios), renomear a pasta para slug limpo (`oficio-circular-416-2026`) e atualizar em 3 lugares: `indexacao.json` (campo `slug`), frontmatter do `artigo.md`, e o catálogo `index.md`. **Ao renomear pasta, o git não stagea os deletes da pasta antiga** — usar `git add -A raw/articles/` (não `git add <pasta-nova>` específico) para incluir renames/deletes, senão fica `D` pendente e o push sai incompleto.

⚠️ **Autores de papers arXiv não detectados** pela heurística do pdf2kb — extrair da página 1 do PDF (fitz) e preencher no `indexacao.json` manualmente antes de confirmar.

Heurísticas de detecção: `references/pdf2wiki-ingestion.md`.

## Cron do Hermes — Restrições (pitfall crítico)

O campo `script` de cron job exige:
- **Arquivo real** em `~/.hermes/scripts/` (resolvido por nome)
- **SEM symlinks** apontando para fora (bloqueado: `resolves outside the scripts directory`)
- **SEM argumentos** (ex: `pendencia.py remind` → `Script not found`)

Padrão correto: **wrapper real** em `~/.hermes/scripts/` que executa o código versionado no OPS:
- bash: `exec /opt/data/hermes-data/hermes_mpt_ops/scripts/script.sh "$@"`
- python: `runpy.run_path("/opt/data/.../script.py", run_name="__main__")`
- argumento fixo (ex: remind) → wrapper dedicado que seta `sys.argv` antes do `runpy`

Modelos prontos: `references/cron-wrapper-pattern.md`.

## MCP vs Scripts Custom (preferência do usuário)

Antes de criar um script custom de **armazenamento ou busca de dados** (SQLite, memória, filesystem), avaliar primeiro os **servidores MCP padrão** — o usuário prefere padrões estabelecidos a reinventar a roda:

- Hermes suporta MCP custom: `hermes mcp add <server>` (catálogo curado em `optional-mcps/` tem só 6 — blender, comfy-cloud, figma, linear, n8n, unreal-engine; **nenhum de armazenamento/busca** → usar `hermes mcp add` para os oficiais)
- Servidores oficiais relevantes (modelcontextprotocol/servers):
  - ⚠️ `@modelcontextprotocol/server-sqlite` **foi ARQUIVADO** (E404 no npm, junto com Redis) — os oficiais atuais são só **Filesystem** e **Memory** (knowledge graph). Alternativas mantidas por terceiros: `mcp-server-sqlite-npx` (johnnyoshika, npx), `mcp-server-sqlite` (PyPI), `@berthojoris/mcp-sqlite-server` — **exigem avaliação de supply-chain pelo usuário antes de instalar**
  - `@modelcontextprotocol/server-memory` — knowledge graph persistente (entidades/relações; modelo ≠ wiki markdown). Testado e funciona via npx
  - `@modelcontextprotocol/server-filesystem` — acesso a arquivos com controle de acesso (⚠️ Hermes já tem tools nativas de arquivo — avaliar redundância)
  - `mcp-server-git` — operações git
- **Onde MCP NÃO substitui script:** processamento de domínio (ex: `pdf2wiki.py` — lógica MPT de extração/frontmatter) e automação específica do fluxo (auto-commit, backup). MCP não adiciona valor aí.
- **Custo real:** cada MCP é um processo stdio externo (recursos + manutenção) e suas tools entram no contexto (tokens). Para 1 usuário, tool nativa que resolve ≠ MCP.
- **Avaliados e REJEITADOS (ago/2026, pendências #8/#9):** `BrowserMCP` (MCP server + extensão Chrome p/ controlar browser real — Hermes já tem browser tools nativas; topologia container headless incompatível; repo ~1 ano sem commits) e `MCP-Toolbox` do Google (é MCP para **bancos de dados** — PostgreSQL/BigQuery — não browser; overkill p/ stack SQLite local). Não reabrir sem necessidade nova.

## Arquitetura Atual (VM nativa — Docker removido em 07/08/2026)

**MUDANÇA ESTRUTURAL (07/08/2026, feita pelo usuário):** o ambiente saiu de Docker
Compose (2 containers) para **VM nativa** (`hermes-01`, Ubuntu 24.04). Não há
daemon/socket docker no host nem Tailscale. Fatos verificados pós-migração:

| Componente | Como roda | Gestão |
|-----------|-----------|--------|
| Gateway (Telegram + API interna :20241) | user service `hermes-gateway.service` (venv `~/.hermes/hermes-agent`, ExecStart `python -m hermes_cli.main gateway run`) | `systemctl --user status/restart` |
| WebUI (:8787, só 127.0.0.1) | user service `hermes-webui.service` (`~/hermes-webui/start.sh` → `server.py`; unit em `~/.config/systemd/user/`; senha em `~/hermes-webui/.env`) | `systemctl --user status/restart hermes-webui` |
| Túnel Cloudflare | system service `cloudflared.service` (root; token `/etc/cloudflared/token`) | `sudo systemctl`; hostname `webui-01.asideia.net` |
| Cron do Hermes | scheduler dentro do gateway | `hermes cron list` |

- `/opt/data/hermes-data` é **diretório real** na VM (não bind mount).
- Segredos **fora** do hermes-data: `/home/hermes/GITHUB_TOKEN.txt`,
  `/home/hermes/.git-credentials`, `~/.hermes/.env` (Telegram/OpenRouter),
  `~/hermes-webui/.env` (WEBUI_PASSWORD). A raiz do hermes-data está limpa.
- ⚠️ `browser.cdp_url` foi **zerado** (`''`) em 07/08/2026 (pendência #13): o
  valor antigo `ws://browser:3000/` apontava para o container browserless
  **removido** e quebrava as ferramentas de browser. Estado atual:
  `cloud_provider: browser-use` + `use_gateway: true` (**Nous Tool Gateway** —
  browser cloud via assinatura, sem chave direta) com
  `auto_local_for_private_urls: True` → URLs públicas vão ao cloud, URLs
  LAN/localhost usam Chromium local (VM Ubuntu 24.04 com AppArmor userns=1 faz
  o Hermes auto-injetar `--no-sandbox`). Conferir rota com `hermes portal
  info`. Ver skill `browser-infrastructure` p/ diagnóstico e configuração.
- Runbooks: `hermes_mpt_ops/docs/RUNBOOK-MANUTENCAO-VM.md` (dia a dia),
  `RUNBOOK-RECUPERACAO.md` (host novo), `RUNBOOK-SSH-HOST.md` (OBSOLETO).

### Histórico: Docker (removido)

O compose sanitizado continua versionado em `hermes_mpt_ops/docker/` (template
`${VAR:-default}` + `.env-default`) apenas como **registro** — NÃO usar em
operações atuais. As lições seguem válidas: nunca versionar segredos; `.env`
real com chmod 600; backup de valores antes de sanitizar; conferir
`git diff --cached | grep -iE 'token|password|secret'` antes de commitar.

### Backup exclui repos git

`hermes-backup.py` usa `DATA_EXCLUDE = {".google-venv", "hermes_mpt_kb", "hermes_mpt_ops", "backups"}` — repos git são redundantes no tar.gz (já no GitHub). Reduziu backup de ~154MB → ~94MB. Ao criar repo git novo em `hermes-data/`, incluir na exclusão.

**`EXTRA_SECRETS` (host-secrets/ — desde 07/08/2026):** o backup também inclui
segredos do host fora dos 2 diretórios padrão, em `host-secrets/` dentro do
tar.gz: `~/hermes-webui/.env` (senha WebUI), `~/.config/himalaya/` (config
email + senha app), `~/.git-credentials` e `~/GITHUB_TOKEN.txt` (push GitHub).
**NÃO vai ao backup (de propósito):** chaves SSH (`~/.ssh/`, `~/.hermes/home/.ssh/`)
e o token do Cloudflare Tunnel (`/etc/cloudflared/token` — SÓ no dashboard CF,
recriar manualmente em DR). Doc completo com de-para + restauração passo a
passo: `hermes_mpt_ops/docs/BACKUP-RESTAURACAO.md`.

### Pós-migração / restauração em host novo (validado 07/08/2026)

Migração Docker → VM nativa quebrou silenciosamente: credential.helper dos repos
apontando para caminho do container, `user.name` errado no KB, venvs com symlink de
python quebrado, himalaya ausente (não existe no apt/snap Ubuntu), token Google
revogado, e exposição de segredos ao montar a raiz do hermes-data. **Checklist
completo de verificação e correção: `references/pos-migracao-checklist.md`** —
rodar em qualquer host novo antes de reativar cron/backup. Resumo dos pontos:
(1) repos + `git ls-remote` autenticando, (2) `user.name` por repo, (3) venvs
recriados com `uv --clear`, (4) himalaya via GitHub release + config do tgz com
caminhos ajustados, (5) token Google via `setup.py --auth-url/--auth-code`,
(6) mounts seletivos do hermes-data (nunca a raiz — expõe segredos).

## Pitfalls

- **write_file segue symlink e sobrescreve o arquivo REAL**: se o destino é symlink para código versionado, write_file grava POR DENTRO do symlink (clobber). Conferir com `ls -la` antes de escrever; para destinos suspeitos, escrever em `/opt/data/` e `cp` via terminal.
- **Env vars antigas viciadas**: `KB_PATH=/opt/data/wiki` (pré-migração) sobrescrevia o default do script de auto-commit. Usar caminhos absolutos fixos nos scripts, não `${VAR:-default}` quando o env pode estar obsoleto.
- **Repo novo precisa de identidade git**: `git config user.name "Aloisio Spadeto"` e `user.email aspadeto@gmail.com` (local) antes do primeiro commit — senão `Author identity unknown`.
- **Auto-commit cobre os DOIS repos**: `hermes_mpt_ops/scripts/kb-auto-commit.sh` (renomeado de `wiki-auto-commit.sh` na migração) itera KB + OPS; tratar repo sem remote (commit local apenas).
- **Auto-commit race no OPS também**: o sync de 10min commita alterações do OPS (ex: `regional-orcamento.db` novo, edições em scripts) antes do commit manual — `git commit` manual pode acusar "nothing to commit" ou pouquíssimas linhas; verificar com `git log --oneline -3` antes de supor erro.
- **Banco de dados versionado**: `pendencias.db` é exceção no `.gitignore` do KB via `!data/...` — migrou para OPS; demais `*.db` seguem ignorados até decisão.
- **`HERMES_WORKSPACE` é variável de override do template**, não do sistema: no
  modelo VM atual o workspace da WebUI é `HERMES_WEBUI_DEFAULT_WORKSPACE=/opt/data/hermes-data`
  (abre na base do Telegram). Boa prática oficial: workspace em pasta **dedicada** no host (fora de `~/.hermes`).
- **Antes de sanitizar/versionar arquivo de config, perguntar se é o original em uso**: docker-compose/.env originais do host NÃO devem ser alterados sem permissão explícita — o usuário pode movê-los de volta. Sanitizar só cópias/templates, nunca o arquivo vivo.
- **Duplicação de scripts entre pastas**: ao consolidar scripts em `hermes_mpt_ops/scripts/`, conferir duplicatas em `bin/` (ex: `update_hermes-agente-src.sh` existia nos dois, idênticos). Padronizar em `scripts/`, remover o outro (`git rm`). Conferir com `git ls-files | grep <nome>` antes de assumir que só existe um.
- **Symlinks do KB podem apontar para o nome ANTIGO do repo**: após a migração `dr_mpt_ops` → `hermes_mpt_ops`, os symlinks de `hermes_mpt_kb/scripts/` ficaram quebrados (`readlink` mostra `/opt/data/hermes-data/dr_mpt_ops/...`, que não existe — `pdf2wiki.py` também virou `pdf2kb.py`). Sintoma: `scripts/pdf2kb.py` não abre. Corrigir com `rm` + `ln -s` para o caminho novo do OPS (conferir o nome atual do script antes).
- **Validar segredos no histórico ANTES de confiar**: `git rev-list --all | while read c; do git grep -lE 'padrão-secreto' $c; done` (vazio = limpo) e `git show <commit>:<arquivo> | grep -c` para confirmar que placeholder (não valor real) foi commitado — o auto-commit de 10min pode ter corrido entre sanitização e commit manual.
- **Migração de ambiente (container↔VM/host novo): pausar os cron jobs ANTES**
  (07/08/2026): ao mover o hermes-data, o auto-commit (10min) e o backup (3h)
  rodam com caminhos antigos e falham (`last_status: error`) — pausar com
  `cronjob action=pause` em TODOS os jobs antes da migração; reativar só após
  validar. **Checklist pós-migração:** (1) repos no caminho esperado + `git
  status` limpo; (2) `git ls-remote origin HEAD` autentica? (3) identidade git
  por repo (`git config user.name/email` — o KB já teve `user.name=user.email`
  corrompido); (4) binários externos que NÃO migram com backup (ex: `himalaya`
  — reinstallar + recriar `~/.config/himalaya/`); (5) tokens de serviço no
  lugar (`google_token.json`).
- **`credential.helper` LOCAL dos repos usa caminho ABSOLUTO**: os repos têm
  `git config credential.helper "store --file=/opt/data/hermes-data/.git-credentials"`
  (config local). Mover o hermes-data (migração) sem atualizar o helper quebra
  o push — sintoma: `git ls-remote origin HEAD` → `could not read Username for
  'https://github.com'` (pede credencial interativa). Fix: apontar o helper
  para o novo local do `.git-credentials` (ex: `/home/hermes/.git-credentials`)
  ou usar `--global`. Conferir em AMBOS os repos (KB e OPS têm helper local).
- **Email (himalaya) pós-migração — v2.0.0 e Ubuntu** (07/08/2026): o himalaya
  **NÃO existe no apt nem no snap do Ubuntu 24.04** (`apt-cache search` e
  `snap find` vazios — é distribuído como binário pré-compilado no GitHub).
  Instalar: `curl -sL https://github.com/pimalaya/himalaya/releases/download/v2.0.0/himalaya.x86_64-linux.tgz`
  → extrair → `cp himalaya ~/.local/bin/` (ELF estático musl, sem deps).
  ⚠️ **CLI mudou na v2.0.0**: `himalaya template send` NÃO existe mais (a skill
  `himalaya` da comunidade ainda documenta a sintaxe antiga). Envio de teste:
  ```bash
  cat << 'EOF' | himalaya smtp send --mail-from X@gmail.com --rcpt-to X@gmail.com
  From: X@gmail.com
  To: X@gmail.com
  Subject: teste

  corpo
  EOF
  ```
  (ou `himalaya message compose` + `message send`). IMAP não mudou:
  `himalaya envelope list`. Config/credenciais restauram do tgz do backup em
  `~/.config/himalaya/{config.toml,get-password.sh,.gmail-app-password}`
  (ajustar caminhos `/home/hermes/.hermes/home/...` → `/home/hermes/.config/...`).
- **Extrair arquivos do tgz: glob `*` NÃO pega ocultos + `sed -i` perde bit de
  execução** (07/08/2026): ao extrair `tar -xzf backup.tgz .hermes/home/.config/...`,
  o tar preserva a estrutura aninhada (`.hermes/home/...`) e o `mv .hermes/.../* .`
  deixa de fora arquivos ocultos (ex: `.gmail-app-password` — quase perdido no
  `rm -rf .hermes` seguinte; o tgz é imutável, deu para re-extrair). Depois,
  `sed -i` em `get-password.sh` reescreve o arquivo e **remove o bit de
  execução** → himalaya falha com "Permission denied" no password.command até
  `chmod 700 get-password.sh`. Lições: (1) mover ocultos explicitamente ou usar
  `tar --strip-components`; (2) após editar scripts com `sed -i`, refazer o
  chmod; (3) `write_file` recusa `.ssh/` (protegido) — usar terminal `cat >`.

## Ingestão de Vídeo → KB (YouTube + local/TikTok)

Quando o usuário compartilhar um vídeo (ex: framework RAG, TikTok) para guardar na base, o fluxo depende da origem:

### Caso A — YouTube com transcrição

1. **Transcrição** (skill `youtube-content`, venv `.tool-venv` em `/opt/data/hermes-data`):
   ```bash
   # PRIMEIRO tenta sem --language; se "No transcript found", tenta --language pt
   # (vídeos BR frequentemente SÓ têm legenda pt, não en)
   /opt/data/hermes-data/.tool-venv/bin/python \
     ~/.hermes/skills/media/youtube-content/scripts/fetch_transcript.py \
     "URL" --text-only --language pt
   ```
2. **Salvar** em `hermes_mpt_kb/raw/videos/<slug>-transcript.txt`
3. **Resumo estruturado** em `raw/videos/<slug>-resumo.md` (ideia central, framework/passos, tabela de técnicas, "lições para nós")
4. Commit + push (auto-commit cobre)
5. Papers/artigos citados no vídeo → baixar do arXiv e converter via pipeline `pdf2kb` (ver skill `ingestao-pdf-wiki`; pitfall: autores de papers arXiv não são detectados pela heurística — extrair da página 1)

### Caso B — vídeo local / TikTok / YouTube sem transcrição

Quando o vídeo é um **arquivo local** (anexo Telegram/TikTok) ou o YouTube não tem legenda (`{"error": "No transcript found"}` em todas as línguas), transcrever via **STT do próprio Hermes** (Whisper — provider configurado em `config.yaml` → `stt:`):

```bash
# 1. Inspecionar o vídeo
ffprobe -v quiet -print_format json -show_format -show_streams <video.mp4>

# 2. Extrair áudio (mono 16kHz — padrão Whisper)
ffmpeg -y -v quiet -i <video.mp4> -ar 16000 -ac 1 /tmp/audio.wav

# 3. Transcrever com o STT do Hermes
#    ⚠️ usar o python do VENV do Hermes (/opt/hermes/.venv), não o python3 do sistema
/home/hermes/.hermes/hermes-agent/venv/bin/python -c "
import sys; sys.path.insert(0, '/home/hermes/.hermes/hermes-agent')
from tools.transcription_tools import transcribe_audio
r = transcribe_audio('/tmp/audio.wav')
print(r.get('success'), r.get('transcript'), r.get('error'))"
```

Depois: seguir os passos 2-5 do Caso A (salvar transcrição, resumo, commit, papers citados).

## Administração da VM (modelo nativo — sem containers)

O agente roda **na própria VM** — o padrão antigo `ssh host "docker ..."`
(container → host) é OBSOLETO. Operações do dia a dia:

```bash
systemctl --user status hermes-gateway.service    # gateway (Telegram/API)
journalctl --user -u hermes-gateway --no-pager -n 100
systemctl --user restart hermes-gateway.service
systemctl --user status/restart hermes-webui       # WebUI (porta 8787)
journalctl --user -u hermes-webui -f               # logs do WebUI
systemctl status cloudflared                      # túnel (root)
```

- **WebUI = systemd --user** desde 07/08/2026 (unit `~/.config/systemd/user/hermes-webui.service`,
  mesmo padrão do gateway, Linger=yes → sobrevive a logout/reboot, **sem sudo**).
  O antigo daemon via `ctl.sh` foi descontinuado (ctl.sh ainda funciona, mas o
  systemd é o caminho oficial). ⚠️ Senha do WebUI fica em `~/hermes-webui/.env`
  (`HERMES_WEBUI_PASSWORD`), carregada **no start** — editar exige
  `systemctl --user restart hermes-webui`.

- **Portas:** 22 (SSH), 8787 (WebUI — só localhost; externo via Cloudflare
  Tunnel), 20241 (API interna do gateway).
- **WebUI ↔ gateway:** comunicação via localhost — `API_SERVER_KEY` **não
  existe mais** no modelo VM.
- **Reinício de host:** `sudo reboot` — sem docker a reiniciar; os user services
  e o cloudflared sobem sozinhos no boot.
- Detalhes, pendências e troubleshooting: `hermes_mpt_ops/docs/RUNBOOK-MANUTENCAO-VM.md`.

## Monitoramento de Uso/Custo (hermes insights)

Quando o usuário perguntar sobre gasto/uso de tokens, usar **`hermes insights`** (CLI nativa do Hermes, últimos 30 dias):

```
~/.hermes/hermes-agent/venv/bin/hermes insights
# → sessions, mensagens, tool calls, input/output/total tokens, modelos,
#   plataformas, top tools/skills, padrões de atividade, sessões notáveis
```

- `Total tokens` inclui **cache read** (contexto reutilizado) — muito maior que input+output; cache custa ~10x menos.
- **Limitação:** o relatório mostra TOKENS, não valor em dinheiro. `estimated_cost_usd` nas sessions fica `0.0 / cost_status=unknown` para provider Nous (assinatura com créditos, não pay-per-token).
- **Valor financeiro real** só no Portal Nous (`portal.nousresearch.com` → login interativo Cloudflare+Privy). Os endpoints `/api/usage|billing|credits|wallet` retornam HTML da SPA (200), NÃO JSON — não há API pública de saldo.
- Estimativa aproximada: usar preços públicos do modelo (ex: deepseek-v4-flash ≈ $0.11/M input, $0.22/M output) e lembrar que assinatura com créditos difere de pay-per-use.

## Referências

- `references/pdf2wiki-ingestion.md` — heurísticas e fluxo do pipeline
- `references/cron-wrapper-pattern.md` — padrão de wrapper para cron
- `references/migracao-nomes-neutros.md` — refatoração estrutural (renomear repos/pastas/scripts em todo o ambiente)
- `references/ssh-host-access.md` — HISTÓRICO: acesso SSH container→host (obsoleto desde a migração p/ VM nativa)
- `references/fluxo-completo-download-catalogo.md` — pipeline end-to-end: cloudscraper → PDF → PyMuPDF → MD → SQLite
- `references/indexar-boletins-prt14.md` — indexador específico PRT14 (relevância 0/1/2, isolamento de sub-bloco)
