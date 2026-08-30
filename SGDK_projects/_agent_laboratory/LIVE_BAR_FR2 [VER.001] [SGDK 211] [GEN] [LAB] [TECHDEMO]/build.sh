#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
exec "$ROOT/tools/sgdk_wrapper/build.sh" "$(cd "$(dirname "$0")" && pwd)"
