# Search Patterns para PGEAs de Contratação

Ao extrair PGEAs de contratação com muitas páginas, os PDFs frequentemente contêm DOUs completos com extratos de contratos de outras Regionais. Use estes padrões grep para filtrar apenas os documentos relevantes à PRT14.

## Localizar aditivos do contrato específico

```bash
grep -an "termo aditivo\|aditivo\|apostilamento" extracao.md \
  | grep -i "01/2022\|156-2022\|G\.J\.SEG\|vigilância" \
  | head -30
```

## Filtrar ruído de outras Regionais

Quando o PDF contém DOUs completos (muito comum), use `grep -iv` para excluir outras Regionais. O padrão de exclusão típico:

```bash
grep -an "termo aditivo\|apostilamento\|repactuação\|PRORROGAÇÃO\|REAJUSTE" extracao.md \
  | grep -iv "PRT10\|PRT09\|PRT03\|PRT16\|PRT18\|PRT21\|PRT22\|PRT15\|PRT05\|PRT12\|PRT13\|PRT19\|PRT20\|PRT23\|PRT24\|PRT06\|PRT07\|PRT08\|PRT04" \
  | grep -i "01/2022\|14ª\|PRT14\|G\.J"
```

## Localizar cláusulas de valor

```bash
grep -an "CLÁUSULA SÉTIMA\|VALOR.*CONTRATO\|R\$.*71\.\|valor anual" extracao.md | head -10
```

## Localizar a certidão DOF de disponibilidade orçamentária

```bash
grep -an "disponibilidade orçamentária\|créditos orçament\|Certidão.*DOF\|DISponibilidade de Créditos" extracao.md
```

## Localizar despachos recentes (mais perto do fim do arquivo)

```bash
tail -1000 extracao.md | grep -an "DESPACHO\|Despacho\|Termo de Informação\|CIENTIFICAR\|AUTORIZO\|deferido"
```
