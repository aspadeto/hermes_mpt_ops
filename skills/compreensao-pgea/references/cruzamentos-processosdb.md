# Cruzamentos úteis no `processos.db`

Consultas SQL validadas no piloto (ago/2026, 3 processos / 52 eventos) que
transformam os eventos causais em conhecimento acionável. Banco:
`hermes_mpt_ops/data/processos.db` — tabelas `processos` e `eventos`
(`seq, data, peca, funcao, estagio, efeito`).

## 1. Estágio atual por processo

```sql
SELECT p.slug, p.assunto, e.estagio AS estagio_atual
FROM processos p JOIN eventos e ON e.processo_id=p.id
WHERE e.seq=(SELECT MAX(seq) FROM eventos WHERE processo_id=p.id)
ORDER BY e.estagio;
```

## 2. Tempo total decorrido (autuação → último evento)

```python
# datas em DD/MM/AAAA; converter e subtrair. Resultado do piloto:
# 337: 80 dias · 372: 64 dias · 281: 102 dias
```

## 3. Dias parados desde o último evento

```sql
-- último evento de cada processo; subtrair de hoje
-- Piloto (05/08/2026): 281 parado 16d, 372 parado 7d, 337 parado 6d
```

## 4. Distribuição de funções causais

```sql
SELECT funcao, COUNT(*) n FROM eventos GROUP BY funcao ORDER BY n DESC;
-- Piloto: instrucao 18 > movimentacao 16 > manifestacao 10 > origem 4 > ...
```

## 5. Gargalos: movimentação sem peça de decisão/execução seguinte

```sql
SELECT p.slug, e.seq, e.data, e.peca
FROM eventos e JOIN processos p ON p.id=e.processo_id
WHERE e.funcao='movimentacao'
AND NOT EXISTS (SELECT 1 FROM eventos e2 WHERE e2.processo_id=e.processo_id
                AND e2.seq>e.seq AND e2.funcao IN ('decisao','execucao'))
ORDER BY p.slug, e.seq;
```

⚠️ **Interpretar com cuidado:** a consulta 5 lista movimentações no meio do
ciclo (normais), não só gargalos reais. O gargalo de verdade é o **estágio
atual** (consulta 1) + dias parados (consulta 3) — ex: 2 de 3 processos
parados em `decisao` = a Diretoria é o gargalo setorial.

## Insight do piloto

- 372 e 281 parados na **decisão** (aguardando DR) — gargalo comum
- 281 com pedido de prorrogação por afastamento de servidora (19/06) — desvio
  de cronograma detectável na cadeia causal
- Perfil de funções (instrução > movimentação > manifestação) é o esperado em
  PGEAs de área meio
