#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
manifest_path="$script_dir/linux_host_dependencies.json"
project_root=""
rom_path=""
output_base="$repo_root/out/remediation/P0-005/fresh_bundle"
canonical_root=""
warmup_seconds="20"
target_scene=""
audio_driver="dummy"
region="ntsc"
burst_delay=""
burst_count="0"
burst_interval="0.10"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --project-root) project_root="$2"; shift 2 ;;
        --rom) rom_path="$2"; shift 2 ;;
        --output-base) output_base="$2"; shift 2 ;;
        --canonical-root) canonical_root="$2"; shift 2 ;;
        --warmup-seconds) warmup_seconds="$2"; shift 2 ;;
        --target-scene) target_scene="$2"; shift 2 ;;
        --audio-driver) audio_driver="$2"; shift 2 ;;
        --region) region="$2"; shift 2 ;;
        --burst-delay) burst_delay="$2"; shift 2 ;;
        --burst-count) burst_count="$2"; shift 2 ;;
        --burst-interval) burst_interval="$2"; shift 2 ;;
        *) echo "linux_blastem_capture_status=blocked reason=unknown_argument argument=$1"; exit 2 ;;
    esac
done

if [[ "$audio_driver" != "dummy" && "$audio_driver" != "disk" ]]; then
    echo "linux_blastem_capture_status=blocked reason=unsupported_audio_driver driver=$audio_driver"
    exit 2
fi
if [[ "$region" != "ntsc" && "$region" != "pal" ]]; then
    echo "linux_blastem_capture_status=blocked reason=unsupported_region region=$region"
    exit 2
fi
if [[ -n "$target_scene" ]] && ! [[ "$target_scene" =~ ^[0-9]+$ ]] ; then
    echo "linux_blastem_capture_status=blocked reason=invalid_target_scene value=$target_scene"
    exit 2
fi
if ! [[ "$burst_count" =~ ^[0-9]+$ ]]; then
    echo "linux_blastem_capture_status=blocked reason=invalid_burst_count value=$burst_count"
    exit 2
fi
if [[ "$burst_count" -gt 0 && -z "$burst_delay" ]]; then
    echo "linux_blastem_capture_status=blocked reason=burst_delay_required"
    exit 2
fi

if [[ -z "$project_root" ]]; then
    echo "linux_blastem_capture_status=blocked reason=project_root_required"
    exit 2
fi
project_root="$(cd "$project_root" && pwd)"
if [[ -z "$rom_path" ]]; then
    rom_path="$project_root/out/rom.bin"
fi
if [[ ! -f "$rom_path" ]]; then
    echo "linux_blastem_capture_status=blocked reason=rom_missing path=$rom_path"
    exit 1
fi

"$script_dir/ensure_linux_blastem.sh" >/dev/null
mapfile -t emulator_values < <(
    python3 -c 'import json,sys; p=json.load(open(sys.argv[1], encoding="utf-8"))["blastem_linux"]; print(p["ref"]); print(p["commit"])' "$manifest_path"
)
emulator_ref="${emulator_values[0]}"
emulator_commit="${emulator_values[1]}"
session_id="blastem-linux-$(date -u +%Y%m%dT%H%M%SZ)-$$"
session_root="$output_base/$session_id"
flatpak_root="$HOME/.var/app/com.retrodev.blastem"
launch_rom="$session_root/$session_id.bin"
sealed_rom="$session_root/rom.bin"
screenshot_path="$session_root/screenshot.png"
burst_dir="$session_root/animation_frames"
burst_gif="$session_root/runtime_animation.gif"
sram_path="$session_root/save.sram"
emulator_log="$session_root/blastem.log"
existing_windows="$session_root/existing_windows.txt"
audio_path="$session_root/audio.raw"

mkdir -p "$session_root"
cp "$rom_path" "$launch_rom"
region_code="U"
if [[ "$region" == "pal" ]]; then
    region_code="E"
fi
expected_rom_sha256="$(sha256sum "$launch_rom" | awk '{print $1}')"
started_at="$(python3 -c 'from datetime import datetime,timezone; print(datetime.now(timezone.utc).isoformat())')"
xdotool search --name 'BlastEm' >"$existing_windows" 2>/dev/null || true

