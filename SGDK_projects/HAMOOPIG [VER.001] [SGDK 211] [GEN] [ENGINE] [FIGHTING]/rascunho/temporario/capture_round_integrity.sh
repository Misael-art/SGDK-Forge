#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
capture_mode="${1:-barrage}"
attack_key="${2:-a}"
session_id="interactive-round-integrity-$(date -u +%Y%m%dT%H%M%SZ)"
session_root="$project_root/out/emulator_evidence/$session_id"
source_rom="$project_root/out/rom.bin"
launch_rom="$session_root/$session_id.bin"
window_id=""
launcher_pid=""

pulse_key() {
    local key_name="$1"
    xdotool keydown --clearmodifiers --window "$window_id" "$key_name"
    sleep 0.10
    xdotool keyup --clearmodifiers --window "$window_id" "$key_name"
    sleep 0.10
}

mkdir -p "$session_root"
cp "$source_rom" "$launch_rom"
sha256sum "$launch_rom" > "$session_root/rom.sha256"
xdotool search --name 'BlastEm' > "$session_root/existing_windows.txt" 2>/dev/null || true

cleanup() {
    if [[ -n "$window_id" ]]; then
        xdotool key --window "$window_id" Escape 2>/dev/null || true
    fi
    if [[ -n "$launcher_pid" ]]; then
        wait "$launcher_pid" 2>/dev/null || true
    fi
}
trap cleanup EXIT

flatpak --user run \
    --filesystem="/mnt/sdcard/Projects/Sgdk Forge" \
    --env=SDL_AUDIODRIVER=dummy \
    --env=SDL_JOYSTICK_HIDAPI=0 \
    com.retrodev.blastem -r U "$launch_rom" > "$session_root/blastem.log" 2>&1 &
launcher_pid=$!

for _ in $(seq 1 200); do
    while IFS= read -r candidate; do
        if [[ -n "$candidate" ]] && ! grep -Fxq "$candidate" "$session_root/existing_windows.txt"; then
            title="$(xdotool getwindowname "$candidate" 2>/dev/null || true)"
            if [[ "$title" == *" - BlastEm - "*" fps" ]]; then
                window_id="$candidate"
                break
            fi
        fi
    done < <(xdotool search --name 'BlastEm' 2>/dev/null || true)
    [[ -n "$window_id" ]] && break
    sleep 0.1
done

if [[ -z "$window_id" ]]; then
    echo "round_capture_status=blocked reason=window_timeout session_root=$session_root"
    exit 1
fi

xdotool windowactivate --sync "$window_id"
sleep 3.5
import -window "$window_id" "$session_root/00_select.png"

# Default BlastEm mapping: a=A, Return=START, arrows=d-pad.
pulse_key a
sleep 0.35
sleep 1
xdotool keydown --clearmodifiers --window "$window_id" Return
sleep 0.35
xdotool keyup --clearmodifiers --window "$window_id" Return
sleep 2
import -window "$window_id" "$session_root/01_round1_start.png"

if [[ "$capture_mode" == "timeover" ]]; then
    sleep 58
    import -window "$window_id" "$session_root/02_before_timeover.png"
    sleep 10
    import -window "$window_id" "$session_root/03_after_timeover_reset.png"
    xdotool getwindowname "$window_id" > "$session_root/window_title.txt" 2>/dev/null || true
    mv "$launch_rom" "$session_root/rom.bin"
    echo "round_capture_status=captured mode=timeover session_root=$session_root"
    exit 0
fi

xdotool keydown --clearmodifiers --window "$window_id" Right
sleep 1.5
for hit in $(seq 1 52); do
    pulse_key "$attack_key"
    if [[ "$hit" == "18" || "$hit" == "36" || "$hit" == "52" ]]; then
        import -window "$window_id" "$session_root/02_round1_barrage_${hit}.png"
    fi
    sleep 0.14
done
sleep 5
import -window "$window_id" "$session_root/03_after_round1.png"

for hit in $(seq 1 72); do
    pulse_key "$attack_key"
    if [[ "$hit" == "18" || "$hit" == "36" || "$hit" == "52" || "$hit" == "72" ]]; then
        import -window "$window_id" "$session_root/04_round2_barrage_${hit}.png"
    fi
    sleep 0.14
done
xdotool keyup --clearmodifiers --window "$window_id" Right
sleep 6
import -window "$window_id" "$session_root/05_after_match.png"

pulse_key Return
sleep 2
import -window "$window_id" "$session_root/06_return_select.png"
xdotool getwindowname "$window_id" > "$session_root/window_title.txt" 2>/dev/null || true
mv "$launch_rom" "$session_root/rom.bin"
echo "round_capture_status=captured session_root=$session_root"
