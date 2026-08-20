# Repositório de Processos MPT Cosmos

**URL:** https://midia-ext.mpt.mp.br/cosmos/planejamento/
**Ferramenta:** Bizagi Modeler (BPMN)
**Finalidade:** Diagramas oficiais dos processos administrativos do MPT

## Macroprocesso Principal
**Planejamento_Contratacao_V16_07-07-2022** (ID: dc014640-00ab-4e65-a639-1ec5124b1560)

## Subprocessos Identificados

### Planejamento e Orçamento
- PLANEJAMENTO ANUAL DE AQUISIÇÕES E CONTRATAÇÕES
- DEFINIR DIRETRIZES ESTRATÉGICAS
- PLANEJAR ORÇAMENTO DO EXERCÍCIO SUBSEQUENTE
- ALINHAR DEMANDAS ÀS DIRETRIZES ESTRATÉGICAS
- ELABORAR PROPOSTA DE ORÇAMENTO DO MPT
- DEFINIR CONTRATAÇÕES LOCAIS E NACIONAIS
- ADEQUAR PAAC À LOA

### Contratações
- PLANEJAR CONTRATAÇÃO
- SELECIONAR FORNECEDOR
  - Pregão Eletrônico
  - Dispensa
  - Inexigibilidade
  - ARP (Registro de Preço)
  - Órgão Gerenciador / Partícipe

### Execução Financeira
- EMPENHAR / Registrar Empenho no SIAFI
- GERIR CONTRATAÇÃO
  - Alterar, Reequilibrar, Revisar
  - Repactuar, Reajustar, Prorrogar
  - Encerramento / Rescindir
- PAGAR FORNECEDORES
  - Efetuar Pagamento / Registrar Pagamento
  - Lançar no Portal da Transparência

### Bens e Materiais
- GERIR BENS E MATERIAIS
  - Gerir Bens (Patrimônio)
    - Receber bens, Movimentar, Distribuir, Baixar
    - Processar RMB
  - Gerir Materiais (Almoxarifado)
    - Receber, Devolução, Requisição
    - Processar RMA
  - INVENTARIAR BENS E MATERIAIS
    - Inventário com Leitor de Código de Barras
    - Propor apuração de responsabilidade

## Como Usar

Para acessar um diagrama específico, usar a URL no formato:
`https://midia-ext.mpt.mp.br/cosmos/planejamento/#diagram/{diagram-id}`

Navegar com o browser (ferramenta `browser_navigate`) para extrair a árvore de etapas do diagrama.

## Limitações

- Site é uma aplicação SPA (JavaScript) — requer browser, não web_extract
- Diagramas são BPMN visuais — a extração captura a árvore de navegação, não detalhes de setas/condições
- Pode haver rate limiting em acessos frequentes