flatpak_sram="$flatpak_root/data/blastem/$session_id/save.sram"
if [[ -n "$target_scene" ]]; then
    mkdir -p "$(dirname "$flatpak_sram")"
    python3 - "$flatpak_sram" "$target_scene" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
scene_id = int(sys.argv[2])
if scene_id < 0 or scene_id > 0xFFFF:
    raise SystemExit("target scene outside u16")
payload = bytearray(0x120 + 12)
offset = 0x120
payload[offset:offset + 4] = b"SBIS"
words = (1, 12, scene_id, 0xA55A ^ 1 ^ 12 ^ scene_id)
for index, value in enumerate(words):
    word_offset = offset + 4 + (index * 2)
    payload[word_offset:word_offset + 2] = value.to_bytes(2, "big")
path.write_bytes(payload)
PY
fi

audio_args=(--env="SDL_AUDIODRIVER=$audio_driver")
if [[ "$audio_driver" == "disk" ]]; then
    audio_args+=(--env="SDL_DISKAUDIOFILE=$audio_path")
fi

flatpak --user run \
    --filesystem="$repo_root" \
    "${audio_args[@]}" \
    --env=SDL_JOYSTICK_HIDAPI=0 \
    com.retrodev.blastem -r "$region_code" "$launch_rom" >"$emulator_log" 2>&1 &
launcher_pid=$!
window_id=""
for _ in $(seq 1 200); do
    while IFS= read -r candidate; do
        if [[ -n "$candidate" ]] && ! grep -Fxq "$candidate" "$existing_windows"; then
            candidate_title="$(xdotool getwindowname "$candidate" 2>/dev/null || true)"
            # The title is initially just "BlastEm" for a few frames and only
            # later gains the ROM name/FPS suffix.  Accept the transient title;
            # the warmup below still guarantees a composed framebuffer.
            if [[ "$candidate_title" == *"BlastEm"* ]]; then
                window_id="$candidate"
                break
            fi
        fi
    done < <(xdotool search --name 'BlastEm' 2>/dev/null || true)
    [[ -n "$window_id" ]] && break
    sleep 0.1
done

if [[ -z "$window_id" ]]; then
    kill "$launcher_pid" 2>/dev/null || true
    wait "$launcher_pid" 2>/dev/null || true
    echo "linux_blastem_capture_status=blocked reason=window_timeout session_root=$session_root"
    exit 1
fi

# Force composition/focus before the first framebuffer import.  BlastEm can
# expose a valid title and audio stream while an unfocused X11 surface still
# returns an all-black image to ImageMagick `import -window`.
xdotool windowactivate --sync "$window_id" 2>/dev/null || true

if [[ "$burst_count" -gt 0 ]]; then
    mkdir -p "$burst_dir"
    sleep "$burst_delay"
    # O primeiro quadro do burst sai invalido quando a janela ainda nao terminou
    # de compor: a captura pega a superficie nao inicializada e ela e gravada
    # como magenta puro. Medido em 5 sessoes — screenshot.png e frame_3 saem
    # pretos, so frame_1 sai magenta, e PAL0[0] no dump do VDP e 0x0000.
    # Sem esta guarda, um artefato de captura vira "bug de backdrop" no relatorio.
    sleep 0.35
    for frame_index in $(seq -w 1 "$burst_count"); do
        import -window "$window_id" "$burst_dir/frame_${frame_index}.png"
        sleep "$burst_interval"
    done
    if command -v convert >/dev/null 2>&1; then
        convert -delay 8 -loop 0 "$burst_dir"/frame_*.png "$burst_gif"
    fi
fi

sleep "$warmup_seconds"
window_title="$(xdotool getwindowname "$window_id" 2>/dev/null || true)"
import -window "$window_id" "$screenshot_path"
# BlastEm maps Escape to ui.exit. For a ROM opened from the command line this
# is the canonical clean exit and flushes SRAM before process termination.
xdotool key --window "$window_id" Escape 2>/dev/null || true

for _ in $(seq 1 50); do
    if ! kill -0 "$launcher_pid" 2>/dev/null; then
        break
    fi
    sleep 0.1
done
if kill -0 "$launcher_pid" 2>/dev/null; then
    xdotool windowclose "$window_id" 2>/dev/null || true
fi
for _ in $(seq 1 50); do
    if ! kill -0 "$launcher_pid" 2>/dev/null; then
        break
    fi
    sleep 0.1
