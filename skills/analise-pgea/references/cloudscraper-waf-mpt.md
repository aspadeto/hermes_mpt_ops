# Cloudscraper vs WAF do mpt.mp.br (investigação — 07/08/2026, RESOLVIDO)

## Contexto

Baixar Boletim de Serviço do MPT (portal da Transparência,
`boletinsDeServico.xhtml`) a partir da VM nativa. O browser headless (local
via agent-browser E cloud via Browser Use/gateway Nous) é **bloqueado** pelo
WAF; o `cloudscraper` (Python) **passa** e resolve o fluxo completo
(consulta + download de PDFs).

## Fatos verificados

1. **WAF bloqueia headless por detecção de automação, não por IP.**
   - Browser local (agent-browser, IP do host) → "Página bloqueada!"
   - Browser cloud (Browser Use via gateway Nous, IP 181.220.199.51) → mesma página
   - `Client IP` reportado é o mesmo nos dois casos → o WAF distingue por
     fingerprint/JS, não pelo IP de origem.
2. **cloudscraper passa** (`scraper.get(url)` → HTTP 200, página real ~39KB
   com form `consultaForm`). Requests puro falha com
   `SSL: UNEXPECTED_EOF_WHILE_READING` (TLS fingerprint rejeitado); o
   cloudscraper emula fingerprint de browser e o WAF aceita. Mesmo IP do host.
3. **Fluxo do portal é JSF/PrimeFaces puro** (sem botão de pesquisa clássico):
   - Selects: `j_idt176` (ano) e `j_idt180` (mês), ambos com
     `onchange="PrimeFaces.ab({s:this,e:"change",p:"<id>",u:"resultado"})"`
   - Mês em **inglês abreviado**: `AUG` (NÃO `AGO`) — JAN..DEZ
   - Form `consultaForm`; campos: `menu=menu`, `j_idt176`, `j_idt180`,
     `javax.faces.ViewState` (um por form — menu e consultaForm)
   - Cookies de sessão: `JSESSIONID`, `csfcfc` (CSRF PrimeFaces), `cookiesession1`

## SOLUÇÃO (payload real capturado no DevTools — a chave do enigma)

O POST que funciona NÃO é o ajax do `onchange` — é um **submit completo
multipart/form-data** com um campo **gatilho oculto** que o ajax emulado não
enviava. Capturar o payload real de um browser (DevTools → Network) foi
decisivo; tentar adivinhar os parâmetros do PrimeFaces por tentativa-e-erro
falha (todas as variações de `partial.execute/process` retornam painel
`resultado` vazio).

### Consulta (listar boletins do mês)

POST **multipart/form-data** (NÃO urlencoded) em
`boletinsDeServico.xhtml`, campos nesta ordem:

```
consultaForm           = consultaForm
javax.faces.ViewState  = <do GET inicial, extraído do form consultaForm>
j_idt176               = 2026        (ano)
j_idt180               = AUG         (mês, inglês abreviado)
j_idt183               = j_idt183    ← GATILHO obrigatório (id = valor)
```

Sem o `j_idt183`, o servidor responde 200 com a página mas **não executa a
busca** (painel `resultado` vazio). O `j_idt183` não aparece em selects nem
onclicks — só no payload do browser real.

Resposta: HTML completo com `<table id="tabelaArquivos">` — cada `<tr>` é um
boletim: célula 1 = `BS Eletrônico - NNN/2026 - DD/MM/AAAA`, célula 2 = link
`<a id="tabelaArquivos:N:linkArq">` com `onclick="mojarra.jsfcljs(...)"`.

### Download (baixar PDF)

POST multipart com o campo do link + **ViewState da resposta pós-consulta**
(um GET novo falha — a tabela precisa estar carregada na sessão):

```
consultaForm                = consultaForm
javax.faces.ViewState       = <ViewState do HTML da consulta, NÃO de um GET novo>
j_idt176                    = 2026
j_idt180                    = AUG
tabelaArquivos:N:linkArq    = tabelaArquivos:N:linkArq   (N = índice da linha)
```

Resposta: `application/pdf` (validar com `content[:5] == b"%PDF-"`).

## Scripts versionados (hermes_mpt_ops/scripts/)

- `baixar_boletim.py` — consulta + download via cloudscraper (CLI: ano, mês,
  `--baixar N|todos`, `--dir`). Requer venv com `cloudscraper`.
- `indexar_boletins_prt14.py` — indexa os MDs extraídos num SQLite
  (tabela `atos` com boletim/data/tipo/numero/ementa/relevância 0/1/2).
- `audit_boletim.py` — PDF → MD por ato (headers `## TIPO Nº X`).

## Pitfalls

- **NUNCA tentar adivinhar o POST do PrimeFaces por tentativa-e-erro** —
  capturar o payload real (DevTools) quando o fluxo envolve JSF.
- O POST é multipart — `requests.post(url, files={...})` (cloudscraper aceita);
  urlencoded não funciona.
- Download usa o ViewState pós-consulta, não de um GET novo.
- `j_idt183` (e ids `j_idt*`) são gerados pelo JSF — podem mudar; validar no
  payload atual se o fluxo quebrar.
