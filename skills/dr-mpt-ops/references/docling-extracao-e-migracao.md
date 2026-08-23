# Docling: extração de atos + migração das ferramentas de busca (ago/2026)

Contexto da pendência #41 (unificar gerações de pesquisa) e da decisão #35
(boletins docling = representação canônica). Como migrar as ferramentas que
lêem o MD **plano** (`boletins/`) para o corpus **docling** (`boletins_docling/`).

## ⚠️ Diferença estrutural crítica: docling põe a ementa ANTES do heading

O parser do MD plano (`catalogar_atos.py`) assume **número primeiro, ementa
depois**:

```
Nº 56, DE 15 DE JANEIRO DE 2025     ← cabeçalho
<ementa/órgão/texto>                ← o que segue
```

No docling é o **oposto** para atos que têm tabela/anexo: o corpo do ato
(ementa, órgão, artigos, tabelas) vem **ANTES** do heading que marca o número:

```
Altera a estrutura organizacional da PRT10 ...   ← ementa vem antes
O DIRETOR-GERAL ... RESOLVE: ...
Art. 1º ...
## Nº 56, DE 15 DE JANEIRO DE 2025               ← heading do número no fim
```

**Consequência:** extrair `ementa`/`tipo` olhando o trecho **seguinte** ao
heading `## Nº` falha (pega resíduo de tabela/anexo ou nada). Número, boletim,
data e ano ficam corretos; **tipo/ementa podem sair imperfeitos**. Para o
`tipo`, mitigar com heurística `_inferir_tipo_de_trecho` (Designar/Nomear/
Altera a Portaria/estrutura organizacional→PORTARIA; RESOLVE/RESOLVO→DECISÃO),
mas ela só funciona quando a ementa está no trecho seguinte — não quando o
docling a colocou antes.

## Padrões reais do docling para detecção de atos

- Ato como heading:  `## Nº 56, DE 15 DE JANEIRO DE 2025`
- Ato como linha:    `Nº 1124, DE 4 DE AGOSTO DE 2025` (linha solta, sem `##`)
- Tipo+num explícito: `## DECISÃO N°111.2025` / `## DESPACHO Nº 1663.2025`
- Seções:            `## PORTARIAS`, `## ATOS DO PROCURADOR-GERAL`,
                     `## ATOS DAS PROCURADORIAS REGIONAIS`
- Nomes próprios     `## GLÁUCIO ...` / `## ANDERSON ...` (não são atos)
- Variação de dia:   `1°` / `1º` (ex.: `DE 1° DE AGOSTO DE 2025`)
- Marcador de página: `<!-- image -->` (docling NÃO usa `<!-- pág N -->`)
- **SEM frontmatter**: o ano vem do NOME do arquivo `BS-012-2025` → 2025
- Data de circulação: `CIRCULAÇÃO: DD/MM/AAAA` ou capa `SEGUNDA-FEIRA, DD DE MÊS DE AAAA`

## Regex

- Número do ato: `N[º°\.]` (aceita Nº, N°, N.) — o parser plano só usava `Nº`.
- Precedência de detecção por linha:
  1. `<!-- image -->` → incrementa página
  2. heading `## <seção>` → atualiza seção (PORTARIAS, ATOS DA ...)
  3. `## DECISÃO N°...` (tipo explícito) → ato
  4. `## Nº X, DE ...` (heading) → ato
  5. linha solta `Nº X, DE ...` → ato

## Scripts (Fase 1 — regenerar CSV do docling)

- `scripts/detectar_atos_docling.py` — parser docling-aware.
  Função principal: `atos_por_arquivo_docling(md)`.
- `scripts/exportar_atos_docling.py` — gera `atos_normativos.{csv,md,tsv,toml}`
  a partir de `boletins_docling/`. Mesmas 11 colunas do antigo.
- Resultado baseline: **11.856 atos** em 512 boletins docling (antigo 11.427
  em 508 planos). Validação das 5 perguntas: boletim/número/data corretos.

## Estratégia de migração acordada (pendência #41)

1. **Fase 1** — regenerar o CSV a partir do docling (novos scripts; NÃO mexer
   no antigo `exportar_atos_formatos.py` até validar).
2. **Fase 2** — segmentar as pesquisas: cada base com **um script separado**
   (ex.: `pesquisar_boletins_csv.py` factual/CSV + `pesquisar_boletins_fulltext.py`
   full-text docling). Descontinuar o híbrido `pesquisar_boletins.py`.
3. **Fase 3** — migrar o full-text para docling (deixar de ler `boletins/`).

Regras do usuário:
- **Sempre partir do docling** quando for regenerar conteúdo (CSV, índices).
- Trabalhar **um script por vez, interativo, com confirmação** antes de editar.
- Baseline aceito: melhorar tipo/ementa **depois**, no benchmark das 5 perguntas.

## Pitfalls

- **Auto-commit race:** os scripts novos podem ser commitados pelo cron de
  10min ANTES do commit manual. Não é erro — conferir `git ls-files` e
  `git log --oneline -3 -- <arquivo>` antes de supor que faltou versionar.
- **Não sobrescrever o CSV oficial sem backup:** `cp` do antigo para `/tmp/`
  antes de adotar o gerado do docling.
- **O `pesquisar_docling.py` (POC) tem mapeamentos hardcoded** para 5 perguntas
  específicas — não é uma busca genérica; serve como referência de ground-truth,
  não como motor de produção.
