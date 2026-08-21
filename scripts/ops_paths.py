#!/usr/bin/env python3
"""
ops_paths.py — Configuração centralizada de caminhos para OPS e KB.

Este módulo define OPS_PATH e KB_PATH de forma única.
Todos os scripts devem importar daqui em vez de definir caminhos hardcoded.

Ordem de prioridade:
1. Variáveis de ambiente OPS_PATH / KB_PATH (para overrides em cron, CI, etc.)
2. Default: /opt/data/hermes-data/mpt_workspace/hermes_mpt_ops e /opt/data/hermes-data/mpt_workspace/hermes_mpt_kb
"""

import os
from pathlib import Path

# Base do workspace (pode ser alterado via HERMES_DATA_ROOT)
HERMES_DATA_ROOT = Path(os.environ.get("HERMES_DATA_ROOT", "/opt/data/hermes-data"))

# Caminhos dos repositórios
OPS_PATH = Path(os.environ.get("OPS_PATH", HERMES_DATA_ROOT / "mpt_workspace" / "hermes_mpt_ops"))
KB_PATH = Path(os.environ.get("KB_PATH", HERMES_DATA_ROOT / "mpt_workspace" / "hermes_mpt_kb"))

# Subpastas comuns
OPS_SCRIPTS = OPS_PATH / "scripts"
OPS_DATA = OPS_PATH / "data"
OPS_SKILLS = OPS_PATH / "skills"
OPS_CONFIGS = OPS_PATH / "configs"

KB_RAW_BOLETINS = KB_PATH / "raw" / "boletins"
KB_BOLETINS = KB_PATH / "boletins"
KB_BOLETINS_DOCLING = KB_PATH / "boletins_docling"
KB_CONCEPTS = KB_PATH / "concepts"
KB_ENTITIES = KB_PATH / "entities"
KB_DATA = KB_PATH / "data"
KB_INFO = KB_PATH / "info"
KB_INITIATIVES = KB_PATH / "initiatives"
KB_MODELOS = KB_PATH / "modelos"
KB_PGEAS = KB_PATH / "pgeas"
KB_PROCESSES = KB_PATH / "processes"
KB_REFERENCIAS = KB_PATH / "referencias"
KB_SCRIPTS = KB_PATH / "scripts"

# Banco de dados
PENDENCIAS_DB = OPS_DATA / "pendencias.db"
ATOS_DB = OPS_DATA / "atos.db"
INDICES_DIR = OPS_DATA / "indices"

# Logs
BOLETINS_DOWNLOAD_LOG = HERMES_DATA_ROOT / "boletins_download.log"

# Garante que pastas essenciais existam
for p in (OPS_DATA, INDICES_DIR, KB_BOLETINS, KB_BOLETINS_DOCLING, KB_RAW_BOLETINS):
    p.mkdir(parents=True, exist_ok=True)


def main():
    """Teste rápido: imprime todos os caminhos."""
    for name in dir():
        if name.isupper() and not name.startswith("_"):
            val = globals()[name]
            if isinstance(val, Path):
                print(f"{name} = {val}")


if __name__ == "__main__":
    main()