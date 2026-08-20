# MCP Servers para Browser Automation no Hermes

## Visão Geral

O Hermes pode usar servidores MCP (Model Context Protocol) para expor capacidades de browser a qualquer cliente MCP (Claude Desktop, Cursor, o próprio Hermes).

---

## chrome-devtools-mcp (Recomendado para Chrome Local)

Controla **SEU Chrome real** (abas, logins, extensões visíveis).

### Instalação e Registro no Hermes

```bash
hermes mcp add chrome-devtools --command npx --args "-y,chrome-devtools-mcp,--browserUrl,http://127.0.0.1:9222"
```

### Pré-requisito: Chrome com CDP Aberto

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-mcp --no-first-run --disable-default-apps
```

### Vantagens
- ✅ Controla abas/janelas que você está vendo
- ✅ Acessa seus logins, cookies, extensões
- ✅ Zero custo (local)

### Desvantagens
- ❌ Precisa Chrome/Chromium instalado no SO
- ❌ Porta 9222 exposta localmente (segurança: use perfil isolado)
- ❌ Não funciona headless em servidor sem display

---

## browser-use-mcp (Cloud, Pago)

Browser cloud gerenciado com stealth e proxies residenciais.

```bash
hermes mcp add browser-use-cloud --command npx --args "-y,browser-use-mcp"
# Requer BROWSER_USE_API_KEY no ambiente
```

### Vantagens
- ✅ Stealth nativo, passa WAFs
- ✅ Proxies residenciais rotativos
- ✅ Escalável, sem infra local

### Desvantagens
- ❌ Precisa API key paga (NÃO coberto por subscrição Nous)
- ❌ Não controla SEU Chrome

---

## Ferramenta Nativa `browser_exec` (JÁ FUNCIONA no Hermes)

O Hermes Desktop/CLI já inclui **`browser_exec`** — sobe Chromium via Playwright **sem dependências externas**.

### Características

| Característica | Detalhe |
|----------------|---------|
| **Engine** | Playwright (Chromium bundled) |
| **Modo** | Headed (visível) ou headless |
| **Sessão** | Persistente via `session="nome"` — mantém abas/estado entre chamadas |
| **API** | `new_tab(url)`, `goto_url(url)`, `wait_for_load()`, `js(code)`, `capture_screenshot()`, `click_at_xy(x,y)`, `fill_input(sel, text)`, `cdp(...)` |
| **Requisitos** | Zero — Chromium vem no bundle Playwright |
| **Testado** | ✅ Ubuntu 24.04 VM nativa, Hermes Desktop |

### Exemplo Prático (Estilo "Manus Browser Operator")

```python
# 1. Abre janela visível (você vê)
browser_exec(session="meu-chrome", code="""
result = new_tab('https://github.com')
wait_for_load()
""")

# 2. Continua na MESMA janela/abas
browser_exec(session="meu-chrome", code="""
goto_url('https://github.com/NousResearch/hermes-agent')
wait_for_load()
title = js('document.title')
print(title)
""")
```

---

## Resumo de Opções no Ambiente VM Nativa (Sem Docker)

| Abordagem | Precisa Chrome no SO? | Precisa API Key? | Você vê a janela? | Controla SUAS abas? |
|-----------|----------------------|------------------|-------------------|---------------------|
| `browser_exec` (nativo) | ❌ Não (bundled) | ❌ Não | ✅ Sim (headed) | ❌ Abas novas |
| `chrome-devtools-mcp` | ✅ Sim | ❌ Não | ✅ Sim | ✅ Sim |
| `browser-use` cloud (Nous) | ❌ Não | ✅ Subscrição Nous | ❌ Não | ❌ Não |
| `browserless/chromium` Docker | ❌ Não (container) | ❌ Não | ❌ Headless | ❌ Não |

---

## Decisão Recomendada para Este Ambiente

**Use `browser_exec` (nativo)** para:
- Testes rápidos, scraping, automação visual
- Não precisa instalar nada
- Sessão persistente entre chamadas
- Já validado funcionando

**Use `chrome-devtools-mcp`** apenas se:
- Precisa controlar SUAS abas/logins/extensões específicas
- Tem Chrome instalado e aceita abrir com `--remote-debugging-port`