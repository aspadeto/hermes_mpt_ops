#!/usr/bin/env python3
"""Baixa Boletins de Serviço do MPT (Portal da Transparência) via cloudscraper.

Fluxo descoberto/validado em 07/08/2026 (payload real capturado no DevTools):

1. GET na página boletinsDeServico.xhtml → extrai ViewState do form consultaForm
2. POST multipart com os campos (o j_idt183 é o GATILHO da consulta):
       consultaForm, javax.faces.ViewState, j_idt176 (ano), j_idt180 (mês), j_idt183
3. Resposta HTML contém <table id="tabelaArquivos"> — cada <tr> é um boletim:
       célula 1: "BS Eletrônico - NNN/2026 - DD/MM/AAAA"
       célula 2: <a id="tabelaArquivos:N:linkArq" onclick="mojarra.jsfcljs(...)">
4. Download: POST multipart com o campo 'tabelaArquivos:N:linkArq' (id=valor)

Por que cloudscraper: o WAF do mpt.mp.br bloqueia browsers headless (local E
cloud via gateway) por detecção de automação; o cloudscraper passa (fingerprint
TLS + sem execução de JS). Mesmo IP, sem proxy.

Uso:
    python3 baixar_boletim.py 2026 AUG                 # lista boletins de ago/2026
    python3 baixar_boletim.py 2026 AUG --baixar 143    # baixa o BS 143/2026
    python3 baixar_boletim.py 2026 AUG --baixar todos  # baixa todos do mês
    python3 baixar_boletim.py 2026 AUG --dir ~/boletins
"""

import argparse
import re
import sys
from pathlib import Path

import cloudscraper

URL = "https://mpt.mp.br/MPTransparencia/pages/portal/boletinsDeServico.xhtml"
MESES = {
    "JAN": "Janeiro", "FEV": "Fevereiro", "MAR": "Março", "ABR": "Abril",
    "MAI": "Maio", "JUN": "Junho", "JUL": "Julho", "AUG": "Agosto",
    "SET": "Setembro", "OUT": "Outubro", "NOV": "Novembro", "DEZ": "Dezembro",
}


def _viewstate(html: str) -> str:
    """Extrai o ViewState do form consultaForm (há 2 forms na página)."""
    cf = re.search(r'<form[^>]*id="consultaForm".*?</form>', html, re.S)
    if not cf:
        raise RuntimeError("form consultaForm não encontrado")
    m = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]+)"', cf.group(0))
    if not m:
        raise RuntimeError("ViewState não encontrado no consultaForm")
    return m.group(1)


def _consultar_html(scraper, ano: str, mes: str) -> str:
    """GET + POST de consulta; retorna o HTML com a tabelaArquivos."""
    html = scraper.get(URL, timeout=30).text
    vs = _viewstate(html)
    resp = scraper.post(URL, files={
        "consultaForm": (None, "consultaForm"),
        "javax.faces.ViewState": (None, vs),
        "j_idt176": (None, str(ano)),
        "j_idt180": (None, mes),
        "j_idt183": (None, "j_idt183"),  # gatilho da consulta
    }, timeout=30)
    return resp.text


def consultar(scraper, ano: str, mes: str) -> list[dict]:
    """Consulta boletins do mês; retorna [{indice, nome}] da tabelaArquivos."""
    html = _consultar_html(scraper, ano, mes)
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
        if nome and m:
            boletins.append({"indice": m.group(1), "nome": nome})
    return boletins


def baixar(scraper, ano: str, mes: str, indice: str, destino: Path) -> bool:
    """Baixa um boletim pelo índice da tabela (POST mojarra.jsfcljs).

    IMPORTANTE: usa o ViewState da resposta pós-consulta (o download falha
    com ViewState de um GET novo — a tabela precisa estar carregada).
    """
    html = _consultar_html(scraper, ano, mes)  # re-consulta p/ pegar o ViewState certo
    vs = _viewstate(html)
    campo = f"tabelaArquivos:{indice}:linkArq"
    resp = scraper.post(URL, files={
        "consultaForm": (None, "consultaForm"),
        "javax.faces.ViewState": (None, vs),
        "j_idt176": (None, str(ano)),
        "j_idt180": (None, mes),
        campo: (None, campo),
    }, timeout=60)
    if resp.content[:5] == b"%PDF-":
        destino.write_bytes(resp.content)
        return True
    return False


def main():
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("ano", help="ano (ex: 2026)")
    ap.add_argument("mes", help="mês em inglês abreviado (JAN..DEZ)")
    ap.add_argument("--baixar", nargs="?", const="todos", default=None,
                    help="número do boletim, ou 'todos'")
    ap.add_argument("--dir", default=".", help="diretório de destino")
    args = ap.parse_args()

    mes = args.mes.upper()
    if mes not in MESES:
        sys.exit(f"Mês inválido: {mes} (use JAN..DEZ)")
    scraper = cloudscraper.create_scraper()

    print(f"📋 Consultando {MESES[mes]}/{args.ano}...")
    boletins = consultar(scraper, args.ano, mes)
    if not boletins:
        print("  Nenhum boletim encontrado.")
        return
    print(f"  {len(boletins)} boletins:")
    for b in boletins:
        print(f"    [{b['indice']}] {b['nome']}")

    if args.baixar is None:
        return
    alvo = [b for b in boletins if args.baixar == "todos"
            or b["nome"].split(" - ")[1].rstrip("/").startswith(f"{args.baixar}/")]
    if args.baixar != "todos":
        alvo = [b for b in boletins if f"{args.baixar}/" in b["nome"]]
    if not alvo:
        sys.exit(f"Boletim {args.baixar} não encontrado em {mes}/{args.ano}.")
    destino = Path(args.dir).expanduser()
    destino.mkdir(parents=True, exist_ok=True)
    for b in alvo:
        m_num = re.search(r"(\d+(?:\.\d+)?)/", b["nome"])
        num = m_num.group(1) if m_num else b["indice"]
        arquivo = destino / f"BS-{num}-{args.ano}.pdf"
        print(f"  ⬇️  Baixando {b['nome']} ...")
        if baixar(scraper, args.ano, mes, b["indice"], arquivo):
            print(f"     ✅ {arquivo.name} ({arquivo.stat().st_size} bytes)")
        else:
            print(f"     ❌ falha (resposta não-PDF) para {b['nome']}")


if __name__ == "__main__":
    main()
