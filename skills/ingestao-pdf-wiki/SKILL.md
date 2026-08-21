---
name: ingestao-pdf-wiki
description: "Converter PDFs para Markdown + assets na wiki."
version: 1.0.0
author: HAL 9000
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [pdf, markdown, wiki, extracao, pymupdf, artigos]
    category: analise
    related_skills: [analise-pgea, llm-wiki, ocr-and-documents]
---

# Ingestão de PDFs na Base (pipeline pdf2kb)

Converte documentos PDF (artigos, legislação, relatórios) em Markdown pesquisável + assets (imagens, tabelas) para a base de conhecimento, com **confirmação do usuário antes de indexar**.

## Quando Ativar

Use quando o usuário:
- Enviar um PDF (artigo, relatório, legislação) para popular a base de conhecimentos
- Pedir conversão de PDF para Markdown pesquisável
- Mencionar "popular a wiki", "converter PDF", "extrair conteúdo de PDF"
- Enviar documentos para `raw/articles/`

> ⚠️ Se for **PGEA**, usar a skill `analise-pgea` (fluxo próprio). Este pipeline é para documentos não-PGEA.

## Fluxo de Trabalho (confirmação ASSÍNCRONA via pendências)

1. **Receber o PDF** (Telegram → `~/.hermes/cache/documents/`, workspace `/opt/data/hermes-data/hermes-webui/workspace/`, **ou email** — usuário avisa que enviou anexos):
   - Listar caixa: `himalaya envelope list --page-size 10` → identificar pelo remetente/assunto
   - **Conferir autenticidade antes de processar** (domínio corporativo exige): cabeçalho com `dkim=pass`/`spf=pass`/`dmarc=pass` do domínio oficial
   - Ler corpo: `himalaya message read <id>` (cabeçalho longo — usar `tail` para o corpo)
   - Baixar anexos: `himalaya attachment download <id>` — ⚠️ salva em `/tmp/` por padrão (não no cwd); mover para pasta de trabalho: `mkdir -p /tmp/email-<id> && mv "/tmp/<nome>.pdf" /tmp/email-<id>/`
   - Converter 1 PDF por vez (decisão do usuário)
2. **Converter** (1 PDF por vez — decisão do usuário):
   ```bash
   cd /opt/data/hermes-data/mpt_workspace/hermes_mpt_kb
   .venv/bin/python3 scripts/pdf2kb.py <caminho-do-pdf.pdf>
   # opcional: --slug nome-da-pasta
   ```
   ⚠️ **NÃO passar `--dest <pasta-existente>`**: se a pasta destino já existe, o script
   cria uma SUBPASTA aninhada (`<pasta>/<pasta>/`). Corrigir com
   `mv <pasta>/<pasta>/* <pasta>/ && rmdir <pasta>/<pasta>`. (Aconteceu 2x em ago/2026
   ao converter papers do arXiv — HyDE e Blended RAG.)
3. **O script gera** em `raw/articles/<slug>/`:
   - `artigo.md` — texto por página + tabelas em Markdown
   - `assets/` — PNGs das páginas com tabelas (fallback visual)
   - `fonte.pdf` — cópia do PDF original (fonte imutável)
   - `indexacao.json` — metadados detectados p/ confirmação
4. **NÃO bloquear esperando resposta síncrona.** Criar uma PENDÊNCIA no sistema (decisão do usuário, jul/2026):
   ```bash
   ~/.hermes/scripts/pendencia.py add \
     --titulo "Confirmar indexação: <título resumido>" \
     --contexto "raw/articles/<slug>/indexacao.json" \
     --tipo confirmacao --prioridade media
   ```
   O usuário é lembrado até 3x/dia (cron 9h/14h/18h UTC) e decide quando resolver.
