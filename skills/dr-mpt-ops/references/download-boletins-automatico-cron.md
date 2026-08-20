# Download automático de boletins novos (cron watchdog) — 20/08/2026

Pipeline que baixa automaticamente os boletins novos do MPT, substituindo o
download manual mês a mês. Criado e validado em 20/08/2026.

## Script canônico

`hermes_mpt_ops/scripts/baixar_boletins_novos.py` (versionado). Wrapper para
cron: `~/.hermes/scripts/baixar-boletins-novos.py` (runpy → OPS).

## O que ele faz (5 etapas)

1. Consulta o **mês corrente** no Portal da Transparência (reusa
   `baixar_boletim.py` + cloudscraper)
2. **Compara** com os boletins já baixados (`hermes_mpt_kb/raw/boletins/BS-*-<ano>.pdf`)
3. **Baixa só os novos** (via `baixar_boletim.py --baixar <numero>`)
4. **Extrai PDF→MD** (`extrair_md_boletins.py`)
5. **Regenera o índice CSV** (`exportar_atos_formatos.py` → `data/indices/atos_normativos.csv`)

## Padrão watchdog (crítico)

O cron roda `no_agent` **diário às 06:00** (`0 6 * * *`). Para não entregar
mensagem todo dia, o script **sai em silêncio (exit 0, stdout vazio) quando não
há boletins novos** — o cron `no_agent` não entrega nada com stdout vazio.
Só imprime quando:
- Há novos → imprime resumo + baixa + extrai + regenera índice (entrega)
- Portal sem resposta (WAF/servidor) → imprime alerta e retorna 1 (entrega erro)

**Estrutura do main para isso:** detectar `novos` ANTES de qualquer `print`;
se `not novos: return 0` imediatamente; só imprimir a partir do ponto em que há
novos. Não colocar prints de cabeçalho ("Mês alvo", "Boletins locais"...) antes
da verificação de novos — senão o stdout nunca fica vazio.

## Detecção de "novos"

- Boletins locais = conjunto de números de `BS-*-<ano>.pdf` na pasta.
- Portal = lista de `{indice, numero, data}` parseada da tabela `tabelaArquivos`.
- Novos = `[b for b in portal if b["numero"] not in locais]`.

## Incompatibilidade catalogar_atos.py (importante)

O `catalogar_atos.py` espera **pastas `YYYY-MM-DD`** com MDs dentro, mas a
padronização de armazenamento atual é **MD plano** em `hermes_mpt_kb/boletins/*.md`
(desde 19/08/2026). Então o pipeline de indexação **NÃO usa `catalogar_atos.py`**
— usa `exportar_atos_formatos.py` (que lê MDs planos) para gerar o CSV do índice.

## Validação (20/08/2026)

- Baixou 4 boletins novos (149, 149.1, 150, 151/2026) que faltavam.
- Índice atualizado de 11.350 → 11.427 atos.
- Re-execução confirmou 0 novos (idempotente, silencioso).
