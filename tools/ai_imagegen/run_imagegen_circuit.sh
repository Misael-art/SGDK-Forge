#!/usr/bin/env bash
# run_imagegen_circuit.sh
# Wrapper Bash/SteamOS do imagegen_circuit.py (Ring 1).
# Espelho POSIX do run_imagegen_circuit.ps1.
#
# Uso:
#   ./run_imagegen_circuit.sh preflight --project "<nome>" --asset-role concept_art [--style-manifest PATH] [--json]
#   ./run_imagegen_circuit.sh run       --project "<nome>" --asset-role concept_art --prompt "..." [--seed 42] [--dry-run] [--json]
#
# Exit codes (espelham imagegen_circuit.py):
#   0  ok
#   2  license_blocked
#   3  scope_blocked
#   4  blocked_host_capability
#   5  forbidden scope
#   6  backend refused
#   7  filesystem error
#
# Este wrapper NAO escreve em res/. Toda persistencia eh em
# <project>/data/raw_ai/, <project>/data/source_art/ ou <project>/out/logs/.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PY="${PYTHON:-python3}"

if [ $# -lt 1 ]; then
    echo "Usage: $0 {preflight|run} [args...]" >&2
    exit 7
fi

CMD="$1"; shift
if [ "$CMD" != "preflight" ] && [ "$CMD" != "run" ]; then
    echo "ERROR: first arg must be 'preflight' or 'run' (got: $CMD)" >&2
    exit 7
fi

ARGS=("$CMD")
JSON_OUT=0
WRITE_DEC=0
DRY=0
ASSET_ROLE=""
PROMPT=""
NEG=""
SEED=""
WIDTH=1024
HEIGHT=1024
PROFILE="bonsai_4b_ternary"
PROJECT=""
PROJECT_ROOT=""
STYLE_MANIFEST=""
NC=0
NI=0

while [ $# -gt 0 ]; do
    case "$1" in
        --json)            ARGS+=("--json"); JSON_OUT=1 ;;
        --write-decision)  ARGS+=("--write-decision"); WRITE_DEC=1 ;;
        --dry-run)         ARGS+=("--dry-run"); DRY=1 ;;
        --project)         PROJECT="$2"; ARGS+=("--project" "$2"); shift ;;
        --project-root)    PROJECT_ROOT="$2"; ARGS+=("--project-root" "$2"); shift ;;
        --asset-role)      ASSET_ROLE="$2"; ARGS+=("--asset-role" "$2"); shift ;;
        --style-manifest)  STYLE_MANIFEST="$2"; ARGS+=("--style-manifest" "$2"); shift ;;
        --native-callable) NC=1; ARGS+=("--native-callable" "true") ;;
        --native-inline)   NI=1; ARGS+=("--native-inline" "true") ;;
        --prompt)          PROMPT="$2"; ARGS+=("--prompt" "$2"); shift ;;
        --negative)        NEG="$2"; ARGS+=("--negative" "$2"); shift ;;
        --seed)            SEED="$2"; ARGS+=("--seed" "$2"); shift ;;
        --width)           WIDTH="$2"; ARGS+=("--width" "$2"); shift ;;
        --height)          HEIGHT="$2"; ARGS+=("--height" "$2"); shift ;;
        --profile)         PROFILE="$2"; ARGS+=("--profile" "$2"); shift ;;
        -h|--help)         sed -n '2,40p' "$0"; exit 0 ;;
        *)                 echo "ERROR: unknown arg: $1" >&2; exit 7 ;;
    esac
    shift
done

if [ "$CMD" = "run" ] && [ -z "$ASSET_ROLE" ]; then
    echo "ERROR: --asset-role is required for run." >&2
    exit 7
fi

exec "$PY" "$SCRIPT_DIR/imagegen_circuit.py" "${ARGS[@]}"
