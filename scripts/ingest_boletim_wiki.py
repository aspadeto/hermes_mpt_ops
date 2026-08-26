#!/usr/bin/env python3
"""
ingest_boletim_wiki.py — Ingestão de um boletim docling para o wiki do KB.

Gera uma página entities/bs-xxx-yyyy.md a partir de boletins_docling/BS-XXX-YYYY.md,
seguindo o SCHEMA.md do wiki.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

DEFAULT_KB = Path("/opt/data/hermes-data/mpt_workspace/hermes_mpt_kb")
DEFAULT_DOCLING = DEFAULT_KB / "boletins_docling"
DEFAULT_ENTITIES = DEFAULT_KB / "entities"
DEFAULT_INDEX = DEFAULT_KB / "index.md"
DEFAULT_LOG = DEFAULT_KB / "log.md"
DEFAULT_RAW = DEFAULT_KB / "raw/boletins"


def extract_boletim_fields(md_text: str) -> dict:
    data = {
        "numero": "",
        "ano": "",
        "data": "",
        "ementa": "",
        "regionais": [],
        "atos": [],
        "tipo": "boletim",
    }

    # número/ano do heading principal (case-insensitive, sem depender de ^#)
    # Aceita: "BOLETIM DE SERVIÇO ELETRÔNICO NNN/AAAA" e "BOLETIM DE SERVIÇO ELETRÔNICO EXTRAORDINÁRIO NNN.X/AAAA"
    m = re.search(r"BOLETIM\s+DE\s+SERVI[ÇC]O[^\n]*?0*(\d+(?:\.\d+)?)/(\d{4})", md_text, re.I)
    if m:
        data["numero"] = f"{int(m.group(1).split('.')[0]):03d}" + ("." + m.group(1).split('.')[1] if "." in m.group(1) else "")
        data["ano"] = m.group(2)

    # data: janela após o heading do boletim → "SEXTA-FEIRA, 17 DE JANEIRO DE 2025"
    if m:
        window = md_text[m.start():m.start() + 220]
        m_date = re.search(r"(\d{1,2})\s+DE\s+([A-ZÇÃÕÁÉÍÓÚ]+)\s+DE\s+(\d{4})", window)
        if m_date:
            dia = m_date.group(1).zfill(2)
            mes = {
                "JANEIRO": "01", "FEVEREIRO": "02", "MARÇO": "03", "ABRIL": "04",
                "MAIO": "05", "JUNHO": "06", "JULHO": "07", "AGOSTO": "08",
                "SETEMBRO": "09", "OUTUBRO": "10", "NOVEMBRO": "11", "DEZEMBRO": "12",
            }.get(m_date.group(2).upper(), "")
            if mes:
                data["data"] = f"{dia}/{mes}/{m_date.group(3)}"

    regionais = sorted(set(re.findall(r"PRT-?\d+[ªº]", md_text)))
    # Normaliza: remove indicador ordinal (ª/º) e converte para lowercase
    data["regionais"] = [r.lower().replace("ª", "").replace("º", "") for r in regionais]

    # ajuste 2: parar ementa em headings internos também
    heading_interno = re.compile(r"^#{1,6}\s+#")
    atos = []
    current = None
    current_ementa = []
    current_unit = None
    current_section_unit = "mpt"  # default
    for line in md_text.splitlines():
        # Detecta atos: heading (## ...) que contém Nº/N° seguido de número
        # Ex: "## Nº 2152, DE 30 DE DEZEMBRO DE 2025", "## DECISÃO N° 4476.2025"
        if re.match(r"^#{1,6}\s+.*N[º°]\s*\d+", line):
            if current is not None and current_ementa:
                current["ementa"] = " ".join(current_ementa)
                atos.append(dict(current))
            m_num = re.search(r"N[º°]\s*(\d+[^\n]*)", line)
            current = {"numero": m_num.group(1).strip() if m_num else ""}
            current_ementa = []
            current_unit = None
            
            # Detectar unidade do ato pelo contexto de headings anteriores
            # Mantém estado da última seção principal vista
            continue
        
        # Track current section heading for unit inference
        if re.match(r"^#{1,3}\s+", line):
            section_heading = line.strip()
            # Check for known section patterns
            if "PROCURADORIA-GERAL" in section_heading.upper() or "VICE-PROCURADORA" in section_heading.upper():
                current_section_unit = "pgt"
            elif "DIRETORIA DE GESTÃO DE PESSOAS" in section_heading.upper() or "DGP" in section_heading.upper():
                current_section_unit = "dgp"
            elif "DIRETORIA DE ADMINISTRAÇÃO" in section_heading.upper():
                current_section_unit = "dadm"
            elif "CORREGEDORIA" in section_heading.upper():
                current_section_unit = "cg"
            elif "OUVIDORIA" in section_heading.upper():
                current_section_unit = "ouv"
            elif "SECRETARIA EXECUTIVA" in section_heading.upper() or "TIC" in section_heading.upper():
                current_section_unit = "setic"
            elif "PROCURADORIA REGIONAL DO TRABALHO DA" in section_heading.upper():
                m = re.search(r"(\d+)[ªº]", section_heading)
                if m:
                    current_section_unit = f"prt{m.group(1)}"
                else:
                    current_section_unit = "mpt"
            elif "MINISTÉRIO PÚBLICO DO TRABALHO" in section_heading.upper():
                current_section_unit = "mpt"
            elif "ATOS DA" in section_heading.upper() or "PORTARIAS" in section_heading.upper() or "EDITAIS" in section_heading.upper() or "DECISÕES" in section_heading.upper():
                # Keep previous section unit
                pass
            continue
        if current is None:
            continue
        s = line.strip()
        if not s or s.startswith("<!--") or s.startswith("|"):
            continue
        if heading_interno.match(s):
            continue
        current_ementa.append(s)
        # detectar unidade do ato - usa a seção atual se disponível
        if current_unit is None:
            current_unit = current_section_unit
        # fallback: detecta no texto do ato
        if current_unit is None:
            m_unit = re.search(r"Procuradoria Regional do Trabalho da\s+(\d+)[ªº]", s, re.I)
            if m_unit:
                current_unit = f"prt{m_unit.group(1)}"
            elif re.search(r"Procuradoria-Geral do Trabalho", s, re.I):
                current_unit = "pgt"
            elif re.search(r"Ministério Público do Trabalho", s, re.I):
                current_unit = "mpt"
    if current is not None and current_ementa:
        current["ementa"] = " ".join(current_ementa)
        atos.append(current)

    cleaned = []
    for a in atos:
        e = a.get("ementa", "")
        # limpeza de heading residual, preâmbulo padrão e marcações
        e = re.sub(r"#{1,6}\s+[^\n]+", "", e, flags=re.I)
        e = re.sub(r"CIRCULAÇÃO:\s*[^\n]+", "", e, flags=re.I)
        e = re.sub(r"O\s+(PROCURADOR[^\n]+?|DIRETOR[^\n]+?|COORDENADOR[^\n]+?|CHEFE[^\n]+?)\s*,\s*no\s+uso\s+[^\n]+?,\s*", "", e, flags=re.I)
        e = re.sub(r"A\s+(PROCURADORA[^\n]+?|DIRETORA[^\n]+?|COORDENADORA[^\n]+?|CHEFE[^\n]+?)\s*,\s*no\s+uso\s+[^\n]+?,\s*", "", e, flags=re.I)
        e = re.sub(r"Lei\s+Complementar\s+n?[º°]?\s*75[^\n]*?,", "", e, flags=re.I)
        e = re.sub(r"Portaria\s+PGT\s+n?[º°]?\s*1\.?728[^\n]*?,", "", e, flags=re.I)
        # remove datas históricas no início: "de 20 de maio de 1993," etc.
        e = re.sub(r"^de\s+\d{1,2}\s+de\s+[a-zçãõáéíóú]+\s+de\s+\d{4}[.,]?\s*", "", e, flags=re.I)
        # remove datas abreviadas no início: "de 20/05/93,"
        e = re.sub(r"^de\s+\d{1,2}/\d{2}/\d{2,4},?\s*", "", e, flags=re.I)
        # remove resíduos "da de 2 de outubro de 2017," / "do de ..."
        e = re.sub(r"\b(da|do)\s+de\s+\d{1,2}\s+de\s+[a-zçãõáéíóú]+\s+de\s+\d{4}[.,]?\s*", "", e, flags=re.I)
        # remove citações de portarias/leis com referência de data no início
        e = re.sub(r"^(?:Portaria\s+PG[^\n]{0,80}?,\s*|Portaria\s+PGT\s+n?[º°]?\s*\d+[^\n]*?,?\s*)", "", e, flags=re.I)
        e = re.sub(r"\s+", " ", e).strip()
        # ajuste 3: normalizar número de ato e remover ruído
        e = re.sub(r"N[º°]\s*\d+,\s*DE\s+\d{1,2}\s+DE\s+[A-ZÇÃÕÁÉÍÓÚ]+\s+DE\s+\.?\d{4}", "", e, flags=re.I)
        e = re.sub(r"N[º°]\s*\d+,\s*DE\s+\.?\d{4}", "", e, flags=re.I)
        e = re.sub(r"N[º°]\s*\d+\s+DE\s+\.?\d{4}", "", e, flags=re.I)
        e = re.sub(r"\s+", " ", e).strip()
        e = e[:180]
        if not e:
            continue
        cleaned.append({
            "numero": a.get("numero", ""),
            "ementa": e,
            "unidade": current_unit or "mpt",
        })
    data["atos"] = cleaned[:8]
    return data


def extract_themes(text: str, max_themes: int = 8) -> list[str]:
    """Extrai temas automáticos por TF simples."""
    stop = {"que","de","do","da","no","na","em","para","por","com","sobre","o","a","os","as","um","uma","foi","for","são","tem","entre","e","ou","seu","sua","seus","suas","como","quando","onde","qual","quais","quem","tem","tendo","seus","dados","informações","constantes","tendo","vista","considerando","disposto","artigo","inciso","parágrafo","único","letra","data","número","boletim","serviço","ministério","público","trabalho","procuradoria","regional","geral","diretor","procurador","chefe","coordenador","assessor","secretário","nº","n°","art","arts","decreto","lei","portaria","resolução","instrução","normativa","ato","conjunto","acórdão","súmula","recomendação","pgr","casmpt","cs","mpu","pgt","prt","ptm","mpt","pelo","pela","pelo","pela","delegada","delegado","delegados","item","itens","pela","pelo","alterada","alterado","pela","pelo","pela","pelo","parecer","pareceres","contida","contido","fundamento","informação","informações","cumpimento","cumprimento","disposito","disposto","competência","competencias","competência","competencias"}
    words = re.findall(r"\b[a-zçãõáéíóú]{4,}\b", text.lower())
    freq = {}
    for w in words:
        if w not in stop:
            freq[w] = freq.get(w, 0) + 1
    themes = sorted(freq, key=freq.get, reverse=True)[:max_themes]
    return themes


def build_wiki_page(slug: str, fields: dict) -> str:
    numero = fields["numero"] or slug.split("-")[1]
    ano = fields["ano"] or slug.split("-")[2]
    data = fields["data"] or ""
    regionais = fields.get("regionais", [])
    atos = fields.get("atos", [])
    
    # Prioriza temas do LLM, senão extrai por TF
    if "temas_llm" in fields and fields["temas_llm"]:
        themes = fields["temas_llm"]
    else:
        ementas_combined = " ".join(a.get("ementa", "") for a in atos)
        themes = extract_themes(ementas_combined)

    reg_links = ", ".join(f"[[{r}]]" for r in regionais[:6]) if regionais else "—"
    theme_links = ", ".join(f"[[{t}]]" for t in themes) if themes else "—"

    ato_lines = []
    for a in atos:
        raw_num = a.get("numero", "")
        # normaliza número do ato: pega só o número antes da vírgula/espço
        m_num = re.match(r"(\d+)", raw_num)
        num = m_num.group(1) if m_num else raw_num
        ementa = a.get("ementa", "")[:140]
        unidade = a.get("unidade", "mpt")
        
        # Usa tipo do LLM se disponível, senão detecta da ementa
        tipo = a.get("tipo", "ato")
        if tipo == "ato":  # fallback para detecção regex
            if re.search(r"\bportaria\b", ementa, re.I) or "PORTARIA" in ementa.upper():
                tipo = "portaria"
            elif re.search(r"\bresolucao\b", ementa, re.I) or "RESOLUÇÃO" in ementa.upper():
                tipo = "resolucao"
            elif re.search(r"\binstrucao\s+normativa\b", ementa, re.I):
                tipo = "instrucao-normativa"
        
        caption = f"{tipo.capitalize()} {num}/{ano} ({unidade.upper()})"
        
        # Normaliza slug: remove acentos
        import unicodedata
        def slugify(s: str) -> str:
            return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')
        
        ato_slug = f"ato-{slugify(tipo)}-{num}-{ano}-{unidade}".lower()
        ato_lines.append(f"- [[{ato_slug}|{caption}]] — {ementa}")
    atos_section = "\n".join(ato_lines) if ato_lines else "—"

    title = f"BS-{numero}/{ano}"
    return f"""---
