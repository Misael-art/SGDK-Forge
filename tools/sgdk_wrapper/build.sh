#!/bin/bash
PROJECT_DIR="${1:-$PWD}"
cd "$PROJECT_DIR" || exit 1

source "$(dirname "$0")/env.sh"

echo "[SGDK Wrapper] Building project in: $PWD"
make -f "$GDK/makefile.gen"

if [ $? -ne 0 ]; then
    echo "[ERROR] Build failed."
    exit 1
fi
echo "[OK] Build successful."
