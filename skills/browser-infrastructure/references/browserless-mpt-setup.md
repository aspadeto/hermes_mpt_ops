# Browserless/Chromium Docker Setup (MPT context)

## Imagem
`ghcr.io/browserless/chromium:latest` — Chrome 151 (ago/2026), mantido ativamente
(v2.55.3 publicado ago/2026 no GitHub, mas Docker Hub parou em fev/2024).

Repositório: https://github.com/browserless/browserless
Docs Docker: https://docs.browserless.io/enterprise/docker/configuration

## Docker Compose

```yaml
services:
  browser:
    image: ghcr.io/browserless/chromium:latest
    container_name: hermes-browser
    restart: unless-stopped
    shm_size: 2gb
    environment:
      - CONCURRENT=10
      - TIMEOUT=300000
      - HEALTH=true
      - MAX_QUEUE_LENGTH=20
      - USER_AGENT=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 ... Chrome/151.0.0.0 Safari/537.36
    networks:
      - hermes-net
```

## Hermes Config

```yaml
browser:
  cloud_provider: ""
  cdp_url: "ws://browser:3000/"
  inactivity_timeout: 120
```

(Remover `use_gateway: true` — conflita com modo local)

## Comportamento com MPT

- ✅ TLS: Chromium stack próprio negocia com servidor MPT (curl/Python requests falham)
- ❌ WAF: Cloudflare detecta headless Chromium (Attack ID 20000051) mesmo sem `HeadlessChrome`
- ✅ Browser Use cloud passa por ter proxies residenciais + stealth patches

## Testes

- `/json/version` → `{"Browser":"Chrome/151.0.7922.34", ...}`
- `/pressure` → health check
- WAF block: "Sua requisição foi bloqueada", "Attack ID: 20000051", "Message ID: 003..."