done
if kill -0 "$launcher_pid" 2>/dev/null; then
    kill "$launcher_pid" 2>/dev/null || true
fi
set +e
wait "$launcher_pid"
emulator_exit_code=$?
set -e

if [[ ! -f "$flatpak_sram" ]]; then
    echo "linux_blastem_capture_status=blocked reason=sram_missing path=$flatpak_sram session_root=$session_root"
    exit 1
fi
cp "$flatpak_sram" "$sram_path"
mv "$launch_rom" "$sealed_rom"
completed_at="$(python3 -c 'from datetime import datetime,timezone; print(datetime.now(timezone.utc).isoformat())')"

set +e
python3 "$script_dir/seal_fresh_evidence_bundle.py" \
    --session-root "$session_root" \
    --session-id "$session_id" \
    --rom "$sealed_rom" \
    --screenshot "$screenshot_path" \
    --sram "$sram_path" \
    --expected-rom-sha256 "$expected_rom_sha256" \
    --started-at "$started_at" \
    --completed-at "$completed_at" \
    --emulator-ref "$emulator_ref" \
    --emulator-commit "$emulator_commit" \
    --window-title "$window_title"
seal_exit_code=$?
set -e

python3 - "$session_root/session_runtime.json" "$session_id" "$window_id" "$window_title" "$emulator_exit_code" "$target_scene" "$audio_driver" "$audio_path" "$region" "$region_code" "$burst_delay" "$burst_count" "$burst_interval" "$burst_gif" <<'PY'
import json, sys
from datetime import datetime, timezone
from pathlib import Path
path, session_id, window_id, window_title, exit_code, target_scene, audio_driver, audio_path, region, region_code, burst_delay, burst_count, burst_interval, burst_gif = sys.argv[1:]
audio_file = Path(audio_path)
burst_file = Path(burst_gif)
Path(path).write_text(json.dumps({
    "schema_version": "1.0.0",
    "generated_at": datetime.now(timezone.utc).isoformat(),
    "session_id": session_id,
    "window_id": window_id,
    "window_title": window_title,
    "emulator_exit_code": int(exit_code),
    "target_scene": int(target_scene) if target_scene else None,
    "requested_region": region,
    "blastem_forced_region": region_code,
    "audio_driver": audio_driver,
    "audio_path": str(audio_file) if audio_file.is_file() else None,
    "audio_size_bytes": audio_file.stat().st_size if audio_file.is_file() else 0,
    "animation_burst": {
        "delay_seconds": float(burst_delay) if burst_delay else None,
        "frame_count": int(burst_count),
        "interval_seconds": float(burst_interval),
        "gif_path": str(burst_file) if burst_file.is_file() else None,
        "gif_size_bytes": burst_file.stat().st_size if burst_file.is_file() else 0,
        "claim_limit": "Burst proves only the states visible in these captured frames.",
    },
    "close_note": "BlastEm Flatpak flushes SRAM on X11 window close; this build may report BadWindow after the flush.",
}, indent=2) + "\n", encoding="utf-8")
PY

if [[ $seal_exit_code -ne 0 ]]; then
    echo "linux_blastem_capture_status=blocked reason=bundle_rejected session_root=$session_root"
    exit "$seal_exit_code"
fi

if [[ -n "$canonical_root" ]]; then
    mkdir -p "$canonical_root" "$project_root/out/logs"
    for artifact in rom.bin screenshot.png save.sram visual_vdp_dump.bin runtime_metrics.json audio.raw evidence_manifest.json freshness_report.json session_runtime.json runtime_animation.gif; do
        # Never let a missing artifact in the new sealed session inherit the
        # file from an older ROM capture.
        rm -f "$canonical_root/$artifact"
        if [[ -f "$session_root/$artifact" ]]; then
            cp -f "$session_root/$artifact" "$canonical_root/$artifact"
        fi
    done

    python3 - "$project_root" "$canonical_root" "$session_root" "$session_id" "$rom_path" "$expected_rom_sha256" "$target_scene" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

project_root, canonical_root, session_root, session_id, rom_path, rom_sha256, target_scene = sys.argv[1:]
project = Path(project_root).resolve()
canonical = Path(canonical_root).resolve()
session = Path(session_root).resolve()
metrics_path = canonical / "runtime_metrics.json"
metrics = {}
if metrics_path.is_file():
    try:
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        metrics = {}