5. **Quando o usuário disser "resolver pendências"** (ou responder ao lembrete): apresentar o JSON de confirmação — título, autores, ano, publicação, DOI, tema (campos que o script não adivinha com segurança). Resolver com `pendencia.py resolve <id>` após a resposta.
6. **Enriquecer o frontmatter** do `artigo.md` com os metadados confirmados
7. **Atualizar** `raw/articles/index.md` (catálogo)
8. Commit + push (auto-commit cobre, mas confirmar)

## Dependências

- Venv: `/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/.venv` (PyMuPDF/pymupdf)
- Setup: `cd /opt/data/hermes-data/mpt_workspace/hermes_mpt_kb && uv venv .venv && uv pip install pymupdf`
- Usar `.venv/bin/python3` (NUNCA `python3` — system Python tem PEP 668)
- Script canônico: **`hermes_mpt_ops/scripts/pdf2kb.py`** (repo hermes_mpt_ops — fonte da verdade; desde ago/2026 scripts não vivem mais no KB, e o script foi renomeado de `pdf2wiki.py` para `pdf2kb.py` na migração de nomes neutros). Symlink local em `hermes_mpt_kb/scripts/pdf2kb.py` para compatibilidade (NÃO versionado — ver `.gitignore` do KB).

## Heurísticas de Detecção (implementadas no script)

### Título
1. Metadados do PDF (`doc.metadata["title"]`) — frequentemente vazio em artigos científicos
2. Fallback: primeira página, spans com a **maior fonte** (>= 85% da máxima) — pega o título em destaque

### Autores
- Linhas CURTAS (< 60 chars), 2-6 palavras, sem ponto final, primeira maiúscula
- Linha seguinte deve começar com bio: Mestre/Mestra, Doutor(a), Especialista, Graduado(a), Servidor(a), Professor(a), Técnico(a), Mestranda, Bacharel(a)
- **Verificar páginas 1-2** (bios longas quebram o layout — autores continuam na pág. 2)
- Dedupe preservando ordem

### Tabelas (fazer as DUAS coisas — decisão do usuário)
- `page.find_tables()` → Markdown (`| col | col |`)
- **E** renderizar a página como PNG (fallback p/ células mescladas que o MD não replica)
- Detalhe: `tabela.extract()` retorna `None` p/ células vazias → normalizar p/ `""`

## Sistema de Pendências (confirmações assíncronas)

O usuário prefere **trabalho assíncrono**: quando algo precisa de confirmação dele (indexação, despacho, decisão), NÃO bloquear a conversa esperando resposta — criar uma pendência e seguir trabalhando em outras tarefas.

- Script: `~/.hermes/scripts/pendencia.py` (wrapper real p/ cron; o código versionado vive em `hermes_mpt_ops/scripts/pendencia.py` — nunca symlink, ver skill `hermes-cron-automation`)
- Banco: SQLite **`/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/data/pendencias.db`** — VERSIONADO no repo hermes_mpt_ops (migrou do KB em ago/2026; `.gitignore` do OPS tem exceção `!data/pendencias.db`, demais `*.db` ignorados). NÃO usar o caminho antigo `/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb/data/pendencias.db`.
- Lembretes: 3 cron jobs (`remind`) às 9h/14h/18h UTC — silenciosos quando não há pendências
- Gatilho do usuário: **"resolver pendências"** → apresentar uma a uma
- Prioridades: `alta` 🔴 bloqueia fluxo | `media` 🟡 padrão | `baixa` 🟢 pode esperar
- Tipos: `confirmacao` | `decisao` | `revisao` | `outro`
- Documentação completa: `wiki/referencias/sistema-pendencias.md`

> ⚠️ Regra: todo fluxo que precisar de confirmação humana passa por `pendencia.py add` ANTES de seguir. Só resolver após a resposta do usuário.

## Preferências do Usuário

- **1 PDF por vez** (sem lote por enquanto)
- **Tabelas/elementos gráficos:** Markdown E PNG — sempre os dois
- **Sempre gerar JSON de indexação** p/ confirmação — nunca indexar sem aprovação
- **OCR:** implementar SÓ quando aparecer PDF escaneado/página em branco (tesseract) — não adiantar
- Estrutura atual em `raw/articles/` atende; refatorar quando precisar

