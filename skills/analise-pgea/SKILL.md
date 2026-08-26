---
name: analise-pgea
description: "Análise de PGEAs (Procedimentos de Gestão Administrativa) do MPT: extração, análise técnica, identificação de padrões e criação de processos de trabalho."
version: 1.1.2
author: HAL 9000
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [pgea, analise, mpt, processo, orcamento]
    category: analise
    related_skills: [llm-wiki]
---

# Análise de PGEAs (MPT)

Habilidades para processar, analisar e extrair valor de PGEAs (Procedimentos de Gestão Administrativa) do MPT.

## Quando Ativar

Use esta skill quando o usuário:
- Enviar um PGEA para processamento (PDF, extração do Copilot, ou texto)
- Pedir análise técnica de um PGEA (riscos, orçamento, legal)
- **Pedir para comparar PGEAs ou identificar padrões** → para a dimensão causal (linha do tempo, cadeia causa→efeito, estágios) e generalizações entre processos, usar a skill **`compreensao-pgea`** (consome `extracao.md` + inventário da auditoria; gera `compreensao.md` + `processes/padroes/` + `processos.db`)
- Perguntar sobre o andamento de uma iniciativa registrada como PGEA
- Quiser criar um processo de trabalho a partir de PGEAs similares
- **Mencionar PGEA de Contratação, aditivo, apostilamento, prorrogação ou reequilíbrio contratual** — subtipo específico com lifecycle próprio e processos de trabalho embutidos (ver seção "PGEAs de Contratação" abaixo)
- **Validar extração de PGEAs** ("a extração ficou completa/correta?") — auditoria de completude e identificação de peças (ver seção "Auditoria de Extração" abaixo). RAG/busca semântica foi **adiado** pelo usuário (#10 refeita ago/2026) — não propor RAG como solução atual

## Estrutura de Armazenamento

```
wiki/
├── pgeas/                          ← PGEAs da PRT14 (em andamento)
│   ├── index.md                    ← Catálogo com status
│   ├── pgea-biblioteca/            ← Cada PGEA em sua pasta
│   │   ├── resumo.md               ← Dados gerais + status + despachos
│   │   ├── analise.md              ← Análise técnica completa
│   │   └── extracao.md             ← Texto extraído (PDFs ficam em raw/pgeas/)
│   ├── pgea-385-2026/
│   └── pgea-434-2026/
│
├── modelos/                        ← PGEAs de outras Regionais (referência)
│   ├── index.md
│   ├── prt10-desfazimento-2025/
│   └── prt10-inventario-2024/
│
├── processes/                      ← Processos de trabalho criados a partir de PGEAs
│   └── gestao-patrimonial/
│       └── processo-reembolso-abastecimento.md
│
└── data/                           ← Banco SQLite para dados estruturados
    ├── regional-orcamento.db
    └── scripts/
        ├── importar-demandas.py
        ├── importar-execucao.py
        └── consultar.py
```

## Numeração de PGEAs

Formato: `20.02.XXXX.NNNNNNN/AAAA-DV`

| Campo | Descrição |
|-------|-----------|
| `20` | Tipo de Unidade |
| `02` | Ramo do MP (02 = MPT) |
| `XXXX` | Código da unidade (1400=PRT14, 1000=PRT10, 1401=PTM Rio Branco, 1402=PTM Ji-Paraná) |
| `NNNNNNN` | Número sequencial (7 dígitos, zero-padded) |
| `AAAA` | Ano |
| `DV` | Dígito verificador |

O código indica onde o PGEA **nasceu**, mas pode tramitar nacionalmente.

## PGEAs de Contratação (subtipo especial)

### Características distintivas

PGEAs de Contratação são um subtipo de PGEA da área meio que documentam **toda a vida de um contrato**, da celebração à extinção. Diferem dos PGEAs comuns porque:

1. **Iniciam com cópia do contrato** original (celebrado no PGEA da licitação que o originou — o PGEA de licitação fica no setor de licitações; o PGEA de contratação fica com o gestor do contrato)
2. **Ficam ativos até a extinção do contrato** (podem durar anos)
3. **Contêm processos de trabalho EMBUTIDOS** — cada aditivo ou apostilamento é um mini-processo dentro do PGEA, com sua própria fundamentação, objeto, alterações e status
4. **Passam por fases cronológicas bem definidas**

### Fases do ciclo de vida

| Fase | Emoji | Descrição |
|------|-------|-----------|
| Abertura | 🔵 | Juntada do contrato original (vindo do PGEA da licitação) |
| Aditivo | 🟡 | Alteração contratual (prazo, valor, escopo) |
| Apostilamento | 🔵 | Correção pontual sem alteração de objeto |
| Prorrogação | 🟡 | Extensão de vigência |
| Reequilíbrio | 🔵 | Revisão econômico-financeira |
| Rescisão | 🔴 | Extinção antecipada |
| Encerramento | ⚫ | Fim natural da vigência |

### Extração de Processos de Trabalho embutidos

Para cada aditivo/apostilamento dentro do PGEA, extrair como processo autônomo:

```
### Nº TA — ADITIVO — [objeto resumido]
- **Tipo:** Aditivo | Apostilamento | Prorrogação | Reequilíbrio
- **Nº do termo:** [número]
- **Objeto:** [descrição completa]
- **Data:** [assinatura]
- **Fundamentação legal:** [lei/portaria]
- **Alterações:**
  - Prazo: [de/para]
  - Valor: [de/para]
  - Escopo: [descrição]
- **Status:** ✅ Concluído | 🔄 Em andamento | ⏳ Pendente
```

### Formato de saída para Telegram

PGEAs de Contratação devem ser apresentados neste formato enxuto (compatível com Telegram — emojis, tabelas compactas, sem formatação excessiva):

```
## 📋 Dados do Contrato
- Contrato: [CT-PRT14-Nº/AAAA]
- PGEA de origem (licitação): [PGEA]
- Contratada: [Razão Social] ([CNPJ])
- Objeto: [transcrição]
- Valor original: R$ XXX.XXX,XX
- Vigência: DD/MM/AAAA a DD/MM/AAAA
- Amparo legal: [Lei/Pregão/Dispensa]
- Gestor: [nome]

## 📊 Linha do Tempo
| Data | Evento | Documento |

## 🔄 Processos de Trabalho (Aditivos/Apostilamentos)
### Nº TA — ADITIVO — [objeto]
- Data: | Alterações: | Status:

## 💰 Evolução Financeira
| Período | Valor Anual | Variação | Instrumento |

Tabela que compara valores contratuais ao longo dos anos, mostrando o impacto acumulado de cada repactuação/aditivo. Exemplo real:

| Período | Valor Anual | Variação | Instrumento |
|---------|------------|----------|-------------|
| 2022 (original) | R$ 64.894 | — | Contrato |
| 2022 (pós-repact.) | R$ 71.361 | +10,0% | 1º Apostilamento |
| 2024-2025 | R$ 77.209 | +8,2% | 2º TA c/ repactuação |
| 2025-2026 | R$ 85.198 | +10,3% | 3º TA |
> **Valor acumulado estimado:** ~R$ 370.000,00 (2022-2026)

## 📑 Despachos
| Data | Autoridade | Decisão |

## 📎 Documentos Anexos

## ⚠️ Observações
```

### Prompt Copilot especializado

O arquivo `references/agente-copilot-pgea-contratacao.md` contém um prompt dedicado para o MS Copilot extrair PGEAs de Contratação já no formato Telegram acima. Usar quando o usuário pedir para criar ou melhorar o prompt de extração.

#### 🚫 Problema conhecido: Copilot escreve scripts Python

O Copilot M365 frequentemente tenta **escrever scripts Python** para processar o PDF em vez de simplesmente ler e formatar o texto. Isso acontece principalmente quando:
- O PDF é muito grande (>30 MB — Copilot tem limite de contexto)
- O prompt contém linguagem de "processar", "extrair", "mapear" que dispara modo programador

**Solução no prompt:** Inserir esta diretiva ABSOLUTA no topo do agente Copilot:

```
🚫 REGRA ABSOLUTA — NÃO PROGRAME, APENAS LEIA E FORMATE
NÃO escreva, execute ou sugira scripts Python, JavaScript, VBA ou qualquer código.
Use sua leitura nativa de PDF/DOCX para extrair o texto e formatar manualmente em Markdown.
Responda APENAS com o texto formatado — zero código, zero scripts.
```

**Solução alternativa:** Se o PDF for grande demais (>30 MB), extrair o texto localmente com pymupdf em vez de usar o Copilot.

## Fluxo de Processamento de PGEA

### 1. Receber e Extrair

Quando o usuário envia um PGEA (PDF, extração do Copilot, ou colado):

① **Identificar o PGEA:** número, assunto, autuação, unidade de origem
② **Classificar o subtipo:** é um PGEA de Contratação? (contém contrato + aditivos/apostilamentos) → seguir seção "PGEAs de Contratação" acima. É um PGEA comum? → seguir fluxo normal.
③ **Extrair texto** (se PDF → pymupdf; se Copilot → já vem formatado):
   - **Setup:** `uv venv .venv && uv pip install pymupdf` — necessário porque system Python tem PEP 668 (não permite --system)
   - **Comando:** usar `.venv/bin/python3` (não `python3`) para rodar scripts de extração
   - **Script de extração:** `hermes_mpt_ops/scripts/pdf2kb.py` (repo hermes_mpt_ops — o KB não guarda scripts; renomeado de `pdf2wiki.py` na migração de nomes neutros ago/2026)
   - **PDFs de artigos/legislação/relatórios (não-PGEA):** usar a skill `ingestao-pdf-wiki` — pipeline pdf2wiki (Markdown + tabelas + assets + indexacao.json para confirmação assíncrona via pendências) em `raw/articles/<slug>/`.
   - **PDFs grandes** (100+ páginas): usar `terminal(background=true, notify_on_complete=true)` — a extração pode levar minutos
   - **Ruído em DOUs:** PDFs concatenados podem incluir extratos de outras Regionais (PRT3, PRT9, PRT10 etc.) — focar apenas nos documentos da PRT14
   - **Convenção de pastas (desde jul/2026):** `raw/pgeas/` guarda APENAS os PDFs enviados pelo usuário. O texto extraído vai para `pgeas/pgea-XXX/extracao.md` — nunca salvar extrações dentro de `raw/pgeas/`.
④ Se for PGEA de Contratação, extrair também cada aditivo/apostilamento como processo de trabalho autônomo.

### 2. Criar Resumo

Arquivo: `pgeas/pgea-XXX/resumo.md`

Incluir:
- **Identificação** completa (número, assunto, servidor/requerente, valor, datas)
- **Histórico** (datas, movimentos, responsáveis) — tabela cronológica
- **Despachos** extraídos com síntese da decisão
- **Documentos anexos** listados
- **Situação atual** + estágio do processo

### 3. Criar Análise Técnica

Arquivo: `pgeas/pgea-XXX/analise.md`

#### Estrutura padrão da análise

Incluir estas seções SEMPRE (nesta ordem):

| Seção | Conteúdo |
|-------|----------|
| **📊 Situação Atual** | Último movimento + cadeia de eventos recentes (tabela data/autor/conteúdo) |\n| **🔍 Diagnóstico** | O que aconteceu, por que, contexto — em linguagem clara |\n| **⚠️ Pontos de Atenção** | Riscos, prazos expirados, valores retroativos, lacunas |\n| **📋 Próximos Trâmites** | Checklist com 3 horizontes (imediatos, curto prazo, médio prazo) |\n| **🧭 Fluxograma do Trâmite** | Diagrama ASCII mostrando onde o processo está (✅) e onde está ⏳ |\n| **💡 Recomendações** | Sugestões acionáveis e priorizadas |\n\n> ⚠️ A seção **🧭 Fluxograma** é obrigatória em análises de PGEAS em andamento. O usuário precisa visualizar rapidamente onde o processo está travado. Exemplo:\n> ```\n> SLC analisa conformidade ← Despacho 1310 (fulano)\n>         ↓\n> DOF certifica disp. orçamentária ← T.I. 064 ✅\n>         ↓\n> DR autoriza remanejamento ← ⏳ VC ESTÁ AQUI\n>         ↓\n> SGC lavra apóstila\n> ```\n\n#### Análise de remanejamento orçamentário (repactuação contratual)\n\nQuando o PGEA envolve pedido de repactuação com diferença entre valor solicitado e valor programado na demanda:\n\n1. **Extrair os números exatos** da certidão DOF:\n   - Valor anual atual vs. repactuado vs. programado\n   - Diferença mensal e impacto total (meses × diferença)\n   - Fonte do remanejamento indicada pelo DOF\n   - Elemento de despesa (ex: 339037-03)\n\n2. **Identificar onde está no fluxo:**\n   - Já passou pela SLC? (despacho de conformidade)\n   - Já passou pela DOF? (certidão de disponibilidade)\n   - Está na DR? → precisa de despacho autorizatório\n\n3. **Verificar riscos paralelos:**\n   - Prazo contratual expirou? (risco de serviços sem contrato)\n   - Há retroativos a pagar? (desde a data-base)\n   - Garantia contratual está regular?\n   - Limite de 60 meses (art. 57, II, Lei 8.666/93)

### 4. Registrar e Atualizar

- Adicionar ao `pgeas/index.md`
- Atualizar `index.md` principal
- Atualizar `log.md`
- Commit + push

### 5. Push automático

O Hermes Agent faz commit+push automático a cada 10 minutos via cron. Não é necessário executar git push manualmente após cada alteração.

## Identificando Padrões e Criando Processos de Trabalho

Quando 2+ PGEAs tratam do mesmo tema, avaliar se merecem um processo de trabalho formal:

1. **Comparar** os PGEAs lado a lado (objeto, fluxo, responsáveis, valor)
2. **Identificar** etapas comuns e divergências
3. **Propor** processo de trabalho com:
   - Etapas numeradas com responsáveis e prazos
   - Documentos de entrada e saída
   - Critérios de deferimento e indeferimento
   - Casos reais como referência
4. **Criar** em `processes/` com `status: proposta`
5. **Apresentar** para o usuário validar antes de ativar

## Análise Orçamentária

Quando houver dados de demandas e execução orçamentária:

1. Importar para SQLite em `hermes_mpt_ops/data/regional-orcamento.db` (scripts versionados em `hermes_mpt_ops/scripts/` — repo OPS, não no KB)
2. Usar `consultar.py` para consultas rápidas (rodar de `hermes_mpt_ops/` ou via symlink no KB):

```bash
python3 scripts/consultar.py execucao    # Execução por unidade
python3 scripts/consultar.py unidades    # Demandas por unidade
python3 scripts/consultar.py top10       # Maiores itens
python3 scripts/consultar.py sql "..."   # SQL livre
```

3. Tabelas do banco:

| Tabela | Conteúdo |
|--------|----------|
| `demandas` | Demandas do SGA (75 registros) |
| `itens_demanda` | Itens com execução (planejado, empenhado, pago) |
| `itens_avulsos` | Empenhos sem demanda vinculada |
| `execucao` | Acompanhamento mensal (pronta para uso) |

## Integração com Repositório de Processos MPT Cosmos

O site `https://midia-ext.mpt.mp.br/cosmos/planejamento/` contém diagramas BPMN oficiais dos processos administrativos do MPT.

Quando analisar um PGEA, consultar diagramas relacionados para verificar conformidade com o fluxo formal. IDs de diagramas podem ser passados pelo usuário.

## Boletim de Serviço como Fonte de Portarias

O site `https://mpt.mp.br/MPTransparencia/pages/portal/boletinsDeServico.xhtml` publica diariamente os atos administrativos do MPT.

Quando a análise de um PGEA precisar verificar a publicação de uma portaria:
- Buscar por ano/mês no BS
- Localizar o boletim específico pelo número
- Baixar via browser + fetch (JSF-based download)
- Extrair o texto (pymupdf, com limitações de fontes)
- Verificar se o ato foi devidamente publicado

Detalhes do fluxo de download no skill `documentos-mpt`.

> Para **auditoria de extração de Boletins de Serviço** (estrutura distinta de
> PGEA — cabeçalho "BS Eletrônico - NNN/AAAA", sumário, atos), usar
> `hermes_mpt_ops/scripts/audit_boletim.py` (fonte da verdade no OPS) e
> `references/estrutura-boletim.md` da skill `boletim-servico-mpt`.
>
> Para **catálogo em massa de atos normativos a partir dos Boletins de Serviço**
> (pipeline: pastas `YYYY-MM-DD` → `.md` → banco SQLite `data/atos.db` com flag
> `relevante`), ver `references/catalogo-atos-boletins.md` e o script
> `hermes_mpt_ops/scripts/catalogar_atos.py`. Inclui pitfalls: atos que começam
> no meio da página (gatilho `Nº NNN, DE DD DE MÊS DE AAAA`), boletins
> extraordinários (`nº .1/.2` — auditor detecta 0 atos, gerar `.md` manualmente)
> e falso positivo de "Resolução" (rodapé de ato anterior).
>
> ⚠️ **Acesso ao portal do BS (RESOLVIDO 07/08/2026):** o WAF do mpt.mp.br
> bloqueia **Chromium headless** (local E cloud/Browser Use) por **detecção de
> automação/JS** — não por IP (mesmo Client IP nos dois casos). O
> **`cloudscraper` (Python) PASSA** — requests puro falha com
> `SSL: UNEXPECTED_EOF`, mas o cloudscraper usa fingerprint TLS próprio que o
> WAF aceita. **Fluxo completo resolvido** (consulta + download): POST
> **multipart** com o campo-gatilho `j_idt183` + ViewState pós-consulta para
> download — script `baixar_boletim.py` no OPS. Detalhes em
> `references/cloudscraper-waf-mpt.md`.

## Workflow com Múltiplos Provedores

> **Contexto (06/08/2026):** OpenRouter foi **reconfigurado** no credential pool
> com chave nova (`OPENROUTER_API_KEY` no `~/.hermes/.env`, via `hermes auth
> add openrouter --type api-key`). O objetivo é **apenas atividades leves com
> modelos `:free`** — custo zero. A chave anterior (julho) havia sido removida
> por 402 (sem créditos); a nova foi validada com teste real de chat
> (nemotron-3-super-120b-a12b:free respondeu OK). Pool ativo: **Nous
> (principal) + OpenRouter (`:free`)**.

Para otimizar custos com o pool atual:
- **Tarefas leves** (consultas SQL, lint, extrações simples, resumos curtos) →
  modelo gratuito OpenRouter (`:free`), ex: `nvidia/nemotron-3-super-120b-a12b:free`,
  `google/gemma-4-31b-it:free`, `openai/gpt-oss-20b:free`
- **Análises complexas** (riscos, despachos, planejamento) → modelo principal Nous
- ⚠️ Modelos `:free` têm rate-limit de pool compartilhado (429 ocasional —
  tentar outro modelo `:free` ou aguardar)

Usar `delegate_task` para despachar tarefas leves para modelos gratuitos.
Conferir pool com `hermes auth list`.

## Auditoria de Extração de PGEAs (validação de completude)

> **Contexto (ago/2026):** o usuário refez a pendência #10 — **RAG/busca semântica NÃO é o objetivo**.
> O interesse real é garantir que a extração de um PGEA em PDF ficou **completa e com as peças
> identificadas**, sem o usuário precisar conhecer o documento antes. O framework "múltiplas
> estratégias + judge" do vídeo do Hulk se aplica, mas com métricas trocadas: em vez de validar
> retrieval, validar **extração** (completude, identificação, fidelidade). **Saída = relatório, nunca
> bloqueio** (decisão do usuário: "A Auditoria deve gerar relatório").

### O problema

Um PGEA em PDF é um **processo com várias peças dentro** (capa, autuação, despachos, juntadas,
manifestações, ofícios, relatórios, decisões, minutas...). O usuário normalmente **não sabe o que tem
dentro** antes da extração — a auditoria existe para responder: *nenhuma peça ficou de fora? cada peça
foi identificada pelo tipo certo? o conteúdo está fiel?*

### Técnica central: detector genérico pelo cabeçalho dos autos digitais

Todo PDF de autos digitais MPT repete no topo de cada página um cabeçalho de peça com o padrão:

```
<TIPO> NNNNNN.AAAA (ID) − PGEA <numero>
Ex: Despacho Comum Administrativo 000622.2026 (9396152) − PGEA 20.02.1400.0000281/2026−34
```

**Lição-chave:** uma lista FIXA de tipos de peça captura só ~40% — os demais viram "páginas órfãs".
O detector correto é **genérico**: regex no padrão do cabeçalho captura todos os tipos sem lista.

```python
HEADER_RE = re.compile(
    r"^(?P<tipo>[A-ZÀ-Úa-zà-ú ]+?)\s+(?P<num>\d{5,6}\.\d{4})\s*\((?P<id>\d{7,8})\)\s*[−-]\s*PGEA\s",
    re.IGNORECASE,
)
```

Tipos reais já vistos em PGEAs da PRT14: Despacho Comum Administrativo, Juntada, Manifestação do
Servidor, Relatório, Cópia de documento, Ofício, Decisão Administrativa, Outras Providências,
Elaboração de Minuta, Requerimento. (A lista fixa original só tinha ~13 tipos e perdeu metade.)

### As 3 camadas

| Camada | O que faz | Custo |
|--------|-----------|-------|
| **1. Pré-visão** | Metadados + capa (págs 1-3) + contagem de páginas → inventário esperado; detecta páginas vazias (PDF escaneado → precisa OCR) | R$ 0 (pymupdf local) |
| **2. Estrutural** | 1ª linha real de cada página → detecta peça pelo cabeçalho → inventário real com intervalos de páginas + páginas órfãs | R$ 0 |
| **3. Judge LLM** | Só nos pontos suspeitos da camada 2 (amostras, NUNCA o PDF inteiro): score de fidelidade + peças mal identificadas | Centavos (deepseek-v4-flash) |

- **Páginas 1 e últimas** (capa, assinaturas, "Histórico gerado em") **não têm cabeçalho de peça — é esperado**, não é erro.
- **PDFs 100% digitais** = zero páginas vazias → nada de OCR. Só ativar OCR quando a camada 1 acusar.

### Como rodar

1. PDFs chegam em `/workspace/` (WebUI) — a extração/auditoria passou a ser feita lá (ago/2026)
2. Script pronto: `hermes_mpt_ops/scripts/extrair_auditar_pgea.py` — **consolidado, faz as 3 camadas num comando só**
   (desde 04/08/2026; antes eram 2 scripts separados: audit_pgea p/ 1+2 e audit_extracao p/ 3 —
   renomeado de `audit_pgea.py` para `extrair_auditar_pgea.py` em 05/08/2026, pois extrai E audita).
   ⚠️ O script NÃO vive mais na pasta da skill — as cópias locais foram REMOVIDAS em 05/08/2026
   (divergiam do OPS; fonte da verdade = `hermes_mpt_ops/scripts/`). Rodar pelo caminho do OPS.
   ```bash
   python3 extrair_auditar_pgea.py <PGEA.pdf>              # camadas 1+2+3 (inventário + extrai MD + audita)
   python3 extrair_auditar_pgea.py <PGEA.pdf> --sem-extracao   # só camadas 1+2 (inventário, sem MD)
   python3 extrair_auditar_pgea.py <PGEA.pdf> --saida DIR      # grava em DIR (padrão: /workspace)
   ```
   - ⚠️ **Ambiente WebUI:** `pip install pymupdf` funciona direto (sem PEP 668) — diferente do KB, que exige `.venv` (ver Fluxo de Processamento acima)
3. Entregáveis (em `/workspace/` ou `--saida`): `auditoria_<PGEA>.md` (relatório completo com
   tabela peça→páginas + verdicto por página) + `<PGEA>.md` (extração MD auditada)
4. Apresentar o relatório ao usuário e aguardar decisão — a auditoria **não bloqueia** nada
5. **Aprovado → migrar** (governança KB/OPS/workspace — ver skill `dr-mpt-ops` + `hermes_mpt_ops/docs/FLUXO-INGESTAO.md`): PDF → `KB/raw/pgeas/`, extração → `pgeas/pgea-XXX/extracao.md` (usar pasta EXISTENTE se o PGEA já tem — ex: 281 entra em `pgea-biblioteca/`, não cria duplicata), relatório → `OPS/data/auditorias/`, script consolidado → `OPS/scripts/`, atualizar `pgeas/index.md` + `log.md`, commit+push separados (KB e OPS), e **limpar o workspace** (rascunhos e PDFs fonte morrem — está tudo versionado).

### Camada 3 na prática (auditar a extração MD já gerada)

Quando o PDF já foi extraído para Markdown (fluxo normal: extração em `/workspace/`), auditar
o MD contra o PDF com `hermes_mpt_ops/scripts/extrair_auditar_pgea.py` (camada 3 embutida) — compara:

| Checagem | Como | Custo |
|----------|------|-------|
| **Completude** | cada peça do inventário (camada 2) tem seção `## <peça>` no MD? sobrou seção? | R$ 0 |
| **Cobertura de páginas** | marcadores `<!-- pág N -->` no MD cobrem todas as páginas com conteúdo? | R$ 0 |
| **Fidelidade de volume** | chars por página PDF vs MD (razão 0.90–1.15 = ok) → pontos suspeitos | R$ 0 |
| **Judge** | verificar suspeitas por **conteúdo** (comparar texto PDF vs MD da página) | centavos/manual |

### Padrão do extrator MD com marcadores (pré-requisito da camada 3)

Para a camada 3 funcionar, a extração precisa de: (1) **uma seção `##` por peça** — a chave da
seção é o **nome completo** `TIPO NUM (ID)` do cabeçalho (nunca só o tipo, senão peças
diferentes do mesmo tipo colapsam numa seção só); (2) **marcador `<!-- pág N -->`** no início
do texto de cada página (permite conferir cobertura e comparar com o PDF página a página);
(3) nova seção **só quando a peça muda** (testar `if peca != atual`), senão cada página com
cabeçalho cria seção duplicada (33 seções para 14 peças reais).

> 📎 `references/extrator-md-marcadores.md` — padrão completo do extrator MD (código,
> contratos de formato e pitfalls validados em 04/08/2026 com o PGEA 281).

## Pitfalls

- **`doc.page_count` depois de `doc.close()` lança `ValueError`** — guardar `TOTAL_PAGS = doc.page_count` ANTES de fechar o documento; usar essa variável nas comparações seguintes.
- **Fidelidade por volume gera falsos positivos em páginas pequenas** (< ~300 chars, ex: folhas de rosto de juntada): o marcador `<!-- pág N -->` (~18 chars) distorce a razão (1.28–1.43 sem ser erro). **Páginas pequenas: comparar por conteúdo, não por volume** — o judge refuta a suspeita conferindo o texto (byte a byte idêntico = falso positivo).
- **Chave de seção da extração = `TIPO NUM (ID)` completo**, não só o tipo — senão "Juntada 002739" e "Juntada 002740" viram uma seção só (12 seções para 14 peças).
- **Regex de chunking do MD: lookahead deve parar também em `\n## `** — o padrão
  `(.+?)(?=<!-- pág|\Z)` captura, na última página de cada peça, o cabeçalho
  `## <peça seguinte>` que vem antes do próximo marcador. Em páginas grandes
  (~2000 chars) os ~50 chars extras passam na razão de volume; em páginas
  pequenas (191 chars) ficam óbvios (razão 1.28–1.43). **Correção:**
  `(?=<!-- pág|\n## |\Z)`. Lição: a auditoria pegou um bug REAL do parser (não
  da extração) — páginas pequenas expõem bugs de medição que as grandes escondem.
- **`sqlite3` CLI não existe no host** — para ler `pendencias.db` (ou qualquer banco) via `ssh host`, usar o módulo python3: `ssh host 'python3 -c "import sqlite3; ..."'` em vez do binário.
- **PGEA que é essencialmente um Boletim encartado => `extrair_auditar_pgea.py` retorna 0 peças** (validado 25/08/2026, PGEA 006534/2025):
  `HEADER_RE` só reconhece o cabeçalho de peça de autos digitais
  (`<TIPO> NNNNNN.AAAA (ID) − PGEA ...`). Quando o corpo do PDF é um **documento
  encartado com cabeçalho próprio que se repete a cada página** — ex. Boletim
  (`PROCURADORIA-GERAL / BSE NNN/AAAA / CIRCULAÇÃO:...`) ou portaria juntada —
  **nenhuma página casa** → inventário dá 0 peças e a extração sai só com a
  `## Capa` (corpo inteiro de fora; Camada 3 acusa 0/N páginas cobertas). Isso
  **não é bug do PDF**, é o limiar do detector. **Antes de confiar na saída**
  ("0 peças") numa extração de PGEA, conferir o cabeçalho real da página 2 com
  pymupdf: se não for `<TIPO> NNNNNN.AAAA (ID) − PGEA`, o documento é encartado
  e cai nesse caso. **Fix planejado:** detector de fallback "documentos
  encartados" — quando `HEADER_RE` achar 0, agrupar por blocos contíguos (Capa;
  corpo por documento cujo cabeçalho contínuo muda; bloco `HISTÓRICO DO
  PROCEDIMENTO` `Data|Movimento|Usuário` no fim). Granularidade recomendada:
  **um bloco por documento inteiro** (mais robusto) em vez de segmentar cada ato
  do Boletim (mais fino, mais frágil). Implementar como detector secundário,
  manter `HEADER_RE` como primário, sem mudar assinatura/uso do script.
