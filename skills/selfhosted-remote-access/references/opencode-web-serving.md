# Servir o OpenCode Web (`opencode web`)

Como servir o OpenCode como app web persistente e expô-lo via Cloudflare — receita validada na VM hermes-01.

## Binário e path (pitfall do "não instalado")

`npm i -g opencode-ai` coloca o binário nativo em `<npm root -g>/opencode-ai/bin/opencode.exe` (aqui: `/home/hermes/.local/lib/node_modules/opencode-ai/bin/opencode.exe`). Se `command -v opencode` vazio mas `npm ls -g` mostra o pacote:crie o symlink:

```bash
ln -sf $(npm root -g)/opencode-ai/bin/opencode.exe ~/.local/bin/opencode   # ~/.local/bin já está no PATH
```
O binário native é um `.exe` de ~180MB — o npm package usa postinstall para selecionar a plataforma. Auth compartilhado com o CLI: `~/.local/share/opencode/auth.json` (`opencode auth list`).

## Credencial (camada 2, após o Access)

Arquivo `~/.config/opencode/opencode-server.env` (chmod 600):

```
OPENCODE_SERVER_USERNAME=opencode
OPENCODE_SERVER_PASSWORD=<openssl rand -base64 21 | tr -d '/+=' | cut -c1-24>
```

## Unit systemd user

`~/.config/systemd/user/opencode-web.service` — systemd NÃO herda `.profile`/PATH:

```ini
[Unit]
Description=OpenCode Web Server
After=network.target

[Service]
Type=simple
EnvironmentFile=%h/.config/opencode/opencode-server.env
ExecStart=%h/.local/bin/opencode web --hostname 0.0.0.0 --port 4096
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload && systemctl --user enable --now opencode-web
loginctl enable-linger <user>   # senão não sobrevive a logout/reboot
```

## Validação local (antes de expor)

```bash
curl -s -o /dev/null -w '%{http_code}' http://localhost:4096        # → 401 (protegido)
curl -s -o /dev/null -w '%{http_code}' \
  -u "$(grep '^OPENCODE_SERVER_USERNAME=' ~/.config/opencode/opencode-server.env | cut -d= -f2):$(grep '^OPENCODE_SERVER_PASSWORD=' ~/.config/opencode/opencode-server.env | cut -d= -f2)" \
  http://localhost:4096                                                      # → 200
```
Leia a senha SEMPRE direto do env file — um snapshot copiado para outra path pode divergir do que o serviço lê (aconteceu: `/tmp` snapshot rejeitado, arquivo-fonte aceito).

## Exposição Cloudflare

- Dashboard → túnel existente → **Public Hostname**: subdomínio `opencode` → `HTTP localhost:4096`.
- **Access** policy: Allow por e-mail do usuário — **NUNCA "Everyone"**, pois o serviço expõe capacidade de codificar.
- Camadas: Internet → Cloudflare Access (e-mail+OTP) → senha do serviço (`openコード / <PASSWORD>`) → opencode.
- Deploy: `https://opencode.asideia.net` (túnel `webui-tunnel`).
- Trocar senha: editar o env file + `systemctl --user restart opencode-web`.

## Sessões web × CLI

O web compartilha o MESMO auth/provider do CLI,mas as sessões/estados do web são dele, independentes das que o CLI cria — refletem repos/directórios do usuário, não os das delegações via skill.
