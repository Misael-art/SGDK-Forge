#!/usr/bin/env python3
"""Capture the real Sound Test route and its isolated BlastEm audio stream."""

from __future__ import annotations

import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess as sp
import sys
import time

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "out" / "emulator_evidence" / (
    "sound_test_" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
)


def run(*args: str) -> str:
    return sp.check_output(args, stderr=sp.DEVNULL, text=True).strip()


def key(value: str, down: bool) -> None:
    run("xdotool", "keydown" if down else "keyup", value)


def tap(value: str, hold: float = 0.12) -> None:
    key(value, True)
    time.sleep(hold)
    key(value, False)
    time.sleep(0.30)


def slowtap(value: str) -> None:
    """Give the title FSM a full edge interval before the next command."""
    tap(value, 0.22)
    time.sleep(0.25)


def capture(window: str, name: str) -> str:
    path = DEST / (name + ".png")
    for _ in range(8):
        sp.run(["import", "-window", window, str(path)], stdout=sp.DEVNULL,
               stderr=sp.DEVNULL, check=False)
        try:
            image = Image.open(path).convert("RGB")
            if len(set(image.get_flattened_data())) > 1:
                return path.name
        except Exception:
            pass
        time.sleep(0.15)
    return path.name


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    rom = DEST / "rom.bin"
    shutil.copy2(ROOT / "out" / "rom.bin", rom)
    rom_sha = hashlib.sha256(rom.read_bytes()).hexdigest()
    config_root = ROOT / "out" / "emulator_config" / "blastem"
    config_root.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT / "tests"))
    from capture_visual_ko import prepare_blastem_config
    config_file = config_root / "blastem.cfg"
    prepare_blastem_config(config_file)

    before = set()
    found = sp.run(["xdotool", "search", "--name", "BlastEm"],
                   capture_output=True, text=True, check=False)
    if found.returncode == 0:
        before = set(found.stdout.splitlines())

    sink = "hamoopig_sound_test_" + str(os.getpid())
    existing_audio_inputs = {
        item["index"] for item in json.loads(run("pactl", "-f", "json", "list", "sink-inputs"))
    }
    module_id = run("pactl", "load-module", "module-null-sink",
                    "sink_name=" + sink, "rate=48000", "channels=2")
    log = (DEST / "emulator.log").open("w", encoding="utf-8")
    proc = sp.Popen([
        "flatpak", "--user", "run", "--filesystem=/mnt/sdcard/Projects/Sgdk Forge",
        "--env=SDL_AUDIODRIVER=pulseaudio", "--env=PULSE_SINK=" + sink,
        "--env=SDL_JOYSTICK_HIDAPI=0", "--command=sh", "com.retrodev.blastem", "-c",
        'export XDG_CONFIG_HOME="$1" XDG_DATA_HOME="$2"; shift 2; exec /app/bin/blastem "$@"',
        "hamoopig-sound-test", str(config_root), str(DEST / "userdata"),
        "-r", "U", str(rom)
    ], stdout=log, stderr=log, start_new_session=True)
    audio_capture = None
    window = None
    captures = []
    try:
        for _ in range(200):
            result = sp.run(["xdotool", "search", "--name", "BlastEm"],
                            capture_output=True, text=True, check=False)
            candidates = set(result.stdout.splitlines()) - before
            if candidates:
                window = next(iter(candidates))
                break
            time.sleep(0.1)
        if not window:
            raise RuntimeError("BlastEm window timeout")
        run("xdotool", "windowactivate", "--sync", window)
        time.sleep(7)
        # The title page ignores input while its fade-in is settling.  The
        # former fast pair occasionally leaked A into START and captured the
        # fighter selector instead of Sound Test.  Keep the route explicit:
        # MAIN -> OPTION -> OPTIONS -> SOUND TEST.
        slowtap("Down")
        slowtap("a")
        time.sleep(1)
        slowtap("Down")
        slowtap("Down")
        slowtap("a")
        time.sleep(1)
        captures.append({"state": "sound_test_idle", "capture": capture(window, "01_sound_test_idle")})

        owned = []
        for _ in range(60):
            owned = [item for item in json.loads(run("pactl", "-f", "json", "list", "sink-inputs"))
                     if item["index"] not in existing_audio_inputs and
                     (item.get("properties", {}).get("application.process.binary", "").lower() in
                      {"blastem", "blastem.bin"} or
                      "blastem" in item.get("properties", {}).get("application.name", "").lower() or
                      "blastem" in item.get("properties", {}).get("node.name", "").lower())]
            if len(owned) == 1:
                break
            time.sleep(0.2)
        if len(owned) != 1:
            raise RuntimeError("Sound Test emulator stream was not isolated")
        run("pactl", "move-sink-input", str(owned[0]["index"]), sink)
        sinks = [item for item in json.loads(run("pactl", "-f", "json", "list", "sinks"))
                 if item["name"] == sink]
        sink_ids = {item["index"] for item in sinks}
        for _ in range(20):
            owned_after_move = [item for item in json.loads(run("pactl", "-f", "json", "list", "sink-inputs"))
                                if item["index"] == owned[0]["index"] and item["sink"] in sink_ids]
            if owned_after_move:
                owned = owned_after_move
                break
            time.sleep(0.2)
        if not owned or owned[0]["sink"] not in sink_ids:
            raise RuntimeError("BlastEm stream did not move to the private monitor")
        (DEST / "pulse_sink_inputs.json").write_text(json.dumps(owned, indent=2) + "\n")
        (DEST / "pulse_sinks.json").write_text(json.dumps(sinks, indent=2) + "\n")
        audio_log = (DEST / "audio.log").open("w", encoding="utf-8")
        audio_capture = sp.Popen([
            "ffmpeg", "-y", "-f", "pulse", "-i", sink + ".monitor",
            "-c:a", "pcm_s16le", str(DEST / "emulator_audio.wav")
        ], stdout=audio_log, stderr=audio_log)

        run("xdotool", "windowactivate", "--sync", window)
        tap("a")
        time.sleep(6.5)
        captures.append({"state": "playing_first_phrase", "capture": capture(window, "02_sound_test_playing")})
        time.sleep(8.0)
        captures.append({"state": "playing_after_loop", "capture": capture(window, "03_sound_test_loop")})
        run("xdotool", "windowactivate", "--sync", window)
        tap("a")
        time.sleep(1.0)
        captures.append({"state": "sound_test_stopped", "capture": capture(window, "04_sound_test_stopped")})

        (DEST / "manifest.json").write_text(json.dumps({
            "schema_version": "1.0.0",
            "scope": "real_keyboard_sound_test_and_audio_capture",
            "rom_sha256": rom_sha,
            "region_requested": "NTSC",
            "route": ["TITLE", "OPTIONS", "SOUND TEST", "A PLAY", "loop observed", "A STOP"],
            "track": "Forge Crystal",
            "captures": captures,
            "audio": "isolated_monitor_captured_not_auditioned",
            "audio_wav": "emulator_audio.wav",
            "claims": "same-ROM Sound Test route, loop-duration capture and isolated audio signal; human listening review remains required"
        }, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps({"session": str(DEST), "rom_sha256": rom_sha, "captures": len(captures)}))
        return 0
    finally:
        for value in ("Down", "a", "s", "Return"):
            try:
                key(value, False)
            except Exception:
                pass
        if audio_capture:
            audio_capture.send_signal(signal.SIGINT)
            try:
                audio_capture.wait(timeout=10)
            except sp.TimeoutExpired:
                audio_capture.kill()
        try:
            if window:
                key("esc", True)
                time.sleep(0.12)
                key("esc", False)
                time.sleep(0.8)
        except Exception:
            pass
        try:
            os.killpg(proc.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            proc.wait(timeout=5)
        except sp.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()
        log.close()
        sp.run(["pactl", "unload-module", module_id], stdout=sp.DEVNULL,
               stderr=sp.DEVNULL, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
