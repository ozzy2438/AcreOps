#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

rsync -a --delete --exclude node_modules --exclude .next --exclude out "$ROOT/" "$TMP/"
rm -rf "$TMP/src/app/api"
ln -s "$ROOT/node_modules" "$TMP/node_modules"

cd "$TMP"
ACREOPS_STATIC_EXPORT=1 ACREOPS_BASE_PATH="${ACREOPS_BASE_PATH:-}" npm run build
rm -rf "$ROOT/out"
cp -a "$TMP/out" "$ROOT/out"
echo "Static export written to $ROOT/out"
