#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

python3 - "$ROOT" "$TMP" <<'PY'
import os
import shutil
import sys

root, tmp = sys.argv[1], sys.argv[2]
skip = {".next", "out", "node_modules", ".git"}
os.makedirs(tmp, exist_ok=True)
for name in os.listdir(root):
    if name in skip:
        continue
    src = os.path.join(root, name)
    dest = os.path.join(tmp, name)
    if os.path.isdir(src):
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        shutil.copy2(src, dest)
PY

ln -s "$ROOT/node_modules" "$TMP/node_modules"
rm -rf "$TMP/src/app/api"

cd "$TMP"
ACREOPS_STATIC_EXPORT=1 ACREOPS_BASE_PATH="${ACREOPS_BASE_PATH:-}" npm run build
rm -rf "$ROOT/out"
cp -a "$TMP/out" "$ROOT/out"
echo "Static export written to $ROOT/out"