- **Não pular entidades:** ao mapear estruturas organizacionais, criar página para **cada** entidade, não apenas as principais. Usuário espera completude — verificar se todas as unidades mencionadas na fonte foram criadas antes de declarar conclusão.
- **Sempre verificar o histórico:** o PGEA pode estar em estágio diferente do esperado — ler os movimentos recentes antes de analisar.
- **PGEAs de outras Regionais:** guardar separado em `modelos/`, nunca misturar com PGEAs da PRT14.
- **Não confundir processos de trabalho com PGEAs:** processos vivem em `processes/`, PGEAs em `pgeas/`. São estruturas distintas. **Ressalva:** PGEAs de Contratação contêm processos de trabalho embutidos (aditivos/apostilamentos) — estes são extraídos como metadados do PGEA, não movidos para `processes/`.
- **Discutir antes de criar:** antes de criar um processo de trabalho a partir de PGEAs, apresentar a proposta para validação do usuário.
- **Confirmações vão para pendências (não em tempo real):** desde ago/2026, quando algo do PGEA precisar de confirmação do usuário (indexação, minuta de despacho, decisão), criar pendência com `pendencia.py add` e seguir trabalhando — não perguntar na conversa. Lembretes automáticos 3x/dia avisam o usuário; ele diz "resolver pendências" quando disponível. Ver skill `dr-mpt-ops`.

