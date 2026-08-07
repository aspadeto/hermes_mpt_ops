#!/usr/bin/env python3
"""Decodifica base64 de boletins e salva em disco."""
import re, base64, sys

input_file = sys.argv[1]
output_dir = sys.argv[2] if len(sys.argv) > 2 else '/workspace/boletins-jul2026'

with open(input_file) as f:
    content = f.read()

# Each entry: [NOME] <base64>
blocks = re.findall(r'\[([^\]]+)\]\s+(data:[^\s]+)', content)

for name, b64data in blocks:
    start = b64data.find('base64,') + 7
    raw = b64data[start:]
    padding = len(raw) % 4
    if padding:
        raw += '=' * (4 - padding)
    pdf = base64.b64decode(raw)
    fname = f"{output_dir}/{name}"
    with open(fname, 'wb') as f:
        f.write(pdf)
    print(f"✅ {fname} — {len(pdf)} bytes")

print(f"\n📊 Total: {len(blocks)} boletins salvos em {output_dir}")