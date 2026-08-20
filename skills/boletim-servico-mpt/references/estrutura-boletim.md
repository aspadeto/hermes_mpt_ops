# Estrutura do Boletim de Serviço do MPT (BS Eletrônico)

> Documenta a estrutura de um Boletim de Serviço (BS) para auditoria de
> extração. Fonte: padrões validados em `hermes_mpt_ops/scripts/audit_boletim.py`
> (migrado do workspace em 06/08/2026).

## Anatomia do BS

Um Boletim de Serviço difere de um PGEA: **não há cabeçalho de peça padronizado**
(como nos autos digitais). A estrutura é:

1. **Cabeçalho** — padrão no topo da primeira página:
   ```
   BS Eletrônico - NNN/AAAA - DD/MM/AAAA
   ```
   Regex validada:
   ```python
   BS_HEADER_RE = re.compile(
       r"BS\s*Eletr[ôo]nico\s*[-–]\s*(\d+(?:\.\d+)?)/(\d{4})\s*[-–]\s*(\d{2}/\d{2}/\d{4})",
       re.IGNORECASE,
   )
   ```

2. **Índice/Sumário analítico** — lista dos atos publicados no boletim.
   Linhas como `1. PORTARIA...`, `1.1.`, etc.
   ```python
   SUMARIO_RE = re.compile(
       r"^\s*(?:\d+(?:\.\d+)*[\.\)]?\s+)?(?:PORTARIA|DESPACHO|AVISO|EXTRATO|ATA|DECISÃO|RESOLUÇÃO|EDITAL|COMUNICADO|RETIFICAÇÃO)",
       re.IGNORECASE,
   )
   ```

3. **Atos individuais** — cada publicação com tipo + número + ano.

4. **Fecho** — assinatura da autoridade.

## Padrões de atos (validados)

### Formato com número: `TIPO [Nº] NNN[/AAAA]`
```python
ACTO_HEADER_RE = re.compile(
    r"^(?P<tipo>(?:PORTARIA\s*(?:CONJUNTA|CONJ|NORMATIVA|CONJUNTA\s*NORMATIVA|"
    r"CONJUNTA\s*ADMINISTRATIVA)?|"
    r"DESPACHO(?:\s*(?:ADMINISTRATIVO|DA\s*DIREÇÃO|DA\s*SECRETARIA))?|"
    r"AVISO|EXTRATO\s*(?:DE\s*)?(?:INEXIGIBILIDADE|DISPENSA|CONTRATO|"
    r"CONV[EÊ]NIO|ACORDO\s*(?:DE\s*)?COOPERAÇÃO|TERMO\s*(?:ADITIVO|DE\s*)?)?|"
    r"ATA\s*(?:DE\s*)?(?:REGISTRO\s*DE\s*PREÇOS|SESSÃO)?|"
    r"DECISÃO|RESOLUÇÃO|INSTRUÇÃO\s*NORMATIVA|"
    r"EDITAL|COMUNICADO|RETIFICAÇÃO|ERRATA|"
    r"ATO\s*(?:DO\s*(?:PROCURADOR|DIRETOR|SECRETÁRIO))?|"
    r"RECOMENDAÇÃO|NOTIFICAÇÃO|INTIMAÇÃO|CITAÇÃO|"
    r"REQUERIMENTO|OFÍCIO|MEMORANDO|PARECER|RELATÓRIO"
    r"))\s*(?:N[º°ª]|N[úu]mero)?\s*(\d+(?:\.\d+)?(?:[A-Z])?)\s*(?:/\s*(\d{4}))?\b",
    re.IGNORECASE,
)
```

### Formato sem número: `NOME DO ATO [Nº NNN]`
```python
ACTO_SIMPLE_RE = re.compile(
    r"^(?P<tipo>(?:PORTARIA|DESPACHO|AVISO|EXTRATO|ATA|DECISÃO|RESOLUÇÃO|"
    r"INSTRUÇÃO\s*NORMATIVA|EDITAL|COMUNICADO|RETIFICAÇÃO|ERRATA|"
    r"ATO|RECOMENDAÇÃO|NOTIFICAÇÃO|INTIMAÇÃO|CITAÇÃO|"
    r"REQUERIMENTO|OFÍCIO|MEMORANDO|PARECER|RELATÓRIO)"
    r"(?:\s+(?:N[º°ª]\s*)?\d+(?:\.\d+)?)?[:\s]",
    re.IGNORECASE,
)
```

## Tipos de ato detectados (25+)

| Categoria | Tipos |
|-----------|-------|
| **Portarias** | PORTARIA, CONJUNTA, NORMATIVA, CONJUNTA NORMATIVA, CONJUNTA ADMINISTRATIVA |
| **Despachos** | DESPACHO, ADMINISTRATIVO, DA DIREÇÃO, DA SECRETARIA |
| **Extratos** | EXTRATO DE INEXIGIBILIDADE, DISPENSA, CONTRATO, CONVÊNIO, ACORDO DE COOPERAÇÃO, TERMO ADITIVO |
| **Atas** | ATA DE REGISTRO DE PREÇOS, ATA DE SESSÃO |
| **Atos** | ATO, DO PROCURADOR, DO DIRETOR, DO SECRETÁRIO |
| **Outros** | AVISO, DECISÃO, RESOLUÇÃO, INSTRUÇÃO NORMATIVA, EDITAL, COMUNICADO, RETIFICAÇÃO, ERRATA, RECOMENDAÇÃO, NOTIFICAÇÃO, INTIMAÇÃO, CITAÇÃO, REQUERIMENTO, OFÍCIO, MEMORANDO, PARECER, RELATÓRIO |

## Scripts do fluxo (fonte da verdade: OPS)

| Script | Função | Local |
|--------|--------|-------|
| `audit_boletim.py` | Auditoria de extração de BS (3 camadas: pré-visão, estrutural, extração+auditoria) | `hermes_mpt_ops/scripts/` |
| `decode_boletins.py` | Decodifica base64 → PDF (saída do browser_console) | `hermes_mpt_ops/scripts/` |

Uso do audit:
```bash
python3 audit_boletim.py <BS.pdf>              # camadas 1+2+3 (inventário + extrai MD + audita)
python3 audit_boletim.py <BS.pdf> --sem-extracao   # só camadas 1+2
python3 audit_boletim.py <BS.pdf> --saida DIR      # grava em DIR (padrão: /workspace)
```

## Amostra real

⚠️ **Atenção (06/08/2026):** o primeiro "boletim" baixado
(`BS-119-2026-03-07.pdf`, via `requests` em 05/08) **não era um boletim** — era
a **página de bloqueio do WAF** do mpt.mp.br ("Página bloqueada!", Attack ID,
Message ID). Foi removido do KB. Lição: **sempre validar o conteúdo do PDF
baixado antes de arquivar** — checar se começa com "BS Eletrônico" e não com
"Página bloqueada!". Downloads via `requests`/curl capturam a página de erro;
o fluxo correto é browser completo (ver SKILL.md).

## Pitfalls

- **WAF do mpt.mp.br bloqueia requests/curl** — retorna página de bloqueio
  ("Página bloqueada! / Attack ID: NNN") em vez do PDF. Sempre validar o
  conteúdo antes de arquivar; usar o fluxo via browser (browser_console + fetch).
- **Amostras pequenas distorcem fidelidade por volume** — mesmo comportamento
  do PGEA (ver skill `analise-pgea`); comparar por conteúdo em páginas curtas.
- **Fontes não embedadas** (PDFs gerados por Word) → texto corrompido no pymupdf.
- **PDFs escaneados** → páginas vazias na camada 1 → exigem OCR (Tesseract).