## Compreensão Causal (complemento — skill `compreensao-pgea`)

Antes de criar/atualizar a `analise.md`, verificar se existe `compreensao.md`
na pasta do PGEA (gerado pela skill `compreensao-pgea` — linha do tempo causal
com função por peça e estágio). Se existir:

- A **situação atual** e o **fluxograma** da análise devem refletir o **estágio
  causal** da compreensão (abertura → instrução → análise → decisão → execução)
- O **diagnóstico** deve citar o gargalo causal (ex: "processo parado na
  decisão desde DD/MM — aguarda despacho da DR", "movimentação sem peça
  seguinte")
- A análise passa a **consumir** a compreensão (não relê o PDF nem refaz a
  cadeia causal) — eficiência de tokens e consistência
- Se a compreensão não existir e o PGEA foi auditado, gerar com
  `compreender_pgea.py` (rascunho) + revisão antes da análise

Ver skill `compreensao-pgea` para o modelo (funções causais abertas, marco
inicial = despacho de impulsionamento, `processos.db` com eventos).

## Minutar Despachos Autorizatórios

Quando o PGEA de contratação está na DR aguardando autorização de remanejamento orçamentário, o próximo passo é minutar o despacho.

> ⚠️ **Confirmações assíncronas:** quando a análise/minuta precisar de confirmação do DR, NÃO bloquear a conversa — criar pendência com `pendencia.py add --tipo confirmacao|decisao` (script em `hermes_mpt_ops/scripts/`, wrapper em `~/.hermes/scripts/`) e seguir trabalhando. O usuário resolve quando disser "resolver pendências". Detalhes no skill `dr-mpt-ops` (seção Sistema de Pendências) e `wiki/referencias/sistema-pendencias.md`.

### Estrutura do despacho

1. **Cabeçalho** — número (formato `DESPACHO nº XXXX.ANO`), sem repetir processo/assunto (vai no editor do sistema)
2. **Considerandos** — em ordem cronológica: solicitação → SLC → DA → DOF
3. **Dispositivo** — "Resolvo:" + itens numerados
4. **Fecho** — local/data + nome do Diretor + cargo + "(assinado eletronicamente)"

### Regras (estilo do DR — Aloísio Spadeto)

- **Enxuto e direto** — sem floreios, sem "Publique-se. Cumpra-se."
- Cada "Considerando" em **parágrafo único**, começando com "Considerando..."
- Citações entre **parênteses**: `(Despacho nº 1310/2026)`, `(T.I. nº 000064/2026)`
- Numerais **sem extenso** — só o número: `R$ 1.189,20`
- Verbos do dispositivo: **"Resolvo:"** (minúscula) + itens com verbo no infinitivo iniciando com maiúscula: `1. Autorizar...`, `2. Cientificar...` (NÃO caixa alta)
- Padronizar numeração dos documentos dos autos (ex: T.I. sempre `nº 000064/2026`, não `nº 64/2026`)
- "Liquidação" no lugar de "pagamento" quando se tratar de valores
- Fluxo real dos autos: **DA formaliza o apostilamento** (não SGC)
- Salvar em `pgeas/pgea-XXX/minuta-despacho-remanejamento.md`

> 📎 `references/minuta-despacho-remanejamento.md` contém o template com o despacho real do DR como exemplo.

- **Bidding ≠ Execution:** o PGEA da licitação (onde o contrato foi celebrado) fica com licitações; o PGEA de contratação (que recebe a cópia do contrato) fica com o gestor do contrato. São PGEAs distintos. Não confundir.
- **Wiki path:** o wiki vive em `/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/` (persistente, montado do host `${HOME}/hermes-data`). Desde a migração de jul/2026, `write_file`/`patch` funcionam diretamente no wiki (HERMES_WRITE_SAFE_ROOT=/opt/data cobre o caminho) — **não usar mais workaround de terminal** (sed/echo) para escrever no wiki. Usar terminal apenas para git operations (pull/push com auth) e para scripts que precisam de shell.