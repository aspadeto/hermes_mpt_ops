#!/usr/bin/env python3
"""
Backup /home/hermes/.hermes + /opt/data/hermes-data to Google Drive with rotation.
Keeps 7 daily backups, then 1 per week for older ones.
"""

import json
import os
import re
import subprocess
import sys
import tarfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Importa configuração centralizada de caminhos
from ops_paths import HERMES_DATA_ROOT

HERMES_HOME = "/home/hermes/.hermes"
DATA_DIR = str(HERMES_DATA_ROOT)
VENV_PYTHON = "/opt/data/hermes-data/.google-venv/bin/python"
API_SCRIPT = f"{HERMES_HOME}/skills/productivity/google-workspace/scripts/google_api.py"
BACKUP_DIR = "/tmp/hermes-backup"
DRIVE_FOLDER_NAME = "HermesBackup"

# Excluded from .hermes/
EXCLUDE_PATTERNS = [
    "cache/",
    "home/",
    ".ssh/",  # chaves privadas — nunca ir para o backup (Drive)
    "audio_cache/",
    "image_cache/",
    "lazy-packages/",
    "sandboxes/",
    "logs/",
    "sessions/",
    "webui/",
    # Regeneráveis em DR — código/venv/instalação (não são dados do usuário)
    "hermes-agent/",   # código + venv do agente (reinstalável via pip/install)
    "node/",           # runtime Node (reinstalável)
    "lsp/",            # language servers (reinstaláveis)
    "backups/",        # zip de backup antigo (não duplicar no Drive)
    "state-snapshots/",
    "kanban.db*",
    "response_store.db*",
    "state.db*",
    "verification_evidence.db",
    "models_dev_cache.json",
    ".skills_prompt_snapshot.json",
    # Regeneráveis baixáveis (não são dados do usuário) — em qq profundidade
]

# Glob: diretórios/arquivos regeneráveis por download/instalação, casados em
# QUALQUER nível do path (caches de modelo, binários, .hub, retina de pip/npm)
GLOBAL_EXCLUDE_SUBSTR = [
    ".cache",
    ".model-cache",
    ".hub/index-cache",
    "/models/",          # modelos ML baixados (gguf, onnx, embeddings)
    "/bin/uv",
    "/bin/tirith",
    ".npm/",
    "huggingface/hub",   # modelos HF baixados
    "/.github",          # apenas questão de segurança/limpeza se aparecer
]

# Excluded from data/ — repos git são versionados no GitHub,
# backups/ é alvo da rotação, .google-venv é ambiente
DATA_EXCLUDE = {".google-venv", ".tool-venv", "mpt_workspace", "backups", "ottomator-agents"}

# Segredos/config do HOST fora dos 2 diretórios padrão (VM nativa — ago/2026).
# Cada tupla: (caminho_origem_no_host, arcname_dentro_do_tar.gz).
# Incluídos em "host-secrets/" para restauração completa em DR.
EXTRA_SECRETS = [
    ("/home/hermes/hermes-webui/.env", "host-secrets/webui.env"),
    ("/home/hermes/.config/himalaya", "host-secrets/himalaya"),
    ("/home/hermes/.git-credentials", "host-secrets/git-credentials"),
    ("/home/hermes/GITHUB_TOKEN.txt", "host-secrets/GITHUB_TOKEN.txt"),
]

# ── helpers ──────────────────────────────────────────────

def run_gapi(*args: str) -> dict:
    cmd = [VENV_PYTHON, API_SCRIPT] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(f"gapi error: {result.stderr.strip() or result.stdout.strip()}")
    return json.loads(result.stdout) if result.stdout.strip() else {}


def ensure_drive_folder() -> str:
    """Create or find the backup folder on Drive. Returns folder ID."""
    query = f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    result = run_gapi("drive", "search", query, "--raw-query", "--max", "5")
    for item in result:
        if item.get("name") == DRIVE_FOLDER_NAME:
            return item["id"]
    result = run_gapi("drive", "create-folder", DRIVE_FOLDER_NAME)
    return result["id"]


def list_drive_files(folder_id: str) -> list[dict]:
    """List backup files in the Drive folder."""
    query = f"'{folder_id}' in parents and trashed=false"
    result = run_gapi("drive", "search", query, "--raw-query", "--max", "100")
    return result


