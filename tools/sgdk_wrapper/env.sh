#!/bin/bash
# SGDK Environment Auto-Setup Wrapper

# Find MegaDrive_DEV root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
MD_ROOT="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"

export GDK="$MD_ROOT/sdk/sgdk-2.11"
export GDK_WIN="$GDK"  # Keep for compatibility
export PATH="$GDK/bin:$PATH"

EMU_DIR="$MD_ROOT/tools/emuladores"

if [ -f "$EMU_DIR/BizHawk/EmuHawk.exe" ]; then
    export SGDK_EMULATOR_PATH="$EMU_DIR/BizHawk/EmuHawk.exe"
elif [ -f "$EMU_DIR/Blastem/Blastem.exe" ]; then
    export SGDK_EMULATOR_PATH="$EMU_DIR/Blastem/Blastem.exe"
elif [ -f "$EMU_DIR/Exodus_2.1/Exodus.exe" ]; then
    export SGDK_EMULATOR_PATH="$EMU_DIR/Exodus_2.1/Exodus.exe"
elif [ -f "$EMU_DIR/GensKMod/gens.exe" ]; then
    export SGDK_EMULATOR_PATH="$EMU_DIR/GensKMod/gens.exe"
else
    export SGDK_EMULATOR_PATH=""
    echo "[WARNING] No emulator found in $EMU_DIR"
fi
