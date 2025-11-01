#!/usr/bin/env bash

#sudo apt install ccache

set PYTHONPATH=$PWD

core_path=/home/paul/pw-storage/dev/work/agio/packages/agio-core
export PYTHONPATH=$core_path

uv run --active python -m nuitka \
  --onefile \
  --standalone \
  --enable-plugin=pyside6 \
  --follow-imports \
  --include-qt-plugins=platforms \
  --output-dir=./dest \
  --remove-output \
  --output-filename=agio_desk_installer \
  --include-data-dir=agio_desk_installer/assets=assets \
  agio_desk_installer/main.py