## Pitfalls

- **Symlinks do KB podem quebrar após renomeação do repo OPS:** os links em
  `hermes_mpt_kb/scripts/` apontam para `/opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/scripts/`.
  Após renomeações de repo (ex: `dr_mpt_ops` → `hermes_mpt_ops`, ago/2026), os
  links ficam órfãos — `python3 scripts/pdf2kb.py` falha com "No such file".
  **Sintoma:** `can't open file '.../scripts/pdf2kb.py'`. **Correção:** apontar
  o symlink para o caminho atual (`ln -sf /opt/data/hermes-data/mpt_workspace/hermes_mpt_ops/scripts/pdf2kb.py scripts/pdf2kb.py`)
  ou chamar o script canônico do OPS diretamente. Conferir com `ls -la scripts/`.
- **PDFs do arXiv (papers):** a heurística de autores NÃO funciona — papers usam
  "1st/2nd/3rd Nome" ou "Nome†‡" com emails/afiliações, sem bios "Mestre/Doutor".
  Título pode vir como "arXiv:XXXX.XXXXXvX [cs.IR] DD MMM YYYY" (metadado). **Extrair
  autores manualmente da página 1** (`fitz` → `doc[0].get_text()[:500]`) e preencher
  o `indexacao.json` à mão (padrão arXiv: autor com superscripts †/‡ = igual contribuição).
- **Metadados `title` costumam vir vazios** em PDFs de revistas (ex: Revista TCU) — a detecção por fonte da primeira página resolve
- **Documentos oficiais (portarias, ofícios, circulares):** o título detectado vem como o TEXTO INTEIRO da página 1 (cabeçalho + ementa + assinatura) e os slugs derivados do nome do arquivo ficam feios (`documento-externo-outros-0271342026`, acentos no slug). Na confirmação, propor sempre **título limpo** (ex: "Portaria PGR/MPU nº 412, de 24/06/2026") e **slug legível** (ex: `portaria-412-2026`) — campos que o script não acerta em normativos.
- **Página sem texto extraível** → o script marca `*[Página sem texto extraível...]*` — sinal de PDF escaneado → OCR
- **Não confundir com PGEA:** PGEAs usam `analise-pgea` + `pgeas/pgea-N/`; artigos usam este pipeline + `raw/articles/`
- **JSON é a fonte da verdade p/ frontmatter:** título/autores do script são sugestões; usuário confirma antes
- Se `--slug` já existir, o script aborta (proteção contra sobrescrita)
- **Auto-commit race:** o cron de auto-commit (a cada 10 min) pode já ter commitado/pushado o artigo antes do commit manual — se o `git commit` manual mostrar pouquíssimas linhas (ex: só o frontmatter), NÃO é erro: verificar com `git log --oneline -3` que o conteúdo já está no repo. Normal em conversas longas (o sync roda em background).
- **Commit do frontmatter enriquecido:** depois de atualizar o frontmatter e o `index.md`, commitar com `git add raw/articles/<slug>/artigo.md raw/articles/index.md` — o resto da pasta costuma já estar commitado pelo auto-commit.
- **Renomear pasta do slug (slug feio → limpo) exige `git add -A`:** após `mv <slug-feio> <slug-limpo>`, um `git add raw/articles/<slug-novo>` stageia só os creates — os **deletes das pastas antigas ficam pendentes** e o commit sai incompleto. Usar `git add -A raw/articles/` para commitar o rename inteiro (aconteceu ago/2026: `documento-externo-outros-0271xx` → `portaria-4xx-2026`).
- **himalaya: versão instalada NÃO aceita `--output json` no `envelope list`** (`error: unexpected argument '--output'`) — usar a saída tabular padrão. O skill `himalaya` (community/hub) documenta `--output json`; confiar no teste real.
