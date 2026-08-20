#!/usr/bin/env python3
"""
baixar_boletins_novos.py — Baixa automaticamente os boletins novos do MPT.

Detecta e baixa apenas os boletins ainda não presentes localmente:
1. Consulta o mês corrente no Portal da Transparência
2. Compara com os boletins já baixados (hermes_mpt_kb/raw/boletins/)
3. Baixa os novos (via baixar_boletim.py + cloudscraper)
4. Extrai PDF→MD (extrair_md_boletins.py)
5. Atualiza o catálogo SQLite (catalogar_atos.py)

Uso:
    python3 baixar_boletins_novos.py [--mes AUG] [--ano 2026] [--dry-run]

Sem argumentos, usa o mês/ano corrente.
"""

import argparse
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# ------------------------------------------------------------
# Configuração
# ------------------------------------------------------------
OPS = Path("/opt/data/hermes-data/hermes_mpt_ops")
SCRIPTS = OPS / "scripts"
DATA_DIR = Path("/opt/data/hermes-data/hermes_mpt_kb")
RAIZ_BOLETINS = DATA_DIR / "raw" / "boletins"     # PDFs (destino)
DEST_MD = DATA_DIR / "boletins"                    # MDs (destino)
PYTHON = OPS / ".venv-bol" / "bin" / "python"

MESES = {
    "JAN": "Janeiro", "FEV": "Fevereiro", "MAR": "Março", "ABR": "Abril",
    "MAI": "Maio", "JUN": "Junho", "JUL": "Julho", "AUG": "Agosto",
    "SET": "Setembro", "OUT": "Outubro", "NOV": "Novembro", "DEZ": "Dezembro",
}


def listar_boletins_local(ano: str) -> set:
    """Retorna o conjunto de números de boletins já baixados localmente para o ano."""
    nums = set()
    for p in RAIZ_BOLETINS.glob(f"BS-*-{ano}.pdf"):
        m = re.match(r"BS-([\d.]+)-", p.name)
        if m:
            nums.add(m.group(1))
    return nums


def listar_boletins_portal(scraper_py, ano, mes):
    """Consulta o portal e retorna lista de {indice, numero, data}."""
    import cloudscraper
    import sys as _sys
    _sys.path.insert(0, str(SCRIPTS))
    import baixar_boletim as bb

    scraper = cloudscraper.create_scraper()
    html = bb._consultar_html(scraper, ano, mes)
    tab = re.search(r'<table[^>]*id="tabelaArquivos".*?</table>', html, re.S)
    if not tab:
        return []
    boletins = []
    for tr in re.findall(r'<tr[^>]*>(.*?)</tr>', tab.group(0), re.S):
        tds = re.findall(r'<td[^>]*>(.*?)</td>', tr, re.S)
        if len(tds) < 2:
            continue
        nome = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", tds[0])).strip()
        m = re.search(r'id="tabelaArquivos:(\d+):linkArq"', tds[1])
        mnum = re.search(r"- (\d+(?:\.\d+)?)/\d{4} - (\d{2})/(\d{2})/(\d{4})", nome)
        if nome and m and mnum:
            boletins.append({
                "indice": m.group(1),
                "numero": mnum.group(1),
                "data": f"{mnum.group(4)}-{mnum.group(3)}-{mnum.group(2)}",
                "nome": nome,
            })
    return boletins


def main():
    ap = argparse.ArgumentParser(description="Baixa boletins novos do MPT")
    ap.add_argument("--mes", help="Mês em abreviação (JAN..DEZ). Default: mês corrente")
    ap.add_argument("--ano", help="Ano. Default: ano corrente")
    ap.add_argument("--dry-run", action="store_true", help="Mostra os novos sem baixar")
    args = ap.parse_args()

    hoje = datetime.now()
    mes = (args.mes or hoje.strftime("%b").upper())
    ano = args.ano or str(hoje.year)
    if mes not in MESES:
        sys.exit(f"❌ Mês inválido: {mes} (use JAN..DEZ)")

    # 1. Listar boletins locais
    locais = listar_boletins_local(ano)

    # 2. Consultar portal
    portal = listar_boletins_portal(None, ano, mes)
    if not portal:
        # Sem resposta do portal: sinalizar erro (entrega alerta no cron)
        print(f"⚠️ [cron boletins] Nenhum boletim retornado para {mes}/{ano} (WAF ou servidor indisponível)")
        return 1

    # 3. Detectar novos (número não baixado)
    novos = [b for b in portal if b["numero"] not in locais]

    # Modo watchdog: se não há novos, sair em silêncio (cron no_agent não entrega nada)
    if not novos:
        return 0

    # A partir daqui, há novos → imprime o resumo e processa
    print(f"📋 Mês alvo: {MESES[mes]}/{ano}")
    print(f"  Boletins locais ({ano}): {len(locais)}")
    print(f"  Boletins no portal ({mes}/{ano}): {len(portal)}")
    print(f"  🆕 Novos a baixar: {len(novos)}")
    for b in novos:
        print(f"    - BS {b['numero']}/{ano} ({b['data']})")

    if args.dry_run:
        print("\n[DRY-RUN] Nenhum download feito.")
        return 0

    # 4. Baixar os novos (via baixar_boletim.py --baixar <numero>)
    baixado = 0
    for b in novos:
        print(f"  ⬇️  Baixando BS {b['numero']}/{ano} ...")
        r = subprocess.run(
            [str(PYTHON), str(SCRIPTS / "baixar_boletim.py"), ano, mes,
             "--baixar", b["numero"], "--dir", str(RAIZ_BOLETINS)],
            capture_output=True, text=True, timeout=60)
        if "✅" in r.stdout or "✅" in r.stderr:
            baixado += 1
            print(f"     ✅ OK")
        else:
            print(f"     ❌ Falha: {r.stderr[-200:] or r.stdout[-200:]}")
        time.sleep(2)

    print(f"\n  Baixados: {baixado}/{len(novos)}")

    # 5. Extrair PDF→MD
    print("\n📄 Extraindo PDF→MD ...")
    r = subprocess.run(
        [str(PYTHON), str(SCRIPTS / "extrair_md_boletins.py"),
         "--orig", str(RAIZ_BOLETINS), "--dest", str(DEST_MD)],
        capture_output=True, text=True, timeout=300)
    print("  " + (r.stdout.strip()[-200:] if r.stdout.strip() else r.stderr[-200:]))

    # 6. Regenerar o índice CSV (MDs planos → atos_normativos.csv)
    #    (o catalogar_atos.py espera pastas YYYY-MM-DD; a padronização é MD plano,
    #     então usa-se o exportar_atos_formatos.py para gerar o índice)
    print("\n🗂️  Regenerando índice CSV ...")
    r = subprocess.run(
        [str(PYTHON), str(SCRIPTS / "exportar_atos_formatos.py"),
         "--raiz", str(DEST_MD),
         "--dest", str(OPS / "data" / "indices")],
        capture_output=True, text=True, timeout=300)
    saida = r.stdout.strip() if r.stdout.strip() else r.stderr[-200:]
    print("  " + "\n  ".join(saida.splitlines()[-4:]))

    print("\n✅ Pipeline concluído. Novos boletins baixados, extraídos e indexados.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