title: {title}
created: {data or 's/d'}
updated: {data or 's/d'}
type: normativo
tags: [boletim, boletim-servico]
fontes:
  - raw/boletins/BS-{numero}-{ano}.pdf
  - boletins_docling/BS-{numero}-{ano}.md
confianca: media
---

# {title}

- **Data:** {data}
- **Ano:** {ano}
- **Número:** {numero}
- **PDF:** [[raw/boletins/BS-{numero}-{ano}.pdf]]
- **Docling:** [[boletins_docling/BS-{numero}-{ano}.md]]

## Atos

{atos_section}

## Temas

{theme_links}

## Regionais mencionadas

{reg_links}
"""


def append_index(slug: str, title: str) -> None:
    index_path = DEFAULT_INDEX
    entry = f"- [[{slug}]] — {title}\n"
    text = index_path.read_text(encoding="utf-8")
    if slug in text or title in text:
        # atualiza a linha existente, se já houver entrada repetida/antiga
        lines = text.splitlines()
        new_lines = []
        replaced = False
        for line in lines:
            if f"[[{slug}]]" in line or f"— {title}" in line:
                new_lines.append(entry.rstrip("\n"))
                replaced = True
            else:
                new_lines.append(line)
        if not replaced:
            marker = "## Entidades\n"
            if marker in text:
                text = text.replace(marker, marker + "\n" + entry, 1)
                index_path.write_text(text, encoding="utf-8")
                return
        text = "\n".join(new_lines)
        index_path.write_text(text, encoding="utf-8")
        return
    marker = "## Entidades\n"
    if marker in text:
        text = text.replace(marker, marker + "\n" + entry, 1)
        index_path.write_text(text, encoding="utf-8")


def append_log(date_str: str, title: str, ano: str = "") -> None:
    log_path = DEFAULT_LOG
    log_date = date_str.strip() or f"{ano}-01-01" if ano else "s/d"
    entry = f"## [{log_date}] ingest | Boletim {title}\n- Arquivo: entities/{title.lower()}.md\n\n"
    text = log_path.read_text(encoding="utf-8")
    marker = f"Boletim {title}\n"
    if marker in text:
        # substitui o bloco antigo pelo novo
        before = text.split(f"## ", 1)[0]
        rest = "".join(text.split(f"## Boletim {title}", 1)[1:])
        rest = rest.split("\n## ", 1)[1] if "\n## " in rest else rest
        text = before + entry.lstrip("\n") + ("\n## " + rest if rest else "")
        log_path.write_text(text, encoding="utf-8")
        return
    text += "\n" + entry
    log_path.write_text(text, encoding="utf-8")


def ingest_one(bs_md: Path, dry_run: bool = False, use_llm: bool = False, llm_model: str = None, api_key: str = None) -> Path | None:
    # Aceita BS-NNN-YYYY.md e BS-NNN.X-YYYY.md (suplementos)
    m = re.search(r"BS-(\d+(?:\.\d+)?)-(\d{4})\.md$", bs_md.name)
    if not m:
        return None
    numero, ano = m.group(1), m.group(2)
    slug = f"bs-{numero}-{ano}"
    text = bs_md.read_text(encoding="utf-8")
    fields = extract_boletim_fields(text)

    # Enriquecimento opcional via LLM (chamada direta via openai)
    if use_llm:
        try:
            import openai
            import json
            
            # Usa api_key passada como parâmetro (obrigatório)
            if not api_key:
                raise ValueError("api_key não fornecida (passe via parâmetro --api-key)")
            
            client = openai.OpenAI(
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1"
            )
            
            # Prepara prompt
            full_text = text
            regex_json = json.dumps(fields, ensure_ascii=False, indent=2)[:3000]
            
            # Sanitiza texto para JSON (remove caracteres de controle)
            def sanitize_for_json(s: str) -> str:
                return s.replace('\x00', '').replace('\r', ' ').replace('\n', ' ').replace('\t', ' ')
            
            clean_text = sanitize_for_json(full_text[:8000])
            clean_regex = sanitize_for_json(regex_json)
            
            template = """Voce e um especialista em processamento de Boletins de Servico do MPT.
