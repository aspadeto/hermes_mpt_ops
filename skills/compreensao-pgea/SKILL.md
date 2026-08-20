---
name: compreensao-pgea
description: "Compreensão causal de PGEAs: linha do tempo e padrões."
version: 0.1.0
author: HAL 9000
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [pgea, compreensao, causalidade, linha-do-tempo, padroes, processos]
    category: analise
    related_skills: [analise-pgea, dr-mpt-ops]
---

# Compreensão Causal de PGEAs

Complemento à `analise-pgea` (extração/auditoria) e ao `extrair_auditar_pgea.py`
(completude/fidelidade). Esta skill trata a **dimensão diacrônica e causal** do
processo: cada PGEA é um encadeamento de documentos em ordem cronológica com
lógica consequencial — causa primeira → documentos acumulativos → resultado
último. O objetivo é duplo:

1. **Por processo:** gerar conhecimento específico para tomada de decisão
   (onde está, por que, o que falta).
2. **Entre processos:** construir generalizações / desenhos padronizados de
   processos (estágios canônicos reutilizáveis).

## Quando Ativar

- Usuário pedir "compreensão", "dinâmica", "linha do tempo causal" ou
  "entendimento do processo" de um PGEA
- Analisar um PGEA para decisão (deferir/indeferir, próximo trâmite)
- Comparar PGEAs para derivar um desenho padrão de processo
- Alimentar a base de padrões (`processes/padroes/`)

## Pré-requisito (decisão do usuário — ago/2026)

**Usar APENAS PGEAs que passaram pelo `extrair_auditar_pgea`** (extração fiel: inventário
de peças completo, zero páginas órfãs, fidelidade conferida). Compreensão sobre
extração não auditada herda erros de extração. Verificar em
`hermes_mpt_ops/data/auditorias/auditoria-pgea-<n>-<ano>.md` antes de começar.

## Modelo de Compreensão (3 dimensões por documento)

Cada peça do PGEA é classificada em:

### 1. Tipo de ato (já vem do inventário da auditoria)
Requerimento, Despacho, Relatório, Juntada, Ofício, Decisão, Minuta, Cópia...

### 2. Função causal (o que o documento FAZ no processo)

**Vocabulário ABERTO e extensível** (decisão do usuário — ago/2026): as 6
funções abaixo são o núcleo, mas novos tipos de ato podem exigir funções novas.
Exemplos reais: **Parecer Jurídico** (análise prévia de conformidade) e
**Análise de Conformidade** do setor específico (ocorre depois da liquidação em
processos de pagamento). Sempre que uma peça não encaixar nas 6, criar a função
nova em vez de forçar.

| Função (núcleo) | Emoji | Exemplo |
|--------|-------|---------|
| **Origem** (causa primeira) | 🔵 | Requerimento que abre o processo; portaria normativa externa que o motiva |
| **Instrução** | 📥 | Juntada, cópia, orçamento — alimenta o processo |
| **Movimentação** | 🔄 | Despacho de encaminhamento — move entre setores |
| **Manifestação** | 🧾 | Relatório, parecer — opina |
| **Decisão** | ⚖️ | Deferimento/indeferimento — resolve |
| **Execução/Desfecho** | 📤 | Providências finais — fecha |
| *Parecer Jurídico* | ⚖️/🧾 | Análise prévia de conformidade (extensão) |
| *Análise de Conformidade* | ✅ | Verificação do setor específico, ex: pós-liquidação (extensão) |

### 3. Estágio resultante do processo
`Abertura → Instrução → Análise → Decisão → Execução → Encerramento`

**Regra de ouro da cadeia:** cada documento *habilita* o próximo (causa →
efeito). Despacho de encaminhamento sem peça seguinte = **processo parado**;
decisão sem despacho de execução = **desfecho pendente**.

**Marco inicial (decisão do usuário — ago/2026):** o melhor marco é o
**Despacho ou documento assinado por dirigente/chefe que dá o impulsionamento
inicial** do processo (ex: Despacho 000786/2026 no 337, assinado por Victor
Gustavo Bernardes da Silva — encaminha à DTI). Na falta de documento do
dirigente/chefe/requerente, usar outro documento (ex: portaria normativa).

**Causa primeira externa:** marcos normativos fora dos autos (ex: Portaria
PGT 646/2026 que restringe uso de SMP) podem ser a causa material real —
registrar como contexto normativo externo, distinguindo do marco inicial
formal dos autos (validar com o usuário quando houver dúvida).

## Artefato por processo: `compreensao.md`

Criar em `pgeas/pgea-XXX/compreensao.md`:

```
## 🧬 Linha do tempo causal
| # | Data | Documento/Peça | Evento | Efeito no processo | Estágio |

## 🔗 Cadeia causal (causa → efeito)
- [Requerimento] → habilita → [Juntada] → ... → [Apóstila]

## 🧭 Estágio atual + desvios
- Onde está vs. onde o desenho padrão esperaria
- Gargalos, atos fora de ordem, documentos sem efeito
```

A coluna **"Efeito no processo"** é a chave: cada documento não é só um item —
é um ato que move (ou deveria mover) o processo de estágio.

## Padrões entre processos: `processes/padroes/`

Generalizações derivadas das linhas do tempo causais:

- `processes/padroes/<tipo>.md` (ex: `padrao-aquisicao-material.md`)
- Estrutura: estágios canônicos (responsável + documento esperado por estágio),
  pontos de decisão, riscos típicos, casos reais como referência
