#!/bin/bash

CONFIG_DIR="{config_dir}"

CONFIG_PATH="$CONFIG_DIR/agio-env.sh"

if [ -f "$CONFIG_PATH" ]; then
    source "$CONFIG_PATH"
fi

AGIO_CLI="{agio_executable}"
