#!/usr/bin/env bash
set -euo pipefail

# MISSAO 2026-08-24 - captura de variante de fase da jornada.
#
# Instrumentacao de laboratorio LOCAL deste projeto (nao e o contrato SBIS
# compartilhado): escreve SBIS@0x120 (boot na STAGE) + JBOY@0x140
# (stageIndex/flags, ver inc/systems/journey.h) no save.sram do BlastEm
# flatpak antes do boot, roda o emulador e captura a tela.
#
# Uso: capture_journey_variant.sh --project-root <dir> --stage 1 [--warmup 25]

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
project_root=""
stage="0"
warmup="25"
boss_pending="0"
final_boss="0"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-root) project_root="$2"; shift 2 ;;
        --stage) stage="$2"; shift 2 ;;
        --warmup) warmup="$2"; shift 2 ;;
        --boss-pending) boss_pending="$2"; shift 2 ;;
        --final-boss) final_boss="$2"; shift 2 ;;
        *) echo "journey_capture_status=blocked reason=unknown_argument argument=$1"; exit 2 ;;
    esac
done

[[ -n "$project_root" ]] || { echo "blocked: project_root_required"; exit 2; }
project_root="$(cd "$project_root" && pwd)"
rom_path="$project_root/out/rom.bin"
[[ -f "$rom_path" ]] || { echo "blocked: rom_missing"; exit 1; }

flatpak_root="$HOME/.var/app/com.retrodev.blastem"
session_id="journey-s${stage}-$(date -u +%Y%m%dT%H%M%SZ)-$$"
session_root="$project_root/out/evidence/journey/$session_id"
mkdir -p "$session_root"
cp "$rom_path" "$session_root/${session_id}.bin"
launch_rom="$session_root/${session_id}.bin"
screenshot_path="$session_root/screenshot.png"
emulator_log="$session_root/blastem.log"

python3 - "$HOME/.var/app/com.retrodev.blastem/data/blastem" "$session_id" "$stage" "$boss_pending" "$final_boss" <<'PY'
import sys
from pathlib import Path

base = Path(sys.argv[1])
sid = sys.argv[2]
stage = int(sys.argv[3])
boss = int(sys.argv[4])
final = int(sys.argv[5])

sram_dir = base / sid
sram_dir.mkdir(parents=True, exist_ok=True)
path = sram_dir / "save.sram"

payload = bytearray(0x200)

# SBIS @0x120: version=1, length=12, scene=STAGE(4)
offset = 0x120
payload[offset:offset+4] = b"SBIS"
scene_id = 4
words = (1, 12, scene_id, 0xA55A ^ 1 ^ 12 ^ scene_id)
for i, v in enumerate(words):
    payload[offset+4+i*2:offset+6+i*2] = v.to_bytes(2, "big")

# JBOY @0x140
offset = 0x140
payload[offset:offset+4] = b"JBOY"
payload[offset+4] = stage
payload[offset+5] = (boss & 1) | ((final & 1) << 1)

path.write_bytes(payload)
print(f"sram_written={path}")
PY

expected_sha="$(sha256sum "$launch_rom" | awk '{print $1}')"
echo "$expected_sha" > "$session_root/rom.sha256"
echo "$session_id stage=$stage boss_pending=$boss_pending final_boss=$final_boss" > "$session_root/request.txt"

xdotool search --name 'BlastEm' >"$session_root/pre_windows.txt" 2>/dev/null || true

flatpak --user run \
    --filesystem="$project_root" \
    --env="SDL_AUDIODRIVER=dummy" \
    --env=SDL_JOYSTICK_HIDAPI=0 \
    com.retrodev.blastem -r U "$launch_rom" >"$emulator_log" 2>&1 &
emu_pid=$!

window_id=""
for _ in $(seq 1 200); do
    while IFS= read -r candidate; do
        [[ -n "$candidate" ]] || continue
        grep -Fxq "$candidate" "$session_root/pre_windows.txt" && continue
        title="$(xdotool getwindowname "$candidate" 2>/dev/null || true)"
        if [[ "$title" == *" - BlastEm - "*" fps" ]]; then
            window_id="$candidate"
            break
        fi
    done < <(xdotool search --name 'BlastEm' 2>/dev/null || true)
    [[ -n "$window_id" ]] && break
    sleep 0.25
done

if [[ -z "$window_id" ]]; then
    kill "$emu_pid" 2>/dev/null || true
    echo "journey_capture_status=blocked reason=no_blastem_window session=$session_id"
    exit 1
fi

sleep "$warmup"
import -window "$window_id" "$screenshot_path" 2>/dev/null || true
kill "$emu_pid" 2>/dev/null || true
wait "$emu_pid" 2>/dev/null || true

if [[ -s "$screenshot_path" ]]; then
    echo "journey_capture_status=captured session=$session_id stage=$stage shot=$screenshot_path"
else
    echo "journey_capture_status=blocked reason=screenshot_missing session=$session_id"
    exit 1
fi
