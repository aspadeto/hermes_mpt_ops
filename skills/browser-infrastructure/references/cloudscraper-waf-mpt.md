# WAF MPT: cloudscraper bypass completo (15/08/2026)

## Contexto
O WAF do `mpt.mp.br` (Cloudflare) bloqueia **browsers headless** (local e cloud via Browser Use) por detecção de automação JS — **não é bloqueio por IP**. O browserless/chromium local e o Browser Use cloud falham com "Sua requisição foi bloqueada! Attack ID 20000051".

## Solução validada: cloudscraper

`cloudscraper` passa no WAF porque:
- Simula fingerprint TLS de browser real (JA3/JA3S)
- Não executa JavaScript (não há detecção `navigator.webdriver`)
- Mesmo IP, sem proxy residencial

## Fluxo completo descoberto (via DevTools em 07/08/2026)

### 1. GET inicial → extrai ViewState
```python
html = scraper.get(URL, timeout=30).text
# ViewState do form consultaForm (há 2 forms na página)
vs = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]+)"', form_html).group(1)
```

### 2. POST multipart (NÃO urlencoded) — gatilho `j_idt183`
```python
resp = scraper.post(URL, files={
    "consultaForm": (None, "consultaForm"),
    "javax.faces.ViewState": (None, vs),
    "j_idt176": (None, str(ano)),      # ex: "2026"
    "j_idt180": (None, mes),           # ex: "AUG" (JAN..DEZ)
    "j_idt183": (None, "j_idt183"),    # GATILHO obrigatório — sem ele o servidor recebe mas NÃO consulta
}, timeout=30)
```

**Ponto crítico:** O campo `j_idt183=j_idt183` é o gatilho da consulta PrimeFaces. Sem ele, o servidor recebe os parâmetros mas **não executa a busca**.

### 3. Resposta HTML → tabelaArquivos
```html
<table id="tabelaArquivos">
  <tr>
    <td>BS Eletrônico - 143/2026 - 06/08/2026</td>
    <td><a id="tabelaArquivos:4:linkArq" onclick="mojarra.jsfcljs(...)"></a></td>
  </tr>
</table>
```

Extrair: índice (ex: `4`) + nome do boletim.

### 4. Download — POST multipart com ViewState **pós-consulta**
```python
# RE-CONSULTAR para pegar o ViewState da resposta COM a tabela carregada
html = _consultar_html(scraper, ano, mes)
vs = _viewstate(html)  # ViewState correto

campo = f"tabelaArquivos:{indice}:linkArq"
resp = scraper.post(URL, files={
    "consultaForm": (None, "consultaForm"),
    "javax.faces.ViewState": (None, vs),
    "j_idt176": (None, str(ano)),
    "j_idt180": (None, mes),
    campo: (None, campo),  # ex: "tabelaArquivos:4:linkArq"
}, timeout=60)

if resp.content[:5] == b"%PDF-":
    destino.write_bytes(resp.content)
```

**Ponto crítico:** O download **falha** com ViewState de um GET novo — precisa do ViewState da resposta que já tem a tabela carregada na sessão JSF.

## Script versionado
`hermes_mpt_ops/scripts/baixar_boletim.py` — método atual (lista, baixa, conversão integrada).

```bash
# listar
python3 baixar_boletim.py 2026 AUG

# baixar todos do mês
python3 baixar_boletim.py 2026 AUG --baixar todos --dir /opt/data/hermes-data/boletins
```

## Uso no pipeline completo
Ver `dr-mpt-ops/references/fluxo-completo-download-catalogo.md` para o pipeline end-to-end:
```
cloudscraper → PDFs → PyMuPDF → MDs (YYYY-MM-DD/) → catalogar_atos.py → SQLite
```