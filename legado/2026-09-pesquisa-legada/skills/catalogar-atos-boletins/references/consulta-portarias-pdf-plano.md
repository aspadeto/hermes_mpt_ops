# Consulta de atos por período diretamente dos PDFs planos

Quando os boletins de um mês/ano **ainda não foram catalogados** no `atos.db`
(verificado 08/2026: o banco para em 2025-06; os PDFs de 2026 ficam como **PDFs
planos** em `/opt/data/hermes-data/boletins/`, sem pastas `YYYY-MM-DD`), o
`catalogar_atos.py --raiz boletins` **não os pega** — ele só varre pastas com
formato `YYYY-MM-DD` que contenham `.md` extraído. Para responder "quais
portarias foram publicadas nos últimos N dias" sem catalogar tudo, extrair
direto do PDF.

## Fluxo validado (08/2026)

### 1. Mapear a data de circulação de cada boletim
O nome do PDF (`BS-NNN-2026.pdf`) não tem a data. Lê-la da **página 1** com
PyMuPDF (`fitz`/`pymupdf`, disponível em `hermes_mpt_ops/.venv-bol`):

```python
import fitz, re
doc = fitz.open('/opt/data/hermes-data/boletins/BS-145-2026.pdf')
txt = doc[0].get_text()
m = re.search(r'(\d{1,2})\s+(?:DE\s+)?([A-ZÇÃÊÓÍÀ-Ú]+)\s+DE\s+(\d{4})', txt[:1500], re.IGNORECASE)
# BS-145 -> 10 AGOSTO 2026 ; exceções: BS-NNN.1/.2 = "BSE EXTRAORDINÁRIO" (sem data na p1)
```

Definir a janela (`hoje - N dias` a `hoje`) e reter só os boletins do período.

### 2. Extrair portarias do texto
Ler o PDF inteiro, aplainar com `re.sub(r'\s+', ' ', texto)` e localizar os
**cabeçalhos de bloco** de portaria:

```python
PAT = re.compile(r'(PORTARIAS?)\s*N[º°o]?\s*([\d.]+)\s*,?\s*(?:DE\s+)(\d{1,2})\s+DE\s+([A-ZÇÃÊÓÍÀ-Ú]+)\s+DE\s+(\d{4})', re.IGNORECASE)
```

⚠️ **Filtrar CITAÇÕES:** o texto do boletim **cita** portarias antigas no corpo
(ex: `Portaria nº 1728, de 2 de outubro de 2017 …`, `Portaria nº 050, de 30 de
março de 2015`). Discriminante confiável = **a data do cabeçalho cai dentro da
janela de período** e o formato é `PORTARIAS Nº X, DE DD DE MÊS DE AAAA`. Uma
primeira passada sem filtrar a data devolve dezenas de citações falsas (2015,
2017) — aplicar sempre a filtragem por `data` antes de contar.

### 3. Deduplicar
Mesmo `(data, numero)` pode repetir (sumário + corpo). Deduplicar por chave
`(data, numero)` antes de apresentar.

### 4. Ementa
O trecho logo após o cabeçalho (`texto_flat[m.end():m.end()+260]`) é um
**resumo provisório** (nome do órgão/região + assunto), não a ementa formal —
avisar o usuário disso. A ementa curada só vem da leitura integral do ato.

## Verificação manual
- `sqlite3` CLI não existe no host → usar
  `.venv-bol/bin/python -c "import sqlite3; ..."` para consultar `atos.db`.
- Se o usuário quiser histórico consultável dos boletins de 2026, o caminho é
  catalogar (baixar mês → `audit_boletim.py` → `catalogar_atos.py`), não a
  extração ad hoc acima.

## Resultado de referência (16/08/2026)
Boletins 145-148 (10–14/08) no catálogo de 7 dias: BS-146→8, BS-147→8,
BS-148→15 portarias; BS-145 ficou de fora (portarias de 06–07/08, fora da
janela).