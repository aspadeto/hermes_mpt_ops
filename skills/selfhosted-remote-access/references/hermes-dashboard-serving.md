# Hermes Dashboard — serving, auth e session token

Conhecimento validado em 15/08/2026 ao criar o serviço do dashboard na VM nativa
(`hermes-01`), expô-lo via Cloudflare Tunnel e configurar o session token.

## Visão geral: dois modos de auth mutuamente exclusivos

O dashboard (hermes_cli/web_server.py) tem **exatamente UM** esquema de auth
ativo por bind. Escolher o bind errado faz o token que você configurou
silenciosamente NÃO funcionar.

| Bind | `auth_required` | Esquema de auth | Resultado |
|------|-----------------|-----------------|-----------|
| `--host 127.0.0.1` (loopback) | `False` | `_SESSION_TOKEN` (env `HERMES_DASHBOARD_SESSION_TOKEN`), header `X-Hermes-Session-Token` | Token funciona; endpoints sensíveis exigem o token |
| `--host 0.0.0.0` (não-loopback) | `True` | OAuth **ou** `dashboard.basic_auth` (password provider); cookie de sessão | Token `_SESSION_TOKEN` **NÃO é usado** → 401 `reason:"no_cookie"` |

Lei em `web_server.py`:

```python
def should_require_auth(host, allow_public=False):
    # --insecure NÃO disabilita o gate desde o hardening jun/2026
    # (campanha hermes-0day MCP-persistence). Não-loopback SEMPRE exige
    # auth provider. --insecure virou no-op (aceito mas ignorado).
    return host not in _LOOPBACK_HOST_VALUES  # 127.0.0.1, localhost, ::1
```

**Conclusão prática:** para o Hermes Desktop se conectar e manter sessão, o
serviço DEVE bindar em `127.0.0.1` e o acesso remoto vai pelo Cloudflare
Tunnel (Access é a camada externa). O `dashboard.basic_auth` só é exercido se
alguém bindar em `0.0.0.0`.

## `HERMES_DASHBOARD_SESSION_TOKEN` (token de sessão da app)

- **Local:** `~/.hermes/.env` (o serviço tem `EnvironmentFile=-%h/.hermes/.env`)
- **Gerar:** `python3 -c "import secrets; print(secrets.token_urlsafe(48))"`
- **Por que fixar:** sem ele o dashboard gera um token **efêmero por restart**.
  Fixando via env, a sessão do Hermes Desktop sobrevive a restart do serviço.
- **Como autentica:** header `X-Hermes-Session-Token: <token>` (ou o legacy
  `Authorization: Bearer <token>`).
- **Uso em teste:** `/api/env/reveal` é **POST** (não GET) com corpo JSON
  `{"key":"NOME_VAR"}`:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
       -H "X-Hermes-Session-Token: $TOKEN" \
       -d '{"key":"HERMES_DASHBOARD_SESSION_TOKEN"}' \
       http://127.0.0.1:9119/api/env/reveal
  # 200 → token válido; 401 no_cookie → bind não-loopback (trocar pra 127.0.0.1)
  ```
- **Rate limit:** 5 reveals por 30s (429 além disso).

## `dashboard.basic_auth` (config.yaml) — só em bind não-loopback

```yaml
dashboard:
  basic_auth:
    username: hermes
    password_hash: scrypt:$...      # gerar hash scrypt no venv do hermes
    secret: <base64url de 32 bytes> # HMAC de assinatura das sessões
    session_ttl_seconds: 43200      # 12h
```

- **`secret` é crítico:** sem ele, o provider gera chave de assinatura aleatória
  por processo → sessões morrem a cada restart e não funcionam multi-worker.
  Fixar `secret` dá sessões estáveis.
- **Geração:** `secret = secrets.token_bytes(32)` (base64url); senha com
  scrypt via `hashlib.scrypt` (n=16384,r=8,p=1,dklen=32) no venv do hermes.
- Apenas `supports_password=True`; login via POST `/auth/password-login` com
  corpo `{"provider":"basic","username":...,"password":...}` definindo cookie.

## Systemd user service (porta 9119)

`~/.config/systemd/user/hermes-dashboard.service` — mesmo padrão gateway/webui:

```ini
[Service]
Type=simple
Environment=HERMES_HOME=%h/.hermes
EnvironmentFile=-%h/.hermes/.env
ExecStart=%h/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main dashboard \
    --no-open --host 127.0.0.1 --port 9119 --skip-build
WorkingDirectory=%h/.hermes
Restart=on-failure
RestartSec=5
[Install]
WantedBy=default.target
```

- Enable: `systemctl --user enable --now hermes-dashboard`
- `--skip-build` evita rebuild do SPA a cada start (usa `web_dist`). SEM ele, o
  serviço roda `npm ci` + vite build no primeiro start (demora ~30s).
- Bind fixo em `127.0.0.1` → token funciona + Cloudflare Access fora.

## Cloudflare Tunnel — segundo hostname

No dashboard CF (Zero Trust → Tunnels → túnel → Public Hostname): segundo
hostname `dashboard-01.asideia.net → HTTP localhost:9119`, com policy de
Acess igual ao webui (Allow + email do usuário, nunca "Everyone").

## Pitfall do evento (15/08/2026)

Colocamos `--host 0.0.0.0` pensando em permitir acesso de outra rede. Com isso
o token NÃO funcionava (`401 reason:"no_cookie"`) — porque bind não-loopback
ativa o gate OAuth/basic_auth e o `_SESSION_TOKEN` deixa de valer. Solução:
voltar para `127.0.0.1` + Cloudflare Tunnel (Access = camada externa). Não usar
`--insecure` para "liberar" — é no-op.