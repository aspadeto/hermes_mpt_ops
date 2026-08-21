# Pipeline PDF → Wiki (pdf2wiki.py)

Script: `hermes_mpt_ops/scripts/pdf2wiki.py` (versionado). Symlink local em `wiki/scripts/pdf2wiki.py`.

## Uso

```bash
cd /opt/data/hermes-data/mpt_workspace/hermes_mpt_kb && .venv/bin/python3 scripts/pdf2wiki.py <arquivo.pdf> [--slug nome] [--no-render] [--dpi 150]
```

Flags:
- `--slug` — nome da pasta destino (default: derivado do nome do PDF)
- `--no-render` — não renderizar páginas com tabelas como PNG
- `--dpi` — resolução das renderizações (default 150)

## Saída

```
wiki/raw/articles/<slug>/
├── artigo.md          ← Markdown convertido (texto por página + tabelas)
├── assets/            ← PNGs de páginas com tabelas + imagens bitmap extraídas
├── fonte.pdf          ← PDF original (fonte imutável)
└── indexacao.json     ← metadados detectados p/ confirmação do usuário
```

## Heurísticas de detecção

### Título
1. Metadados do PDF (`doc.metadata["title"]`)
2. Fallback: primeira página, spans com fonte ≥ 85% da maior fonte (título em destaque)

### Autores
- Linhas de 2-6 palavras, < 60 chars, sem ponto final, primeira letra maiúscula
- Seguidas de bio começando com: Mestre/Mestra, Doutor/Doutora, Especialista, Graduado/a, Servidor/a, Professor/a, Técnico/a, Mestranda, Doutoranda, Bacharel/a
- Verifica páginas 1-2 (bios longas quebram layout) — detecta se pág. 2 contém "Lattes:"/"Orcid:"/"E-mail:"

### Tabelas
- `page.find_tables()` → `tabela_para_markdown()` (converte para `| col | col |`)
- Renderiza a página como PNG de fallback (células mescladas/layout complexo que o MD não replica)
- Registra em `indexacao.json`: página, ordem, linhas, colunas

### Imagens bitmap
- `doc.extract_image(xref)` → salva como `assets/pNNN-img-XXX.ext`, referencia no MD

## Fluxo de indexação (obrigatório)

1. Rodar o script → gera `indexacao.json` com `status: "aguardando_confirmacao"`
2. **Apresentar o JSON ao usuário** (via pendência de confirmação — NÃO perguntar em tempo real)
3. Após confirmação: enriquecer frontmatter (título, autores, publicação, ano, DOI, tema), trocar status para `"confirmado"`, atualizar `raw/articles/index.md`
4. Commit + push (auto-commit de 10min cobre)

## Campos do indexacao.json

`arquivo_original`, `slug`, `titulo`, `titulo_en`, `autores[]`, `publicacao`, `ano`, `doi`, `tema`, `paginas`, `tabelas[{pagina,ordem,linhas,colunas}]`, `imagens[]`, `paginas_renderizadas[]`, `status`

## Exemplo real (Revista TCU v.156)

- Título detectado: "GUIA ELETRÔNICO PARA ELABORAÇÃO E VALIDAÇÃO DE PLANILHA DE CUSTOS..." ✅
- Autores: 5 detectados após ajuste da heurística (Mestra, 6 palavras, página 2) ✅
- 7 tabelas detectadas, 6 páginas renderizadas como PNG
- DOI/publicação preenchidos manualmente pelo HAL (não detectáveis com segurança)
