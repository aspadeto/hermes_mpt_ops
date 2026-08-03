# AGENTS.md — Diretrizes de Comportamento (adaptado de Andrej Karpathy)

Diretrizes comportamentais para reduzir erros comuns de LLMs ao trabalhar neste
ambiente. Adaptado do [CLAUDE.md do Karpathy](https://github.com/multica-ai/andrej-karpathy-skills)
para o contexto deste repositório e do ecossistema Hermes.

**Tradeoff:** estas diretrizes pendem para a cautela em vez da velocidade. Para
tarefas triviais, use bom senso.

---

## 0. Contexto deste ambiente

- **Dois repositórios:** `hermes_mpt_ops` (engenharia: scripts, bancos, configs) e
  `hermes_mpt_kb` (conhecimento: documentos, referências, artigos)
- **Neutralidade:** NUNCA usar nomes de setor/regional (ex: PRT14) em código,
  docs ou nomes — o ambiente deve servir a qualquer contexto
- **Segredos:** tokens, credenciais e `.env` NUNCA vão para o git. Segredos vivem
  fora dos repositórios (raiz do hermes-data) ou em `.env` local ignorado
- **Stack:** Python + SQLite + git. Preferir soluções enxutas, sem serviços externos
- **Idioma:** documentação e comunicação em PT-BR (código e commits podem ser em inglês)
- **Estilo do usuário:** passo a passo, tabelas/checklists, avisar antes de agir se
  houver dúvida, respeitar custo de tokens

---

## 1. Pense Antes de Agir

**Não assuma. Não esconda confusão. Explicite tradeoffs.**

Antes de implementar:
- Declare suas premissas explicitamente. Se incerto, **pergunte** (o usuário
  prefere ser consultado a ver trabalho errado)
- Se há múltiplas interpretações, **apresente-as** — não escolha em silêncio
- Se existe abordagem mais simples, **diga** — faça objeção quando justificado
- Se algo não está claro, **pare e nomeie o que confunde**

**Especial para este ambiente:**
- NÃO alterar arquivos originais/em uso (docker-compose, .env, configs do host)
  sem permissão explícita — analisar primeiro, pedir autorização, ter plano de restauração
- Antes de mudanças estruturais, discutir o desenho com o usuário

---

## 2. Simplicidade Primeiro

**Código mínimo que resolve o problema. Nada especulativo.**

- Sem features além do pedido
- Sem abstrações para uso único
- Sem "flexibilidade" ou "configurabilidade" que não foi solicitada
- Sem tratamento de erro para cenários impossíveis
- Se escreveu 200 linhas e poderia ser 50, reescreva

Pergunte-se: "Um engenheiro sênior diria que isto está overcomplicated?" Se sim, simplifique.

---

## 3. Mudanças Cirúrgicas

**Toque apenas no que precisa. Limpe apenas a própria bagunça.**

Ao editar código existente:
- Não "melhore" código, comentários ou formatação adjacentes
- Não refatore o que não está quebrado
- Siga o estilo existente, mesmo que faria diferente
- Se notar código morto não relacionado, **mencione** — não delete

O teste: cada linha alterada deve rastrear diretamente ao pedido do usuário.

---

## 4. Execução Orientada a Objetivos

**Defina critérios de sucesso. Itere até verificar.**

Transforme tarefas em objetivos verificáveis:
- "Adicionar validação" → "Escreva testes para inputs inválidos, depois faça passar"
- "Corrigir o bug" → "Escreva um teste que o reproduza, depois faça passar"
- "Refatorar X" → "Garanta que os testes passam antes e depois"

Para tarefas multi-passo, declare um plano breve:
```
1. [Passo] → verificar: [check]
2. [Passo] → verificar: [check]
3. [Passo] → verificar: [check]
```

Critérios de sucesso fortes permitem iterar de forma independente. Critérios fracos
("faz funcionar") exigem esclarecimento constante.

---

## 5. Versionamento e Integridade

- **Commits pequenos e descritivos.** O auto-commit roda a cada 10 min — não há
  pressa para commitar manualmente, mas mudanças ficam rastreadas
- **NUNCA commitar segredos.** Antes de `git add`, verificar se não entrou token/
  credencial/.env (o .gitignore protege, mas confirme em mudanças incomuns)
- **Bancos de dados são versionados** (pendencias.db, regional-orcamento.db) —
  são estado de trabalho vivo, não regeneráveis por script
- **Symlinks no KB apontam para o OPS** (scripts) — não versionar symlinks

---

## 6. Segurança por Padrão

- Segredos vivem fora dos repos: `hermes-data/GITHUB_TOKEN.txt`, `.git-credentials`,
  `docker/.env`, `~/.hermes/.env`
- Para versionar configuração, usar **templates** (`.env-default`, `.example`) sem valores
- Wrappers do cron vivem em `~/.hermes/scripts/` (não versionados) e chamam o código
  real do OPS
- Ao expor qualquer coisa (API, WebUI, MCP), considerar autenticação e escopo

---

**Estas diretrizes estão funcionando se:** menos mudanças desnecessárias nos diffs,
menos reescritas por overcomplication, e perguntas de esclarecimento vêm ANTES da
implementação em vez de depois dos erros.
