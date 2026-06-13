#!/usr/bin/env bash
# imagegen_tool.sh
# Wrapper Bash/SteamOS para imagegen_tool.py
# Uso: ./imagegen_tool.sh [status|install|route|generate|convert|healthcheck] [args]

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 "${SCRIPT_DIR}/imagegen_tool.py" "$@"
