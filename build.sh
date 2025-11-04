#!/usr/bin/env bash

set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="$ROOT"

if [ -z "$1" ]; then
  OUTPUT_DIR="$ROOT/dist"
else
  OUTPUT_DIR="$1"
fi

mkdir -p "$OUTPUT_DIR"

uv run --active python -m nuitka \
  --onefile \
  --standalone \
  --enable-plugin=pyside6 \
  --follow-imports \
  --include-package=agio \
  --include-package=agio.tools \
  --include-qt-plugins=platforms \
  --output-dir="$OUTPUT_DIR" \
  --remove-output \
  --output-filename=agio_desk_installer \
  --include-data-dir=agio_desk_installer/assets=assets \
  agio_desk_installer/main.py

echo
echo "Output file: $OUTPUT_DIR/agio_desk_installer"
