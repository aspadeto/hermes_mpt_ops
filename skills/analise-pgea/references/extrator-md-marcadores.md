# Padrão do Extrator MD com Marcadores (pré-requisito da Camada 3)

Validado em 04/08/2026 com PGEA 281 (36 págs) — extração em `/workspace/` via pymupdf,
auditada com `scripts/extrair_auditar_pgea.py` (14/14 peças, 35/35 páginas, texto idêntico).

## Objetivo

Gerar o Markdown de extração de um PGEA de forma que a Camada 3 (auditoria da extração)
consiga compará-lo com o PDF original automaticamente. O MD precisa de **dois contratos
de formato**:

1. **Uma seção `##` por peça**, com a chave = nome COMPLETO `TIPO NUM (ID)` do cabeçalho
   dos autos digitais (ex: `## Juntada 002739.2026 (9449882)`).
2. **Marcador `<!-- pág N -->`** no início do texto de cada página — permite conferir
   cobertura (todas as páginas saíram?) e fidelidade página a página.

## Estrutura do script

```python
import fitz, re
from pathlib import Path

HEADER_RE = re.compile(
    r"^(?P<tipo>[A-ZÀ-Úa-zà-ú ]+?)\s+(?P<num>\d{5,6}\.\d{4})\s*\((?P<id>\d{7,8})\)\s*[−-]\s*PGEA\s",
    re.IGNORECASE,
)

doc = fitz.open(PDF)
secoes = []          # (titulo_completo, [textos])
atual = None
capa = []

for i in range(doc.page_count):
    txt = doc[i].get_text().strip()
    if not txt:
        continue
    if i == 0:
        capa.append(txt)
        continue
    peca = None
    for linha in txt.splitlines():
        linha = linha.strip()
        if len(linha) < 10:
            continue
        m = HEADER_RE.match(linha)
        if m:
            peca = f"{' '.join(m.group('tipo').split())} {m.group('num')} ({m.group('id')})"
        break
    if peca:
        if peca != atual:          # ⚠️ só abre seção quando a peça MUDA
            atual = peca
            secoes.append([peca, []])
    if atual:
        secoes[-1][1].append(f"\n<!-- pág {i+1} -->\n{txt}")
doc.close()
```

Saída: `## Capa` + uma `## <TIPO NUM (ID)>` por peça, cada página com seu marcador.

## Pitfalls (todos encontrados na prática)

| Pitfall | Sintoma | Correção |
|---------|---------|----------|
| Chave da seção só com o TIPO | "Juntada 002739" e "Juntada 002740" colapsam → 12 seções p/ 14 peças | Usar `TIPO NUM (ID)` completo |
| Abrir seção em toda página com cabeçalho | 33 seções para 14 peças reais | `if peca != atual:` antes de abrir |
| `doc.page_count` após `doc.close()` | `ValueError: document closed` | Guardar `TOTAL_PAGS` antes do close |
| Fidelidade por volume em página pequena | razão 1.28–1.43 em páginas de 127–191 chars (folhas de rosto) — falso positivo | Judge confere por CONTEÚDO (byte a byte) — o marcador `<!-- pág N -->` (~18 chars) distorce a razão em páginas < ~300 chars |

## Tipos de peça já vistos (PRT14, ago/2026)

Despacho Comum Administrativo, Juntada, Manifestação do Servidor, Relatório,
Cópia de documento, Ofício, Decisão Administrativa, Outras Providências,
Elaboração de Minuta, Requerimento. **Não confiar em lista fixa** — o detector
genérico pelo cabeçalho captura qualquer tipo.

## Notas de página

- Página 1 (capa) e as últimas (assinaturas, "Histórico gerado em") **não têm cabeçalho
  de peça — é esperado**, não é erro de extração.
- PDFs dos autos digitais MPT são 100% digitais (zero páginas vazias → sem OCR).
  Se a Camada 1 acusar páginas vazias, aí sim avaliar OCR.
