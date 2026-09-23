#!/usr/bin/env python3
"""Stress the real ROM through repeated BlastEm soft-reset scene boots."""
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

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "out/emulator_evidence" / (
    "scene_reset_cycles_" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
)


def run(*args):
    return sp.check_output(args, stderr=sp.DEVNULL, text=True).strip()


def key(value, down):
    run("xdotool", "keydown" if down else "keyup", value)


def shot(window, name):
    path = DEST / f"{name}.png"
    result = sp.run(["import", "-window", window, str(path)], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    return result.returncode == 0 and path.is_file() and path.stat().st_size > 0


def main():
    cycles = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    if cycles < 1 or cycles > 1000:
        raise SystemExit("cycles must be between 1 and 1000")
    DEST.mkdir(parents=True, exist_ok=True)
    rom = DEST / "rom.bin"
    shutil.copy2(ROOT / "out/rom.bin", rom)
    rom_sha = hashlib.sha256(rom.read_bytes()).hexdigest()
    config = ROOT / "out/emulator_config"
    config_dir = config / "blastem"
    config_dir.mkdir(parents=True, exist_ok=True)
    # Reuse the proven, packaged-default profile with P2 extension.
    sys.path.insert(0, str(ROOT / "tests"))
    from capture_visual_ko import prepare_blastem_config
    prepare_blastem_config(config_dir / "blastem.cfg")
    userdata = DEST / "userdata"
    log = (DEST / "emulator.log").open("w")
    before = set()
    found = sp.run(["xdotool", "search", "--name", "BlastEm"], capture_output=True, text=True)
    if found.returncode == 0:
        before = set(found.stdout.splitlines())
    process = sp.Popen([
        "flatpak", "--user", "run", "--filesystem=/mnt/sdcard/Projects/Sgdk Forge",
        "--env=SDL_AUDIODRIVER=dummy", "--env=SDL_JOYSTICK_HIDAPI=0",
        "--command=sh", "com.retrodev.blastem", "-c",
        'export XDG_CONFIG_HOME="$1" XDG_DATA_HOME="$2"; shift 2; exec /app/bin/blastem "$@"',
        "hamoopig-reset", str(config_dir), str(userdata), "-r", "U", str(rom),
    ], stdout=log, stderr=log, start_new_session=True)
    window = None
    records = []
    try:
        for _ in range(200):
            result = sp.run(["xdotool", "search", "--name", "BlastEm"], capture_output=True, text=True)
            candidates = set(result.stdout.splitlines()) - before
            if candidates:
                window = next(iter(candidates))
                break
            time.sleep(.1)
        if not window:
            raise RuntimeError("BlastEm window timeout")
        run("xdotool", "windowactivate", "--sync", window)
        time.sleep(2)
        shots = []
        for cycle in range(1, cycles + 1):
            key("tab", True); key("tab", False)
            time.sleep(.35)
            alive = process.poll() is None
            search = sp.run(["xdotool", "search", "--name", "BlastEm"], capture_output=True, text=True)
            window_present = window in set(search.stdout.splitlines())
            if cycle in (1, cycles // 2, cycles):
                name = f"cycle_{cycle:03d}"
                shots.append({"cycle": cycle, "capture": name + ".png", "nonempty": shot(window, name)})
            records.append({"cycle": cycle, "process_alive": alive, "window_present": window_present})
            if not alive or not window_present:
                raise RuntimeError(f"reset cycle {cycle} lost BlastEm process/window")
        manifest = {
            "schema_version": "1.0.0",
            "scope": "real_keyboard_blastem_soft_reset_scene_stress",
            "rom_sha256": rom_sha,
            "cycles_requested": cycles,
            "cycles_completed": len(records),
            "all_process_alive": all(r["process_alive"] for r in records),
            "all_windows_present": all(r["window_present"] for r in records),
            "captures": shots,
            "round_reset_cycles": "not_exercised_by_this_route",
            "claim_limit": "scene boot/reset stability only; no visual, audio or round-reset approval",
        }
        (DEST / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
        print(json.dumps({"session": str(DEST), "cycles_completed": len(records), "rom_sha256": rom_sha}), flush=True)
    finally:
        for value in ("tab",):
            try: key(value, False)
            except Exception: pass
        try: os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError: pass
        try: process.wait(timeout=5)
        except sp.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
        log.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
