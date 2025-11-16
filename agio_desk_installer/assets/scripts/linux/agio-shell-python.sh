#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

CONFIG_SCRIPT="${SCRIPT_DIR}/agio-setup.sh"

if [ -f "$CONFIG_SCRIPT" ]; then
    source "$CONFIG_SCRIPT"
fi

uv run python
