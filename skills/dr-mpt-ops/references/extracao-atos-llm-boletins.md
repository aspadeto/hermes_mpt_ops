# Extração de atos de boletins via LLM (extract_ato_llm.py)

Fonte: sessão de 24/08/2026 — teste real com BS-97-2026 (392 KB).

## Script

`hermes_mpt_ops/scripts/extract_ato_llm.py` — extrai lista de atos de um
boletim docling (`boletins_docling/BS-*.md`) chamando o LLM configurado
(OpenRouter, `~/.hermes/.env` → OPENROUTER_API_KEY; default
`deepseek/deepseek-v4-flash-0731`). Saída:
`hermes_mpt_kb/entities/BS-XXX-YYYY_llm_atos.json`.

## Como funciona (pós-chunking, ago/2026)

1. **`chunk_text()`** divide o boletim em chunks ≤12.000 chars, preferindo
   quebrar em cabeçalhos markdown (`^#{1,4} `) para não cortar um ato no
   meio; fallback linha em branco; corte duro como último recurso.
2. Cada chunk vai ao LLM com prompt pedindo JSON array com 4 chaves fixas
   por ato: `numero`, `tipo`, `ementa`, `unidade`. Chunk sem ato completo
   deve retornar `[]`.
3. Falha de parsing em um chunk = aviso em stderr e segue (não aborta).
4. **Dedup** por tupla `(numero, tipo.lower(), unidade.lower())` — ato pode
   aparecer parcialmente em dois chunks.
5. Progresso/avisos vão para stderr; resumo + caminho do JSON no stdout.

## ⚠️ Pitfall crítico: modelo de raciocínio estoura max_tokens

O `deepseek-v4-flash` é reasoning model: com `max_tokens=4000`, ele gasta a
janela inteira com *reasoning tokens* e corta ANTES de escrever o JSON.
Sintoma: `content=None` na resposta da API (quebra com
`'NoneType' object has no attribute 'strip'`), `finish_reason=length`,
`completion_tokens_details.reasoning_tokens` alto no usage. Na primeira
rodada do teste, 12/48 chunks falharam assim.

Fix aplicado: `max_tokens=8000` em `call_llm()` + tratamento explícito de
`content None` (retorna mensagem com finish_reason). Diagnóstico rápido:

```python
r = client.chat.completions.create(...)
print(r.choices[0].finish_reason)          # "length" = estourou
print(r.choices[0].message.content is None)
print(r.usage.completion_tokens_details.reasoning_tokens)
```

Se trocar de modelo, revalidar: modelos de raciocínio precisam de folga
grande no max_tokens para tarefas de extração estruturada.

## Resultado do teste real (BS-97-2026)

| | Antes | Depois |
|---|---|---|
| Conteúdo lido | primeiros 12 KB (3%) | 100% (48 chunks) |
| Atos extraídos | 3 | 17 únicos |
| Chunks com falha | — | 5/48 (falha graciosa) |

Runtime: ~80 min para 48 chunks (chamada sequencial, ~60-100s/chunk com
reasoning). Para os ~512 boletins isso é inviável sequencialmente — paralelizar
ou usar modelo não-reasoning mais barato antes de rodar em lote.

## Problemas residuais conhecidos

- Subnotificação: boletim tem ~48 seções de atos, só 17 vieram — chunks densos
  podem ter tido atos truncados por finish_reason=length mesmo com 8000 tokens.
  Considerar chunks menores (~6k chars) ou pedir saída compacta.
- O LLM às vezes desvia do schema (1 caso: chave `regional` em vez de
  `unidade`) — dedup por chave não pega; validar campos na ingestão.
- `tipo` pode vir capitalizado ("Portaria") — normalizar para lowercase se o
  consumidor exigir o enum exato.
