---
name: documentos-mpt
description: "Processar documentos administrativos do MPT — classificar, extrair e ingerir PGEAs, portarias e normativos na wiki."
version: 1.0.0
author: HAL 9000
license: MIT
platforms: [linux, macos, windows]
---

# Documentos Administrativos do MPT

Processamento, classificação e ingestão de documentos do Ministério Público do Trabalho (MPT) na wiki.

## Terminologia

| Termo | Significado |
|-------|-------------|
| **PGEA** | Processo administrativo da área meio do MPT (MPT Digital Administrativo). Sinônimo de "processo" no sentido de conjunto de documentos ordenados. |
| **Processo (genérico)** | Pode ser: processo de trabalho (workflow), conjunto de documentos ordenados (PGEA), ou desenho de processo (BPMN). Desambiguar pelo contexto. |
| **Processo finalístico** | Usa sigla específica do tipo (extrajudicial/judicial) — NÃO se usa "PGEA". |

## Numeração de PGEAs

Formato: `20.02.XXXX.NNNNNNN/AAAA-DV`

| Parte | Significado |
|-------|-------------|
| `20` | Tipo de Unidade |
| `02` | Ramo do MP (MPT) |
| `XXXX` | Código da unidade de origem |
| `NNNNNNN` | Número sequencial (7 dígitos, zero-padded) |
| `AAAA` | Ano de instauração |
| `DV` | Dígito verificador |

Códigos de unidade para PRT14:
- `1400` = PRT14 (Sede — Porto Velho)
- `1401` = PTM Rio Branco/AC
- `1402` = PTM Ji-Paraná/RO
- `1000` = PRT10 (referência)

O código indica onde o PGEA nasceu, mas o processo pode tramitar nacionalmente.

## Classificação de Portarias

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| **Política** | Define parâmetros gerais e responsabilidades, sem instituir processo específico | 1147/2025 (cotas) |
| **Processo de trabalho** | Cria ou regulamenta fluxos e procedimentos | (parte da 1542/2022) |
| **Designação** | Nomeia/exonera pessoas em cargos | 2078/2025 |
| **Mista** | Combina mais de um tipo — discutir com o usuário | 1542/2022, 1019/2024 |

Classificar pelo conteúdo + descrição do usuário. Em caso de dúvida, discutir.

## Estrutura de Armazenamento na Wiki

```
wiki/
├── processes/              ← Processos de trabalho REGULAMENTADOS
├── pgeas/                  ← PGEAs em andamento (casos concretos)
│   ├── index.md
│   └── pgea-nnnnnn/
│       ├── resumo.md       ← Dados + status + despachos
│       └── raw-extracao.txt ← Extração completa do PDF
├── modelos/                ← PGEAs de outras Regionais (referência)
├── initiatives/            ← Iniciativas/projetos derivados
└── raw/                    ← Fontes brutas extraídas
    ├── legislation/         ← Portarias, normativos
    └── articles/            ← Artigos, PGEAs
```

## Extração via Copilot (Extrator MD MPT)

Quando o usuário não puder enviar o PDF diretamente (documento restrito, tamanho >20MB):

1. Usar o agente **Extrator MD MPT** no Microsoft Copilot
2. O prompt do agente está em `referencias/agente-copilot-extrator.md` (v3, comprimido para <8K chars)
3. Evolução: v1=extração básica, v2=frontmatter YAML+PGEA+survey, v3=compressão+diretriz documento ausente
4. O usuário copia o resultado e cola no chat
5. Ingerir normalmente na wiki

### Limitações do Copilot

- Prompt limitado a **8.000 caracteres** pelo MS Copilot
- Pode falhar com: tabelas complexas, OCR danificado, formulários MS Forms
- Para documentos sensíveis ou extensos, preferir extração local via pymupdf
- Edições recentes do Copilot podem reescrever o prompt — verificar se a versão atual corresponde à `referencias/agente-copilot-extrator.md`

## Boletim de Serviço (BS) — Acesso e Download

URL: `https://mpt.mp.br/MPTransparencia/pages/portal/boletinsDeServico.xhtml`

Sistema JSF (PrimeFaces) com selects de ano/mês e tabela de resultados. Extração via requests simples falha — usar browser tool.

### Fluxo de Navegação e Download

```
1. browser_navigate(url)                         → carrega página
2. browser_console("document.getElementById('j_idt180').value='JUL'; ...") → seleciona mês por DOM
3. browser_click(ref) no link "Pesquisar"          → carrega tabela de resultados
4. browser_snapshot()                              → localiza BS desejado na tabela
```

Cada linha da tabela: `<td>` com nome do BS + `<td>` com link `<a id="tabelaArquivos:N:linkArq">` (N = linha, 0-indexed).

### Download via JavaScript (browser_console)

```javascript
const vs = document.getElementById('javax.faces.ViewState').value;
const fd = new URLSearchParams();
fd.append('consultaForm','consultaForm');
fd.append('j_idt176','2026');   // ano
fd.append('j_idt180','JUL');    // mês (JAN, FEV, ..., DEZ)
fd.append('tabelaArquivos:0:linkArq','tabelaArquivos:0:linkArq');
fd.append('javax.faces.ViewState', vs);
fd.append('javax.faces.source','tabelaArquivos:0:linkArq');
const r = await fetch(url, {method:'POST',
  headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:fd});
const blob = await r.blob(); // blob contém o PDF
// Converter blob para base64 → extrair via execute_code / terminal
```

### Limitações Técnicas

- PDFs do BS costumam ter **fontes não embedadas** (criados no Word) — texto subjacente pode ter caracteres corrompidos (Ø, œ, etc.)
- 32 páginas típicas, com conteúdo em formato de imagem nas páginas internas
- Para extração textual completa, instalar Tesseract OCR
- Para **busca pontual de portarias**, o cabeçalho + texto parcial já bastam

## Repositório MPT Cosmos (Diagramas BPMN)

URL base: `https://midia-ext.mpt.mp.br/cosmos/planejamento/`

Repositório de processos administrativos em BPMN, publicado via Bizagi Modeler.

### Como Acessar e Extrair

1. `browser_navigate(url)` — carrega o modelo (ex: "Planejamento_Contratacao_V16")
2. Extrair árvore de navegação da sidebar → lista completa de subprocessos
3. Cada item na sidebar é um link que abre o diagrama individual
4. IDs de diagramas: URL hash `#diagram/<UUID>` — podem ser passados pelo usuário

### Como Usar na Análise

- Quando analisar um PGEA, consultar diagrama relacionado no Cosmos
- Comparar o fluxo real do PGEA com o fluxo formal do diagrama
- Diagramas do Cosmos permitem verificar conformidade e identificar riscos

### Exemplo — Gerir Bens e Materiais

Referência completa com 17 subprocessos em `referencias/cosmos-gerir-bens-materiais.md`:
- Gerir Bens (Patrimônio) — 11 atividades
- Gerir Materiais (Almoxarifado) — 8 atividades
- Inventariar — 3 atividades

Os diagramas do Cosmos são visuais (BPMN). A extração é limitada à árvore de navegação; detalhes de fluxo exigem acesso ao Bizagi Modeler completo.

## Pitfalls

- **NÃO misturar PGEAs de outras Regionais com os da PRT14** — criar em `modelos/` separadamente
- **Sempre classificar a portaria** (política, processo, designação, mista) ao ingerir
- **PGEA não é processo de trabalho** — guardar em locais diferentes
- **Identificar padrões** entre PGEAs repetitivos pode levar à criação de processos de trabalho informais
- **Documentos de outras Regionais** servem como modelo/referência, não como PGEAs ativos
