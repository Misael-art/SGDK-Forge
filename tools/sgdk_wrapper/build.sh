#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${1:-$PWD}"
PROJECT_DIR="$(cd "$PROJECT_DIR" && pwd)"

if [[ "$(uname -s)" == "Linux" ]]; then
    exec "$SCRIPT_DIR/build_sgdk_wine_bridge.sh" --project-root "$PROJECT_DIR"
else
    cd "$PROJECT_DIR" || exit 1
    source "$SCRIPT_DIR/env.sh"
    echo "[SGDK Wrapper] Building project in: $PWD"
    make -f "$GDK/makefile.gen"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Build failed."
        exit 1
    fi
    echo "[OK] Build successful."
fi