def parse_backup_date(name: str) -> datetime | None:
    """Extract datetime from filename like hermes-backup-20260730_044500.tar.gz"""
    m = re.search(r"hermes-backup-(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})", name)
    if m:
        return datetime(int(m[1]), int(m[2]), int(m[3]),
                        int(m[4]), int(m[5]), int(m[6]), tzinfo=timezone.utc)
    return None


def delete_drive_file(file_id: str, name: str):
    """Delete a file from Drive."""
    print(f"  🗑  Deleting old backup: {name}")
    run_gapi("drive", "delete", file_id)


def create_tar_gz() -> str:
    """Create a compressed tar of HERMES_HOME + DATA_DIR, returns path."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"hermes-backup-{timestamp}.tar.gz"
    path = os.path.join(BACKUP_DIR, filename)

    def filter_hermes(tarinfo):
        name = tarinfo.name
        for pat in EXCLUDE_PATTERNS:
            if pat.endswith("*"):
                base = pat.rstrip("*")
                if name.startswith(f".hermes/{base}") or name == f".hermes/{base}":
                    return None
            elif f".hermes/{pat}" in name or name == f".hermes/{pat}":
                return None
        return tarinfo

    def filter_data(tarinfo):
        """Exclude backups/ and wiki/ from data/ backup."""
        name = tarinfo.name
        parts = name.split("/")
        if len(parts) >= 2 and parts[1] in DATA_EXCLUDE:
            return None
        return tarinfo

    print(f"  📦 Creating backup: {filename}")
    with tarfile.open(path, "w:gz", compresslevel=6) as tar:
        tar.add(HERMES_HOME, arcname=".hermes", filter=filter_hermes)
        tar.add(DATA_DIR, arcname="data", filter=filter_data)
        # Segredos/config do host fora dos 2 diretórios padrão (VM nativa)
        for origem, arcname in EXTRA_SECRETS:
            if os.path.exists(origem):
                tar.add(origem, arcname=arcname)
            else:
                print(f"  ⚠️  EXTRA_SECRETS: {origem} não existe — pulando")

    size_mb = os.path.getsize(path) / 1024 / 1024
    print(f"  💾 Size: {size_mb:.1f} MB")
    return path


def upload_backup(local_path: str, folder_id: str):
    """Upload backup file to Drive."""
    print(f"  ☁️  Uploading to Google Drive...")
    result = run_gapi("drive", "upload", local_path, "--name", os.path.basename(local_path), "--parent", folder_id)
    print(f"  ✅ Uploaded: {result.get('name', 'unknown')} (ID: {result.get('id', '?')})")


def rotate_backups(files: list[dict]):
    """
    Rotation strategy:
    - Keep 7 most recent daily backups
    - After 7 days, keep 1 per week
    """
    backups = []
    for f in files:
        dt = parse_backup_date(f["name"])
        if dt:
            backups.append({"id": f["id"], "name": f["name"], "date": dt})

    if not backups:
        return

    backups.sort(key=lambda x: x["date"], reverse=True)

    # Keep the most recent 7
    keep = set()
    for b in backups[:7]:
        keep.add(b["id"])

    # For backups older than 7 days, keep 1 per week (ISO week number)
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    weekly_kept: dict[str, str] = {}
    for b in backups:
        if b["date"] < cutoff:
            week_key = b["date"].strftime("%Y-W%W")
            if week_key not in weekly_kept:
                weekly_kept[week_key] = b["id"]
                keep.add(b["id"])

    # Delete the rest
    deleted = sum(1 for b in backups if b["id"] not in keep)
    for b in backups:
        if b["id"] not in keep:
            delete_drive_file(b["id"], b["name"])

    if deleted:
        print(f"  🧹 Removed {deleted} old backup(s)")
    else:
        print(f"  ✅ No backups to prune")


# ── main ────────────────────────────────────────────────

def main():
    print("=" * 50)
    print(f"🔐 Hermes Backup — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 50)

    try:
        local_path = create_tar_gz()
        folder_id = ensure_drive_folder()
        print(f"  📁 Drive folder: {DRIVE_FOLDER_NAME} (ID: {folder_id})")

        existing = list_drive_files(folder_id)
        print(f"  📋 Found {len(existing)} existing backup(s) on Drive")

        upload_backup(local_path, folder_id)
        rotate_backups(existing)

        os.remove(local_path)
        print(f"  🧹 Local temp file removed")

        print("=" * 50)
        print("✅ Backup concluído com sucesso!")
        print("=" * 50)

    except Exception as e:
        print(f"❌ ERRO: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
