#!/bin/bash
PROJECT_DIR="${1:-$PWD}"
cd "$PROJECT_DIR" || exit 1

source "$(dirname "$0")/env.sh"

ROM_PATH="$PWD/out/rom.bin"
if [ ! -f "$ROM_PATH" ]; then
    echo "[ERROR] ROM not found at: $ROM_PATH"
    echo "Did you build the project first?"
    exit 1
fi

if [ -z "$SGDK_EMULATOR_PATH" ]; then
    echo "[ERROR] No emulator configured or found."
    exit 1
fi

echo "[SGDK Wrapper] Running ROM: $ROM_PATH"
echo "[SGDK Wrapper] Emulator: $SGDK_EMULATOR_PATH"

"$SGDK_EMULATOR_PATH" "$ROM_PATH" &
