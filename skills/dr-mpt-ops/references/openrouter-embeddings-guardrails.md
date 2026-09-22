# OpenRouter: desbloquear embeddings (guardrails por workspace)

## Sintoma

Ao chamar `/v1/embeddings` com uma key do OpenRouter,a API responde:

```
{"error":{"message":"0 endpoints out of 2 requested are available matching your guardrail restrictions and data policy...\nModel blocked by guardrail: 2 endpoints excluded...","code":404}}
```

Não é erro de código — é **config do dashboard da workspace**. O próprio erro aponta o caminho: `https://openrouter.ai/workspaces/<nome-da-workspace>/guardrails`.

## Regras duráveis

- **Guardrails de workspace bloqueiam FAMÍLIAS inteiras de endpoints** (embeddings, imagens,...), não modelos individuais. O padrão "0 endpoints... matching guardrail" com `Model blocked by guardrail` no corpo = config da workspace,, não provider.
- **Correção é no dashboard** (login dono da key): abas *Model access* / *Allowed models* (allowlist ou toggle de endpoint Embeddings) e *Data policy* (config strict "no data training" pode excluir o provider de embedding, que derruba o endpoint). Liberar Embeddings explícita se houver toggle por endpoint.
- **Ao testar, iterar a lista de modelos — "Model X does not exist"(400) é candidato fora do catálogo, ≠ guardrail: apenas a mensagem com "guardrail"/"data policy" indica bloqueio de config.
- **Modelos de embedding conhecidos no catálogo OpenRouter**: `text-embedding-3-small` **funciona** (dim 1536, 200 com vetores reais) quando o guardrail permite. `BAAI/bge-m3` também existe mas foi bloqueado pela guardrail desta workspace. `jinaai/jina-embeddings-v3` **não existe** (400 "does not exist"→ tentar outro, não é bloqueio).
- **Depois de ajustar no painel, re-testar a conectividade** antes de assumir: `curl -s https://openrouter.ai/api/v1/embeddings -H "Authorization: Bearer $OPENROUTER_API_KEY" -H "Content-Type: application/json" -d '{"model":"text-embedding-3-small","input":["teste"]}'` — 200/lista de vetores = liberado.

## Relação com testes de RAG

Ao avaliar RAG vetorial (#10/e demais) com embeddings via OpenRouter, primero confirmar que o endpoint de embeddings está liberado NAQUELE workspace — senão o teste inteiro falha por infra,, não por técnica. Antes de escrever o harness, checar `curl` de 1 token (3 s. Embedding 540 boletins docling inteiros custa fração de centavo no `text-embedding-3-small` (~0.02//1M tokens).