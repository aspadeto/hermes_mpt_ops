# Indexação de Boletins de Serviço (pipeline completo — validado OUT/2025)

Pipeline validado em 07/08/2026: 24 boletins de OUT/2025 (BS 184→205.1) →
46 MDs → SQLite com 170 atos indexados, 14 diretos da PRT14 + 16 menções.
Fluxo sem commit (artefatos em /tmp; PDFs apagados ao final).

## Pipeline

```bash
# 1. Baixar todos do mês (cloudscraper — venv .venv-bol no OPS)
cd hermes_mpt_ops && .venv-bol/bin/python scripts/baixar_boletim.py 2025 OUT --baixar todos --dir /tmp/boletins-out2025

# 2. Converter PDF → MD por ato (requer venv com pymupdf)
for f in /tmp/boletins-out2025/*.pdf; do
  <venv-pymupdf>/bin/python scripts/audit_boletim.py "$f" --saida /tmp/md-out2025
done

# 3. Indexar num SQLite
<venv-pymupdf>/bin/python scripts/indexar_boletins_prt14.py /tmp/md-out2025/ --db /tmp/boletins_idx.db

# 4. Apagar PDFs (manter MDs + índice)
rm -f /tmp/boletins-out2025/*.pdf
```

## Como o indexador funciona (`indexar_boletins_prt14.py`)

1. **Aproveita os headers `## TIPO Nº X`** que o `audit_boletim.py` gera —
   NUNCA re-derivar atos com regex sobre "N°" no texto cru (pega citações
   internas de portarias PGT/PGR antigas → milhares de falsos positivos;
   teste real: 1913 atos "indexados" vs 170 corretos).
2. **Isola o sub-bloco da regional** (`_subbloco_prt14`): o corpo de um ato
   da seção "PROCURADORIAS REGIONAIS" contém VÁRIAS regionais na mesma
   página (PRT-8ª, 11ª, 13ª, 14ª juntas). Divide pelos cabeçalhos
   `PRT-NNª REGIÃO` e só considera o trecho da 14ª.
3. **Relevância em 2 níveis**: `2` = ato DA PRT14 (sub-bloco contém
   "PROCURADOR-CHEFE DA PROCURADORIA REGIONAL DO TRABALHO DA 14ª" ou "no uso
   de suas atribuições"/RESOLVE/designar); `1` = menciona 14ª/RO/AC (ex:
   decisões da PG que afetam a PRT14); `0` = irrelevante.
4. **Número do ato**: primeiro `N° X, DE DD DE MÊS DE AAAA` no sub-bloco
   (regex com `,\s*DE` após o número — ignora "Portaria PGT nº 1728, de
   2 de outubro de 2017" que é citação, não ato do boletim).
5. **Ementa** (`_ementa`): texto entre o número/data e "O PROCURADOR" /
   "RESOLVE" / "Considerando", normalizado.

## Pitfalls

- `audit_boletim.py` tinha bug `NameError: suspeitas` no print final (linha
  370 usava variável de escopo de outra função). Correção: capturar o retorno
  de `auditar_extracao()` e extrair o nº de suspeitas do texto com regex.
- O venv do KB (`.venv`) pode ter symlink de python quebrado após migração →
  criar venv próprio com uv (pymupdf).
- Boletins com sufixo `.1`/`.2` (ex: 203.1, 205.1) são retificações/extras e
  podem ter 0 atos detectados — normal.
- Ordenação por `data_bs` (ISO) no relatório final; mês em inglês (AUG).
- Quando o fluxo JSF quebrar: ids `j_idt*` são gerados pelo JSF e podem
  mudar — capturar payload real via DevTools (ver
  `references/cloudscraper-waf-mpt.md`).
