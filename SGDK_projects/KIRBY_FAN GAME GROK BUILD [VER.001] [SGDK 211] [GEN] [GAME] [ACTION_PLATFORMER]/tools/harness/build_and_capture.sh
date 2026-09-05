#!/usr/bin/env bash
# FASE 3 harness: build ROM (wine bridge) + BlastEm sealed capture + gates.
# Usage:
#   tools/harness/build_and_capture.sh [scene_name] [scene_id]
# Examples:
#   tools/harness/build_and_capture.sh title_smoke
#   tools/harness/build_and_capture.sh stage_playtest 5
#   tools/harness/build_and_capture.sh boss_playtest 7
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MD_ROOT="$(cd "$PROJECT_ROOT/../.." && pwd)"
# project is under SGDK_projects/<name>; parent of SGDK_projects is MD_ROOT
if [ ! -d "$MD_ROOT/tools/sgdk_wrapper" ]; then
  MD_ROOT="$(cd "$PROJECT_ROOT/../../" && pwd)"
fi
if [ ! -d "$MD_ROOT/tools/sgdk_wrapper" ]; then
  # Walk up looking for tools/sgdk_wrapper
  probe="$PROJECT_ROOT"
  while [ "$probe" != "/" ]; do
    if [ -d "$probe/tools/sgdk_wrapper" ]; then
      MD_ROOT="$probe"
      break
    fi
    probe="$(dirname "$probe")"
  done
fi

SCENE_NAME="${1:-title_smoke}"
TARGET_SCENE="${2:-}"
WARMUP="${WARMUP_SECONDS:-14}"

mkdir -p "$PROJECT_ROOT/out/logs" "$PROJECT_ROOT/out/evidence/$SCENE_NAME"

echo "[harness] project=$PROJECT_ROOT"
echo "[harness] scene_name=$SCENE_NAME target_scene=${TARGET_SCENE:-default}"

echo "[harness] building via wine bridge..."
bash "$MD_ROOT/tools/sgdk_wrapper/build_sgdk_wine_bridge.sh" \
  --project-root "$PROJECT_ROOT" \
  | tee "$PROJECT_ROOT/out/logs/build_${SCENE_NAME}.log"

if [ ! -f "$PROJECT_ROOT/out/rom.bin" ]; then
  echo "[harness] ERROR: out/rom.bin missing after build"
  exit 2
fi

CAPTURE_ARGS=(
  --project-root "$PROJECT_ROOT"
  --output-base "$PROJECT_ROOT/out/evidence/$SCENE_NAME"
  --warmup-seconds "$WARMUP"
)
if [ -n "$TARGET_SCENE" ]; then
  CAPTURE_ARGS+=(--target-scene "$TARGET_SCENE")
fi

echo "[harness] capturing BlastEm evidence..."
bash "$MD_ROOT/tools/sgdk_wrapper/capture_blastem_evidence_linux.sh" \
  "${CAPTURE_ARGS[@]}" \
  | tee "$PROJECT_ROOT/out/logs/capture_${SCENE_NAME}.log"

BUNDLE="$(find "$PROJECT_ROOT/out/evidence/$SCENE_NAME" -type d -name 'blastem-linux-*' | sort | tail -1)"
if [ -z "$BUNDLE" ]; then
  echo "[harness] ERROR: no sealed bundle found"
  exit 2
fi

echo "[harness] gates on $BUNDLE"
python3 "$PROJECT_ROOT/tools/harness/gates.py" \
  --project-root "$PROJECT_ROOT" \
  "$BUNDLE" \
  | tee "$PROJECT_ROOT/out/logs/gates_${SCENE_NAME}.log"

echo "[harness] done bundle=$BUNDLE"