Retorne APENAS JSON valido. NAO inclua markdown, explicacoes, ou texto extra.

REGRAS OBRIGATORIAS DO JSON:
1. Array 'atos_patches': cada objeto DEVE ter virgula separando do proximo (exceto o ultimo)
2. Strings: SEMPRE use aspas duplas, escape aspas internas com \\\", feche todas as strings
3. Objetos: chaves e valores SEMPRE com aspas duplas, virgula entre pares chave-valor
4. Nao inclua comentarios, markdown, ou texto antes/depois do JSON

DADOS REGEX:
{regex_json}

TEXTO (primeiros 8000 chars):
{text}

TAREFA: Retorne JSON com:
{{
  "atos_patches": [
    {{"index": 0, "unidade_correta": "pgt", "ementa_limpa": "...", "tipo_ato": "portaria"}},
    {{"index": 1, "unidade_correta": "dgp", "ementa_limpa": "...", "tipo_ato": "decisao"}}
  ],
  "temas": ["tema1", "tema2", "tema3"],
  "confianca_global": 0.9
}}"""
            
            prompt = template.format(
                regex_json=clean_regex,
                text=clean_text
            )
            
            model = llm_model or os.environ.get("LLM_ENRICH_MODEL", "deepseek/deepseek-v4-flash-0731")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=0.1,
                max_tokens=3000,
                response_format={'type': 'json_object'},
            )
            
            content = response.choices[0].message.content
            
            # Tenta extrair JSON válido da resposta (pode vir com texto extra)
            def extract_json(text: str) -> str:
                """Extrai JSON válido de uma string que pode ter lixo antes/depois."""
                # Tenta encontrar o primeiro { e o último }
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1 and end > start:
                    return text[start:end+1]
                return text
            
            content_clean = extract_json(content)
            
            # Tenta parsear, se falhar tenta reparar strings não terminadas
            def try_parse_json(text: str) -> dict:
                try:
                    return json.loads(text)
                except json.JSONDecodeError as e:
                    # Tenta reparar strings não terminadas
                    import re
                    # Tenta fechar strings não terminadas
                    repaired = text
                    # Conta aspas duplas não escapadas
                    in_string = False
                    escaped = False
                    result = []
                    for i, ch in enumerate(text):
                        if ch == '"' and not escaped:
                            in_string = not in_string
                        elif ch == '\\' and not escaped:
                            escaped = True
                            continue
                        if escaped:
                            escaped = False
                        result.append(ch)
                    
                    # Se estava em string no final, fecha
                    if in_string:
                        repaired += '"'
                    
                    # Tenta fechar chaves e colchetes
                    open_braces = repaired.count('{') - repaired.count('}')
                    open_brackets = repaired.count('[') - repaired.count(']')
                    repaired += '}' * open_braces + ']' * open_brackets
                    
                    try:
                        return json.loads(repaired)
                    except:
                        raise e
            
            llm_result = try_parse_json(content_clean)
            
            # Aplica patches
            if "atos_patches" in llm_result:
                for patch in llm_result["atos_patches"]:
                    idx = patch.get("index")
                    if idx is not None and 0 <= idx < len(fields.get("atos", [])):
                        ato = fields["atos"][idx]
                        if "unidade_correta" in patch:
                            ato["unidade"] = patch["unidade_correta"]
                        if "ementa_limpa" in patch:
                            ato["ementa"] = patch["ementa_limpa"]
                        if "tipo_ato" in patch:
                            ato["tipo"] = patch["tipo_ato"]
            
            if "temas" in llm_result:
                fields["temas_llm"] = llm_result["temas"]
            if "confianca_global" in llm_result:
                fields["llm_confianca"] = llm_result["confianca_global"]
                
            if dry_run:
                print(f"[LLM enriquecido] confiança: {fields.get('llm_confianca', 'N/A')}")
                
        except Exception as e:
            print(f"[Aviso] Falha no enriquecimento LLM: {e}", file=sys.stderr)

    page = build_wiki_page(slug, fields)

    out = DEFAULT_ENTITIES / f"{slug}.md"
    if dry_run:
        print(f"[dry-run] {out}")
        return out
    out.write_text(page, encoding="utf-8")
    append_index(slug, f"BS-{numero}/{ano}")
    append_log(fields.get("data") or "", f"BS-{numero}/{ano}", fields.get("ano") or "")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingestão de boletim docling para wiki")
    parser.add_argument("boletim", nargs="?", help="Caminho do BS-XXX-YYYY.md")
    parser.add_argument("--kb", default=str(DEFAULT_KB))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--use-llm", action="store_true", help="Usa LLM para enriquecer campos (unidade, ementa, tipo, temas)")
    parser.add_argument("--llm-model", help="Modelo OpenRouter (default: LLM_ENRICH_MODEL env var)")
    parser.add_argument("--api-key", help="Chave da API OpenRouter (default: OPENROUTER_API_KEY env var)")
    args = parser.parse_args()

    kb = Path(args.kb)
    docling = kb / "boletins_docling"

    if args.boletim:
        path = Path(args.boletim)
        if not path.exists():
            path = docling / Path(args.boletim).name
    else:
        paths = sorted(docling.glob("BS-*.md"))
        if not paths:
            print("Nenhum boletim docling encontrado.")
            return 1
        path = paths[0]
        print(f"Sem alvo: usando {path.name}")

    out = ingest_one(path, dry_run=args.dry_run, use_llm=args.use_llm, llm_model=args.llm_model, api_key=args.api_key)
    if out is None:
        print("Formato inválido.")
        return 1
    print(f"Página wiki criada: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
