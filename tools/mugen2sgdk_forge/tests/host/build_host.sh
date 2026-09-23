#!/usr/bin/env bash
# Compila runtime + dados gerados de um projeto no host. Uso: build_host.sh <projeto> <saida> [cflags...]
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
proj="$1"; out="$2"; shift 2
work="$(dirname "$out")/host_build"
rm -rf "$work"; mkdir -p "$work/mg" "$work/mg_gen"
cp "$here/genesis.h" "$work/"
cp "$proj"/inc/mg/*.h "$work/mg/"; cp "$proj"/inc/mg_gen/*.h "$work/mg_gen/"
for f in "$proj"/src/mg/*.c "$proj"/src/mg_gen/*.c; do cp "$f" "$work/$(basename "$f")"; done
python3 "$here/stub_res.py" "$proj"/res/mgres_*.h > "$work/host_res.c"
cp "$proj"/res/mgres_*.h "$work/"
sed -i 's/#include <genesis.h>/#include "genesis.h"/' "$work"/*.h "$work"/mg/*.h 2>/dev/null || true
main_src="${MG_HOST_MAIN:-$here/harness.c}"
gcc -std=gnu11 -Wall -Wno-unused-function "$@" -I"$work" -o "$out" "$work"/*.c "$main_src"
