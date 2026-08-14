#!/usr/bin/env python3
"""Baixa os boletins de junho/2025 faltantes, com retry e pausa contra rate-limit."""
import subprocess
import sys
import time
from pathlib import Path

NUMEROS = ["103", "103.1", "104", "105", "106", "107", "108", "108.1", "108.2",
           "109", "110", "111", "112", "112.1", "113", "114", "115", "116",
           "117", "117.1", "118"]
DIR = Path("/opt/data/hermes-data/boletins_tmp_jun")
SCRIPT = "/opt/data/hermes-data/hermes_mpt_ops/scripts/baixar_boletim.py"
PY = "/opt/data/hermes-data/hermes_mpt_ops/.venv-bol/bin/python"

DIR.mkdir(parents=True, exist_ok=True)

for num in NUMEROS:
    alvo = DIR / f"BS-{num}-2025.pdf"
    if alvo.exists():
        print(f"{num}: já baixado, pulando")
        continue
    ok = False
    for tent in range(5):
        r = subprocess.run([PY, SCRIPT, "2025", "JUN", "--baixar", num, "--dir", str(DIR)],
                           capture_output=True, text=True, timeout=90)
        out = r.stdout + r.stderr
        if f"BS-{num}-2025.pdf" in out and "✅" in out:
            ok = True
            print(f"{num}: OK")
            break
        print(f"{num}: tentativa {tent+1} falhou — {'erro 500/lento' if '500' in out or not out.strip() else out.strip()[:60]}")
        time.sleep(20)
    if not ok:
        print(f"{num}: ❌ falhou após 5 tentativas")
    time.sleep(12)

print("\n=== Resumo ===")
print(f"Baixados: {len(list(DIR.glob('*.pdf')))} arquivos")
print(f"Faltantes: {[n for n in NUMEROS if not (DIR / f'BS-{n}-2025.pdf').exists()]}")
