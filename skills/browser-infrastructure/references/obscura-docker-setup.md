# Obscura Docker — Setup validado (15/08/2026)

## Container persistente
```bash
docker run -d --name obscura \
  --restart unless-stopped \
  -p 127.0.0.1:9222:9222 \
  h4ckf0r0day/obscura
```

- **Sobrevive a reboot** ✅ (`--restart unless-stopped`)
- CDP exposto em `127.0.0.1:9222`
- Binário único Rust (~70MB), sem Chrome/Node

## Configuração Hermes (plugin `browser-obscura`)
```yaml
browser:
  cloud_provider: "obscura"
# Env para modo remoto (conecta no server existente, não spawna):
OBSCURA_CDP_URL=http://127.0.0.1:9222
```

## Testes realizados (15/08/2026)

| Teste | Resultado |
|-------|-----------|
| Container up após reboot | ✅ |
| CDP `/json/version` responde | ✅ |
| Navegação MPT (GET + select + Pesquisar) | ✅ (via CDP nativo `Target.createTarget`) |
| Plugin `browser-obscura` via Hermes | ⚠️ Bug CDP v0.2.0: `Page.navigate: No page for session` no target default |

## Bug CDP v0.2.0 (conhecido)
O target default (`page-1` em `about:blank`) tem bug:
- `Page.navigate` → `No page for session`
- `DOM.getBoxModel` → `float` error

**Workaround:** CDP nativo criando target novo:
```python
# Criar target novo
cdp.send("Target.createTarget", {"url": URL, "width": 1280, "height": 720})
# Usar o sessionId retornado para navigate, click, etc.
```

O plugin `browser-obscura` usa o target default — por isso falha em interações, mas navegação simples funciona.

## Verificação rápida
```bash
docker ps -f name=obscura
curl -s http://127.0.0.1:9222/json/version
# → "Browser":"Chrome/151.0.7922.34"
```