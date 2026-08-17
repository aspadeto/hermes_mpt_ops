#!/usr/bin/env python3
"""Baixa TODOS os boletins faltando (Jul/2025 a Ago/2026) de forma robusta.
   - Processa mês a mês
   - Resume se falhar (verifica o que já tem)
   - Log detalhado
   - Try/catch por boletim individual
"""
import argparse
import re
import sys
import time
from pathlib import Path

import cloudscraper

URL = "https://mpt.mp.br/MPTransparencia/pages/portal/boletinsDeServico.xhtml"
MESES = {
    "JAN": "Janeiro", "FEV": "Fevereiro", "MAR": "Março", "ABR": "Abril",
    "MAI": "Maio", "JUN": "Junho", "JUL": "Julho", "AUG": "Agosto",
    "SET": "Setembro", "OUT": "Outubro", "NOV": "Novembro", "DEZ": "Dezembro",
}
MESES_NUM = {v: k for k, v in MESES.items()}

BOLETINS_DIR = Path("/opt/data/hermes-data/boletins")
BOLETINS_DIR.mkdir(parents=True, exist_ok=True)

def _viewstate(html: str) -> str:
    cf = re.search(r'<form[^>]*id="consultaForm".*?</form>', html, re.S)
    if not cf:
        raise RuntimeError("form consultaForm não encontrado")
    m = re.search(r'name="javax.faces.ViewState"[^>]*value="([^"]+)"', cf.group(0))
    if not m:
        raise RuntimeError("ViewState não encontrado no consultaForm")
    return m.group(1)

def _consultar_html(scraper, ano: str, mes: str) -> str:
    html = scraper.get(URL, timeout=30).text
    vs = _viewstate(html)
    resp = scraper.post(URL, files={
        "consultaForm": (None, "consultaForm"),
        "javax.faces.ViewState": (None, vs),
        "j_idt176": (None, str(ano)),
        "j_idt180": (None, mes),
        "j_idt183": (None, "j_idt183"),
    }, timeout=30)
    return resp.text

def consultar(scraper, ano: str, mes: str) -> list[dict]:
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

def baixar_um(scraper, ano: str, mes: str, indice: str, destino: Path) -> bool:
    html = _consultar_html(scraper, ano, mes)
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

def mes_para_sigla(mes_num: int) -> str:
    return list(MESES.keys())[mes_num - 1]

def ja_tem_pdf(pasta: Path, nome_boletim: str) -> bool:
    """Verifica se já existe PDF para este boletim na pasta."""
    # Nome do boletim: "BS Eletrônico - 143/2026 - 03/08/2026"
    m = re.search(r"BS Eletrônico\s*-\s*([\d.]+)/(\d{4})\s*-\s*(\d{2})/(\d{2})/(\d{4})", nome_boletim)
    if not m:
        return False
    num = m.group(1)
    # Procura PDF com padrão BS-{num}-{ano}.pdf
    for pdf in pasta.glob(f"BS-{num}-*.pdf"):
        return True
    return False

