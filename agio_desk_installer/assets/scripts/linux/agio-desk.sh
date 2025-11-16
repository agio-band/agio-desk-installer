#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

CONFIG_SCRIPT="${SCRIPT_DIR}/agio-setup.sh"

if [ -f "$CONFIG_SCRIPT" ]; then
    source "$CONFIG_SCRIPT"
fi

if [ -x "$AGIO_CLI" ]; then
    "$AGIO_CLI" desk
else
    echo "Error: AGIO_CLI executable not found or is not executable: $AGIO_CLI" >&2
    exit 1
fi