- Exemplo real identificado: *demanda do PCA → autorização → cotação → TR →
  aprovação → licitação* é o esqueleto de todo PGEA de compra

## Banco: `processos.db` (decisão do usuário)

- **Banco NOVO** `hermes_mpt_ops/data/processos.db` (NÃO estender
  `regional-orcamento.db`)
- Tabela `eventos`: `(processo, seq, data, peca, tipo_ato, funcao_causal,
  efeito, estagio)` — permite cruzar: tempo entre estágios, processos parados
  por setor, desenhos mais comuns

## Automação: script `compreender_pgea.py` (implementado — ago/2026)

Script versionado em `hermes_mpt_ops/scripts/compreender_pgea.py` (regras
primeiro, LLM só na dúvida):

```bash
python3 compreender_pgea.py <extracao.md>               # rascunho da tabela em stdout
python3 compreender_pgea.py <extracao.md> --saida ARQ.md  # grava rascunho em arquivo
python3 compreender_pgea.py <extracao.md> --duvidas       # só os pontos incertos p/ revisão
```

- **Regras (zero custo):** ordenação por data, tipo de ato via `HEADER_RE`
  reutilizado do `extrair_auditar_pgea.py`, função causal por heurística de
  tipo de peça + verbo do despacho ("encaminhe-se" → movimentação;
  "autoriz/defer" → decisão; "design" → movimentação; "cientif/informo" →
  instrução; "suger/opino" → manifestação; "providenc" → execução)
- **LLM/agente só na dúvida:** o script marca `⚠️` as linhas com data ausente
  ou efeito não capturado (`--duvidas` lista) — o agente revisa e refina,
  mesmo padrão do audit (relatório, nunca bloqueio)
- **Saída:** rascunho da tabela de eventos → revisar → gravar em
  `compreensao.md` + inserir no `processos.db`

## Piloto (CONCLUÍDO e validado — ago/2026)

PGEAs escolhidos (todos auditados, extração fiel — ver `OPS/data/auditorias/`):

| PGEA | Assunto | Desenho causal | Estágio atual |
|------|---------|----------------|---------------|
| 337/2026 | Serviço Móvel Pessoal (SMP) | Apuração normativa → 2 decisões DG → desfecho | 📤 Execução |
| 372/2026 | Aquisição de lixeiras | Pedido (PCA) → cotações → TR 69/2026 → aguarda aprovação da DR | ⚖️ Decisão (bloqueado 7d) |
| 281/2026 | Desativação da Biblioteca | Ordem do Procurador-Chefe → levantamento → inventário → relatório conclusivo | ⚖️ Decisão (aguarda destinação) |

**Validações do usuário (05/08/2026) — todas incorporadas:**
1. Modelo de 6 funções: **ok**, mas vocabulário deve ser **aberto/extensível**
   (ex: Parecer Jurídico, Análise de Conformidade pós-liquidação)
2. Marco inicial: **despacho de impulsionamento do dirigente/chefe** (fallback:
   requerimento/portaria)
3. Banco: `processos.db` novo (não estender `regional-orcamento.db`)
4. Automação: **regras + LLM** (script `compreender_pgea.py`, regras primeiro)

Artefatos do piloto: `compreensao.md` em `pgeas/pgea-337-2026/`,
`pgeas/pgea-372-2026/` e `pgeas/pgea-biblioteca/` (281) — 52 eventos em
`processos.db` (OPS). Padrões derivados → `processes/padroes/`
(`padrao-aquisicao-material.md`, `padrao-regularizacao-normativa-externa.md`).

## Cruzamentos úteis no `processos.db`

Consultas que transformam os eventos em conhecimento acionável (validadas no
piloto — ver `references/cruzamentos-processosdb.md`): estágio atual por
processo, tempo total decorrido (autuação → último evento), dias parados,
distribuição de funções causais, gargalos (movimentação sem decisão seguinte).
Exemplo de insight real: 2 de 3 processos parados na Diretoria (decisão) =
gargalo setorial identificado.

## Pitfalls

- **Não confundir com `analise.md`:** análise é diagnóstico do momento atual;
  compreensão é a narrativa causal completa. A compreensão ALIMENTA a análise
  (ela consome `extracao.md` + inventário da auditoria, não relê o PDF).
- **Extrações grandes:** 337 tem 124KB / 372 tem 107KB — resumir por peça
  (regex de seções `##`, datas, verbos de ato) antes de montar a cadeia, para
  não inundar o contexto.
- **Datas ausentes em juntadas:** juntadas costumam não ter data própria no
  texto (ex: Juntadas 004592-004595 do 372) — inferir pela peça seguinte ou
  pelo intervalo da auditoria.
- **HEADER_RE do `extrair_auditar_pgea.py` NÃO casa título de seção `##`:** o
  regex original espera o sufixo `− PGEA <num>` (presente no corpo da página),
  mas o título da seção no MD é só `TIPO NUM (ID)` — o `compreender_pgea.py`
  retornava ZERO peças. Correção: sufixo opcional
  `(?:[−-]\s*PGEA\s)?$` no HEADER_RE local do script. Ao reutilizar regex do
  audit, conferir se o alvo (título vs. corpo) tem o mesmo formato.
- **Efeito de juntadas captura cabeçalho repetido:** juntadas têm o cabeçalho
  da peça repetido no corpo — a heurística de efeito pega essa linha em vez do
  conteúdo real. Filtrar linhas iguais ao nome da peça antes de extrair o efeito.