def processar_mes(ano: int, mes_num: int, scraper, log_file):
    mes_sigla = mes_para_sigla(mes_num)
    pasta = BOLETINS_DIR / f"{ano}-{mes_num:02d}"
    pasta.mkdir(parents=True, exist_ok=True)
    
    log_file.write(f"\n{'='*60}\n")
    log_file.write(f"PROCESSANDO {mes_sigla}/{ano}\n")
    log_file.write(f"{'='*60}\n")
    log_file.flush()
    
    print(f"\n>>> Consultando {mes_sigla}/{ano}...")
    try:
        boletins = consultar(scraper, str(ano), mes_sigla)
    except Exception as e:
        log_file.write(f"ERRO na consulta: {e}\n")
        log_file.flush()
        return False, 0, 0
    
    if not boletins:
        log_file.write(f"Nenhum boletim encontrado para {mes_sigla}/{ano}\n")
        log_file.flush()
        return True, 0, 0
    
    log_file.write(f"Encontrados {len(boletins)} boletins\n")
    log_file.flush()
    print(f"  Encontrados: {len(boletins)} boletins")
    
    baixados = 0
    pulados = 0
    
    for i, b in enumerate(boletins, 1):
        nome = b["nome"]
        indice = b["indice"]
        
        # Verifica se já tem
        if ja_tem_pdf(pasta, nome):
            log_file.write(f"  [{i}/{len(boletins)}] JÁ TEM: {nome}\n")
            pulados += 1
            continue
        
        # Extrai número e data para nome do arquivo
        m = re.search(r"BS Eletrônico\s*-\s*([\d.]+)/(\d{4})\s*-\s*(\d{2})/(\d{2})/(\d{4})", nome)
        if not m:
            log_file.write(f"  [{i}/{len(boletins)}] ERRO parse nome: {nome}\n")
            continue
        
        num, ano_b, dia, mes_d, ano_d = m.groups()
        nome_arquivo = f"BS-{num}-{ano_b}.pdf"
        destino = pasta / nome_arquivo
        
        log_file.write(f"  [{i}/{len(boletins)}] Baixando: {nome} -> {nome_arquivo}\n")
        log_file.flush()
        print(f"  [{i}/{len(boletins)}] {nome_arquivo}...", end=" ")
        
        try:
            ok = baixar_um(scraper, str(ano), mes_sigla, indice, destino)
            if ok:
                log_file.write(f"     ✅ OK ({destino.stat().st_size} bytes)\n")
                baixados += 1
                print("✅")
            else:
                log_file.write(f"     ❌ FALHOU (não é PDF)\n")
                print("❌")
        except Exception as e:
            log_file.write(f"     ❌ EXCEÇÃO: {e}\n")
            print(f"❌ ({e})")
        
        log_file.flush()
        time.sleep(1)  # Rate limiting gentil
    
    log_file.write(f"\nResumo {mes_sigla}/{ano}: {baixados} baixados, {pulados} pulados (já existiam)\n")
    log_file.flush()
    print(f"  Resumo: {baixados} baixados, {pulados} pulados")
    return True, baixados, pulados

def main():
    parser = argparse.ArgumentParser(description="Baixa todos os boletins faltando")
    parser.add_argument("--inicio", default="2025-07", help="Mês inicial (YYYY-MM)")
    parser.add_argument("--fim", default="2026-08", help="Mês final (YYYY-MM)")
    parser.add_argument("--log", default="/opt/data/hermes-data/boletins_download.log")
    args = parser.parse_args()
    
    inicio_ano, inicio_mes = map(int, args.inicio.split("-"))
    fim_ano, fim_mes = map(int, args.fim.split("-"))
    
    scraper = cloudscraper.create_scraper(browser="chrome")
    
    with open(args.log, "a", encoding="utf-8") as log_file:
        log_file.write(f"\n{'#'*60}\n")
        log_file.write(f"INÍCIO: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Range: {args.inicio} a {args.fim}\n")
        log_file.write(f"{'#'*60}\n")
        log_file.flush()
        
        total_baixados = 0
        total_pulados = 0
        meses_ok = 0
        meses_falha = 0
        
        ano, mes = inicio_ano, inicio_mes
        while (ano < fim_ano) or (ano == fim_ano and mes <= fim_mes):
            ok, baixados, pulados = processar_mes(ano, mes, scraper, log_file)
            if ok:
                meses_ok += 1
                total_baixados += baixados
                total_pulados += pulados
            else:
                meses_falha += 1
                log_file.write(f"FALHA no mês {ano}-{mes:02d}, continuando...\n")
            
            # Próximo mês
            mes += 1
            if mes > 12:
                mes = 1
                ano += 1
            
            time.sleep(3)  # Pausa entre meses
        
        log_file.write(f"\n{'#'*60}\n")
        log_file.write(f"FIM: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"Meses OK: {meses_ok} | Falhas: {meses_falha}\n")
        log_file.write(f"Total baixados: {total_baixados} | Pulados: {total_pulados}\n")
        log_file.write(f"{'#'*60}\n")
    
    print(f"\n{'='*60}")
    print(f"CONCLUÍDO!")
    print(f"Meses processados: {meses_ok} OK, {meses_falha} falhas")
    print(f"Total baixados: {total_baixados}")
    print(f"Total pulados (já existiam): {total_pulados}")
    print(f"Log: {args.log}")

if __name__ == "__main__":
    main()