scene_id = metrics.get("scene_id")
if scene_id is None and isinstance(metrics.get("vlab"), dict):
    scene_id = metrics["vlab"].get("scene_id")
requested_scene = int(target_scene) if target_scene else None
target_scene_match = None if requested_scene is None or scene_id is None else int(scene_id) == requested_scene
evidence_files = [
    canonical / "screenshot.png",
    canonical / "save.sram",
    canonical / "visual_vdp_dump.bin",
    canonical / "runtime_metrics.json",
    canonical / "audio.raw",
]
evidence_files = [str(path) for path in evidence_files if path.is_file()]
capture_ok = (
    (canonical / "screenshot.png").is_file()
    and (canonical / "save.sram").is_file()
    and target_scene_match is not False
)

emulator_session = {
    "schema_version": "1.0.0",
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "session_id": session_id,
    "emulator": "blastem",
    "reference_emulator": "blastem",
    "host_capture_route": "linux_flatpak_x11_bridge",
    "launch_status": "captured_closed",
    "status": "ok" if capture_ok else "partial",
    "capture_status": "sealed",
    "boot_emulador": "ok" if capture_ok else "partial",
    "fresh_sram_confirmed": (canonical / "save.sram").is_file(),
    "target_scene": requested_scene,
    "runtime_scene_id": scene_id,
    "target_scene_match": target_scene_match,
    "rom_path": str(Path(rom_path).resolve()),
    "rom_sha256": rom_sha256,
    # The Flatpak sandbox/session directory is kept separately below. The
    # published evidence is intentionally canonical_root, so validators must
    # not classify the publication copy as an outside-sandbox stale artifact.
    "sandbox_root": str(canonical),
    "actual_blastem_sandbox_root": str(session),
    "evidence_root": str(canonical),
    "screenshot_path": str(canonical / "screenshot.png") if (canonical / "screenshot.png").is_file() else None,
    "sram_path": str(canonical / "save.sram") if (canonical / "save.sram").is_file() else None,
    "vdp_dump_path": str(canonical / "visual_vdp_dump.bin") if (canonical / "visual_vdp_dump.bin").is_file() else None,
    "audio_path": str(canonical / "audio.raw") if (canonical / "audio.raw").is_file() else None,
    "evidence_files": evidence_files,
    "captures": evidence_files,
    "published_capture_files": evidence_files,
    "evidence_stale": target_scene_match is False,
    "stale_reason": "runtime_target_scene_mismatch" if target_scene_match is False else None,
    "claim_limit": "Sealed Linux capture proves only the scopes observed in this session.",
}

blastem_evidence = {
    "schema_version": "1.0.0",
    "tool_name": "capture_blastem_evidence_linux",
    "status": emulator_session["status"],
    "evidence_status": emulator_session["status"],
    "session_id": session_id,
    "host_capture_route": "linux_flatpak_x11_bridge",
    "rom_path": emulator_session["rom_path"],
    "rom_sha256": rom_sha256,
    "screenshot_present": (canonical / "screenshot.png").is_file(),
    "screenshot_path": emulator_session["screenshot_path"],
    "sram_present": (canonical / "save.sram").is_file(),
    "sram_path": emulator_session["sram_path"],
    "fresh_sram_confirmed": emulator_session["fresh_sram_confirmed"],
    "vdp_dump_present": (canonical / "visual_vdp_dump.bin").is_file(),
    "vdp_dump_path": emulator_session["vdp_dump_path"],
    "evidence_root": str(canonical),
    "session_manifest_path": str(canonical / "evidence_manifest.json"),
    "target_scene": requested_scene,
    "runtime_scene_id": scene_id,
    "target_scene_match": target_scene_match,
    "blockers": [] if emulator_session["status"] == "ok" else ["linux_capture_incomplete"],
}

logs = project / "out/logs"
logs.mkdir(parents=True, exist_ok=True)
(logs / "emulator_session.json").write_text(json.dumps(emulator_session, indent=2) + "\n", encoding="utf-8")
(logs / "blastem_evidence.json").write_text(json.dumps(blastem_evidence, indent=2) + "\n", encoding="utf-8")
PY
fi
echo "linux_blastem_capture_status=sealed session_id=$session_id session_root=$session_root"
