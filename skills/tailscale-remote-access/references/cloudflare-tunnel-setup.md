# Cloudflare Tunnel — Setup completo (acesso remoto ao WebUI)

Implementado em ago/2026 como substituto do Tailscale (rede corporativa MPT bloqueia
o control plane do TS). Domínio: `asideia.net` · túnel: `webui-tunnel` · endpoint:
`https://webui.asideia.net`.

## Arquitetura

```
Cliente (qualquer rede, inclusive MPT) → https://webui.asideia.net
    → Cloudflare (Access: login e-mail + código) → túnel cloudflared
    → host hermes-01 (localhost:8787) → WebUI (senha própria — 2ª camada)
```

- **cloudflared roda no HOST** como serviço systemd (`cloudflared.service`), não no container.
- **Túnel é conexão de SAÍDA** (HTTPS:443) — funciona atrás de CGNAT e de proxy
  corporativo; **nenhuma porta aberta** no roteador.
- 2 camadas de auth: Cloudflare Access (e-mail + código) + senha do WebUI.

## Passo a passo

### 1. Domínio + conta
- Registrar o domínio **no próprio Cloudflare** (registrador "at cost", sem markup)
  — domínio já fica na conta, sem etapa de nameserver. Ex: `asideia.net` (~US$11/ano).
- Escolha de TLD: `.net` soa mais institucional que `.dev`; `.dev`/`.app` forçam
  HTTPS de fábrica. Verificar disponibilidade via RDAP: `https://rdap.org/domain/<d>`.

### 2. Criar o túnel (painel)
- dash.cloudflare.com → Networking → Tunnels → Create a tunnel → nome (`webui-tunnel`)
- Na tela de instalação aparece o comando `cloudflared service install eyJ...` — o
  **token** é a parte `eyJ...` (~200 chars), o que o agente precisa para instalar no host.

### 3. Instalar cloudflared no host
- Binário oficial: `curl -fsSL -o cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && chmod +x`
- ⚠️ **Sem sudo para `/usr/local/bin`:** se o NOPASSWD só cobre `reboot`, instalar em
  `~/.local/bin/` (sem sudo) OU pedir ao usuário para instalar com sudo. O comando
  `sudo cloudflared service install <token>` registra o serviço systemd + `/etc/cloudflared/token`.
- Verificar: `systemctl status cloudflared` → logs com `Registered tunnel connection`.

### 4. Rota pública (painel)
- Tunnels → túnel → Public Hostname → Add: subdomain `webui`, domain `asideia.net`,
  Service `HTTP`, URL `localhost:8787`. (Hostname público é criado automaticamente
  em full DNS setup.)

### 5. Cloudflare Access (proteção por e-mail)
- Zero Trust → Access controls → Applications → Create → Self-hosted → Add public hostname.
- **Política:** Action `Allow` + rule `Include → Emails → <e-mail do usuário>`
  (NUNCA "Everyone" — é deny-by-default, só quem casa a policy entra).
- Session duration: 24h. Resultado: login com e-mail + código antes de chegar ao app.

## Pitfalls (aprendidos na implementação)

1. **HERMES_WEBUI_PASSWORD não chegava ao container** — o `.env` tinha a senha, mas o
   `docker-compose.yml` do serviço `hermes-webui` NÃO declarava a variável no
   `environment:`. Sintoma: WebUI acessível sem pedir senha (só Access protegia).
   **Fix:** adicionar `- HERMES_WEBUI_PASSWORD=${HERMES_WEBUI_PASSWORD:-}` no environment.
   **Aplicar:** `docker compose up -d` (RECRIA o container; `restart` não basta para
   variável de ambiente nova). Verificar: `docker inspect hermes-webui --format '{{range .Config.Env}}{{println .}}{{end}}'`.
2. **`docker compose config` para validar interpolação** sem subir nada — mostra os
   valores efetivos; conferir que a chave real (não `CHANGE_ME`) está sendo usada.
3. **cloudflared sem sudo:** mover para `~/.local/bin` + `export PATH` — o serviço
   systemd via `cloudflared service install` exige root, mas o binário em user dir
   serve para testes manuais (`cloudflared tunnel run --token ...`).
4. **Token no chat:** é credencial de instalação — o usuário cola no chat; guardar
   no `.env` local (fora do git) se for reutilizar.

## Referências
- Docs oficiais: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/get-started/create-remote-tunnel/
- Access (self-hosted app): https://developers.cloudflare.com/cloudflare-one/access-controls/applications/http-apps/self-hosted-public-app/
