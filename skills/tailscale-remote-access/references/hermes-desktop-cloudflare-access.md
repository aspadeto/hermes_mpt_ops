# Conectando Hermes Desktop a Gateway atrás de Cloudflare Tunnel + Access

O Hermes Desktop (app Electron nativo) pode se conectar a um gateway remoto protegido por **Cloudflare Tunnel + Cloudflare Access (OAuth)**. O fluxo é:

1. Desktop abre a URL do gateway (ex: `https://dashboard-01.asideia.net`)
2. Cloudflare Access exige login (e-mail + código) → seta cookies `privy-token`, `privy-session`
3. Desktop usa esses cookies + headers `CF-Access-Client-Id` / `CF-Access-Client-Secret` para autenticar no gateway Hermes
4. WebSocket upgrade (`wss://.../api/ws`) usa ticket OAuth minted via `POST /api/auth/ws-ticket`

---

## Configuração no Desktop (Settings → Connections)

| Campo | Valor |
|-------|-------|
| **URL** | `https://dashboard-01.asideia.net` (seu hostname Cloudflare) |
| **Auth mode** | `oauth` (o gateway usa OAuth via Cloudflare Access) |
| **Extra gateway headers** | JSON com `CF-Access-Client-Id` e `CF-Access-Client-Secret` (obtidos no painel Cloudflare Zero Trust → Access → Applications) |

Exemplo de `headers` no `connection.json` / registry:
```json
{
  "mode": "remote",
  "remote": {
    "url": "https://dashboard-01.asideia.net",
    "authMode": "oauth",
    "headers": {
      "CF-Access-Client-Id": { "encoding": "safeStorage", "value": "..." },
      "CF-Access-Client-Secret": { "encoding": "safeStorage", "value": "..." }
    }
  }
}
```

---

## Teste de conectividade antes de abrir o Desktop

```bash
# Teste HTTP (precisa dos headers CF-Access)
curl -H "CF-Access-Client-Id: SEU_ID" \
     -H "CF-Access-Client-Secret: SEU_SECRET" \
     https://dashboard-01.asideia.net/api/status
# Espera 200 com {"serve": true, "auth_required": true, ...}

# Teste WS (precisa de cookies de sessão + ticket)
# O Desktop faz isso automaticamente via mintGatewayWsTicket()
```

---

## Onde fica o `userData` do Desktop (Linux)

- Padrão: `~/.config/hermes-desktop` (Electron `app.getPath('userData')`)
- Override: `HERMES_DESKTOP_USER_DATA_DIR=/caminho hermes desktop`
- Arquivos relevantes: `connection.json` (v1), `registry.json` (v2), `desktop-installation.json`

---

## Pitfalls conhecidos

1. **Headers não aplicados no WS** — o Desktop aplica headers extras tanto no HTTP quanto no WebSocket upgrade (mesma origem `https`/`wss`). Verifique `normalizeRemoteHeaders()` em `connection-config.ts`.

2. **Cookies Privy vs Gateway** — Cloudflare Access usa cookies `privy-token`/`privy-session` (Next.js/Privy). O gateway Hermes usa cookies `hermes_session_at`/`hermes_session_rt`. O Desktop detecta liveness via `cookiesHaveLiveSession()` olhando cookies do gateway, NÃO cookies Privy. Se o gateway estiver atrás do Access, o fluxo OAuth do gateway pode não ser usado — o Desktop trata isso como `authMode: 'oauth'` mas o ticket vem do gateway, não do Privy.

3. **`HERMES_DESKTOP=1` no ambiente** — quando o Desktop spawna o backend `serve`, seta `HERMES_DESKTOP=1` e `HERMES_WEB_DIST=...`. Se você herdar esse env num shell e rodar `hermes dashboard`, ele tenta servir o renderer do Desktop (falha). O `cmd_dashboard` limpa isso se `HERMES_DESKTOP != "1"`.

---

## Referências no código

- `apps/desktop/electron/connection-config.ts` — `normalizeRemoteHeaders`, `buildGatewayWsUrlWithTicket`, `resolveTestWsUrl`
- `apps/desktop/electron/connection-registry.ts` — v2 registry com campo `headers`
- `apps/desktop/electron/main.ts` — `applyConnectionChange`, `remoteRequestMatchesBaseUrl`
- `hermes_cli/web_server.py` — `/api/auth/ws-ticket` endpoint, `DashboardAuthProvider` (Plugins → `plugins/dashboard_auth/`)