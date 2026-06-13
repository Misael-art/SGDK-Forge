#!/bin/bash
PROJECT_DIR="${1:-$PWD}"
cd "$PROJECT_DIR" || exit 1

source "$(dirname "$0")/env.sh"

echo "[SGDK Wrapper] Cleaning project in: $PWD"
make -f "$GDK/makefile.gen" clean
