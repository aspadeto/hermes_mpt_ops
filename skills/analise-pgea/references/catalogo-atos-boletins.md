# Catálogo de atos normativos a partir de Boletins de Serviço (pipeline SQLite)

> Validado em ago/2026 com os 10 primeiros boletins (nov/2024) como piloto, antes
> de expandir para ~420 boletins (nov/2024 → hoje). Objetivo: indexar atos
> normativos (regulamentos de funcionamento de processos administrativos) para,
> no futuro, cruzar com os assuntos discutidos em cada PGEA/processo.

## Arquitetura e convenção de pastas

- **Boletins em pastas `YYYY-MM-DD`** (ordenação e visualização): cada pasta tem
  `BS-<n>-<ano>.pdf` + `<nome>.md` (extração) + `auditoria_<nome>.md`.
  Ex.: `boletins/2024-11-04/BS-210-2024.pdf`, `BS-210-2024.md`, `auditoria_BS-210-2024.md`.
- **Banco SQLite versionado:** `hermes_mpt_ops/data/atos.db` (`.gitignore` tem
  exceção `!data/atos.db` — igual a `pendencias.db`/`processos.db`).
- **Script (fonte da verdade no OPS):** `hermes_mpt_ops/scripts/catalogar_atos.py`.

### Esquema do banco

```
boletins(id, data YYYY-MM-DD, numero "210/2024"|"210.1/2024", pdf, md)
atos_normativos(id, boletim_id FK, tipo, numero, ano, orgao, data_ato,
                pagina, secao, ementa, relevante, observacao)
```

- `relevante=1` sinaliza atos que **regulamentam o funcionamento de processos
  administrativos** (preenchido por curadoria, não automaticamente).

## Uso

```bash
cd hermes_mpt_ops
# venv com cloudscraper + pymupdf (criar uma vez)
.venv-bol/bin/python scripts/catalogar_atos.py \
  --raiz /opt/data/hermes-data/boletins \
  --db /opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/data/atos.db --recriar
```

O parser detecta cada ato pelo gatilho real no texto (não pelas seções `##` do
auditor, que são imprecisas):
- `Nº 1529, DE 30 DE OUTUBRO DE 2024` (número+data numa linha)
- `PORTARIA Nº 1030/2024` (tipo+número explícito)
- precedido pela seção (`PORTARIAS`, `DECISÃO`, `EDITAIS`...) e seguido do órgão.

**Dedup:** remove atos repetidos com mesmo `(tipo, numero, pagina)` — o número
costuma aparecer no sumário E no corpo. Mantém o 1º que tem ementa/órgão.

## Detecção do cabeçalho de ato (padrões)

O `audit_boletim.py` detecta por **primeira linha significativa de cada página**,
o que falha em dois casos:

1. **Ato começa no meio da página** (comum — vários atos por página): o gatilho é
   a linha `Nº NNN, DE DD DE MÊS DE AAAA`, não o topo da página. O `catalogar_atos.py`
   varre TODAS as linhas do `.md`, não só o topo de página.
2. **Boletins EXTRAORDINÁRIOS (`nº .1`, `.2`):** o auditor detecta **0 atos** e NÃO
   gera o `.md` (estrutura separa tipo e número em linhas distintas: "EDITAIS" e,
   na linha seguinte, "Nº 82, DE 4 DE NOVEMBRO DE 2024"; cabeçalho "BSE EXTRAORDINÁRIO").
   → Gerar o `.md` manualmente com pymupdf (`doc[i].get_text()` por página +
   marcadores `<!-- pág N -->`), sem passar pelo auditor.

## Falso positivo de "Resolução"

Seções `## Resolução` do auditor podem ser na verdade o **rodapé/fecho de um ato
anterior** (ex.: "1. Registre-se e publique-se... Brasília, 6 de novembro de
2024"). Sempre conferir o conteúdo antes de catalogar como resolução.

## Curadoria (`relevante`)

A marcação `relevante=1` é **manual por leitura de conteúdo** (não automática):
- Marca atos normativos que regulam o funcionamento de processos administrativos
  (organização de unidades, atribuições de ofícios, distribuição, prazos, comitês,
  manuais de atividade finalística, regimentos).
- NÃO marca atos de mero expediente: designação de fiscais de contrato, licenças,
  escalas de plantão, substituições, nomeações.
- Para escalar (~420 boletins): primeiro rodar o parser, depois filtrar candidatos
  por palavras-chave no corpo (`Institui`, `Altera`, `Regulamenta`, `Manual`,
  `Comitê`, `Regimento`, `Resolução`) e revisar em lote antes de marcar.

## Exemplos reais (nov/2024)

| Ato | Boletim/pág | Assunto |
|-----|-------------|---------|
| Resolução CSMPT nº 222/2024 | BS-212/2024, p. 24-27 | organização das unidades, atribuições dos ofícios, distribuição (livre/prevenção), autuação e cadastramento de procedimentos finalísticos (transcrita integralmente) |
| Portaria PRT14 nº 177/2024 | BS-212/2024, p. 22 | aprova o Manual de Suporte à Atividade Finalística da PRT14 |
| Portaria PGT nº 1640/2024 | BS-216/2024, p. 4 | institui o Comitê de Governança de IA (CGIA) |
| Portaria PGT nº 1625/2024 | BS-216/2024, p. 4 | altera o Regimento Interno Administrativo (SIGR) |
| Portaria PGT nº 1471/2024 | BS-213/2024, p. 3 | instituiu o CGIA (revogada e recriada) |

## Ordem de expansão (seguir para o restante)

nov/2024 completo → dez/2024 → jan/2025 … dez/2025 → jan/2026 → fev/2026 … hoje.
Consultar cada mês com `baixar_boletim.py <ano> <MES>` para descobrir o intervalo
de números antes de baixar (`--baixar todos --dir ...`).
