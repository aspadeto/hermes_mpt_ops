# Checklist pós-migração / restauração em host novo

Validado em 07/08/2026 (migração Docker → VM hermes-01). Ordem de verificação
após mover `hermes-data` para o caminho definitivo:

## 1. Repos git (hermes_mpt_kb / hermes_mpt_ops em /opt/data/hermes-data/)

- `git status` em cada repo: branch main, working tree limpo
- **credential.helper**: no container os repos tinham
  `store --file=/opt/data/hermes-data/.git-credentials` (caminho do container).
  No host novo o arquivo vive em `/home/hermes/.git-credentials` → ajustar em CADA repo:
  ```bash
  git config credential.helper "store --file=/home/hermes/.git-credentials"
  ```
  Testar leitura autenticada: `git ls-remote origin HEAD` (antes do ajuste falha com
  `could not read Username for 'https://github.com'`).
- **user.name por repo**: o KB tinha `user.name=user.email` (bug) → commits saíam com
  autor errado. Conferir com `git log --format="%h %an" -3` e corrigir:
  `git config user.name "Aloisio Spadeto"`. O OPS normalmente já está correto.

## 2. Venvs (excluídos do backup — DATA_EXCLUDE)

- `.google-venv` (e qualquer venv com symlink) quebra na migração: `bin/python` é
  symlink para o python do container. Sintoma: `No such file or directory` no
  `bin/python`. Recriar com uv:
  ```bash
  uv venv .google-venv --clear --python 3.11
  uv pip install --python .google-venv/bin/python google-api-python-client google-auth-oauthlib google-auth-httplib2
  ```

## 3. Email (himalaya)

- **Não existe no apt nem snap do Ubuntu** — instalar do GitHub release:
  `himalaya.x86_64-linux.tgz` → `~/.local/bin/himalaya` (v2.0.0, ELF musl estático)
- Config/credenciais NÃO migram no hermes-data — estavam em
  `.hermes/home/.config/himalaya/` (no tgz do backup): `config.toml`,
  `get-password.sh`, `.gmail-app-password`. Extrair do tgz → `~/.config/himalaya/`
- Ajustar caminhos absolutos do container (sed):
  `s|/home/hermes/.hermes/home/.config/himalaya|/home/hermes/.config/himalaya|g`
  em `config.toml` e `get-password.sh`
- Permissões: `chmod 600` em config.toml/.gmail-app-password, `chmod 700` no get-password.sh
- **Pitfalls**:
  - `mv *` NÃO move arquivos ocultos (`.gmail-app-password` fica para trás) — mover
    explicitamente ANTES de `rm -rf` da estrutura aninhada
  - `sed -i` reescreve o script e perde o bit de execução → erro
    `Secret command error: Permission denied` → `chmod +x get-password.sh`
  - **v2.0.0 mudou a CLI**: `himalaya template send` NÃO existe mais. Enviar com
    `himalaya smtp send --mail-from X --rcpt-to Y` (RFC 5322 via stdin). Ler com
    `himalaya envelope list` (inalterado).

## 4. Google Workspace (token OAuth)

- `setup.py --check` → `TOKEN_REVOKED (invalid_grant)` = refresh_token revogado/expirado
  no Google. NÃO é problema de config — client_id/secret podem estar corretos.
- Fluxo de reautorização mediado pelo agente (setup.py foi desenhado para isso):
  ```bash
  python setup.py --auth-url    # → link para o usuário abrir e aprovar
  python setup.py --auth-code CODE   # usuário cola o código do redirect localhost
  python setup.py --check       # validar
  ```
- O redirect `http://localhost:1` mostra página de erro no navegador — NORMAL; o
  usuário copia o `code=...` da URL.

## 5. WebUI / mounts (segurança)

- Montar a RAIZ do hermes-data em containers expõe segredos legíveis por root:
  `GITHUB_TOKEN.txt`, `.git-credentials`, `hermes_mpt_ops/docker/.env`
  (API_SERVER_KEY, HERMES_WEBUI_PASSWORD). Solução: **mounts seletivos** das subpastas
  necessárias (hermes_mpt_kb, hermes_mpt_ops), nunca a raiz; e mover `docker/.env`
  para FORA do repo OPS (bind mount não suporta exclusão de subpath).
- WebUI two-container: NÃO roda agente separado — embute o código do hermes-agent
  (instala deps do hermes-agent-src no venv) mas sessões vão via `HERMES_API_URL` para
  o gateway. Ferramentas acionadas no WebUI rodam no container webui (limitação #681 do
  projeto). `default_workspace` do WebUI é `/workspace` (settings.json) — divergência de
  caminho vs agent é a fonte da "confusão de paths".
