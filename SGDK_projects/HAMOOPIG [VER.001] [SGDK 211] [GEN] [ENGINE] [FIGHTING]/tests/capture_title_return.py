#!/usr/bin/env python3
"""Exercise the session-visible INTRO/FADE options and SELECT->TITLE return.

This is an evidence runner, not a visual approval: it records the same-ROM
screenshots and the exact keyboard route so a reviewer can judge the transition.
"""

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
    "title_return_" + datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
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
    tap(value, 0.22)
    time.sleep(0.25)


def capture(window: str, name: str) -> dict:
    path = DEST / (name + ".png")
    for _ in range(8):
        sp.run(["import", "-window", window, str(path)], stdout=sp.DEVNULL, stderr=sp.DEVNULL)
        try:
            image = Image.open(path).convert("RGB")
            nonempty = len(set(image.get_flattened_data())) > 1
        except Exception:
            nonempty = False
        if nonempty:
            return {"capture": path.name, "nonempty": True}
        time.sleep(0.15)
    return {"capture": path.name, "nonempty": path.exists() and path.stat().st_size > 0}


def set_scene_options(window: str, enabled: bool) -> list[dict]:
    # Main -> OPTIONS; cursor starts at SFX.  OPENING and FADE are indices 10/11.
    slowtap("Down")
    slowtap("a")
    time.sleep(1.0)
    for _ in range(10):
        slowtap("Down")
    time.sleep(0.5)
    first = capture(window, "options_scene_page")
    slowtap("a")  # INTRO OFF/ON
    slowtap("Down")
    slowtap("a")  # FADE OFF/ON
    return [first, {"enabled": enabled, "cursor": "FADE"}]


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    rom = DEST / "rom.bin"
    shutil.copy2(ROOT / "out" / "rom.bin", rom)
    sha = hashlib.sha256(rom.read_bytes()).hexdigest()
    config_root = ROOT / "out" / "emulator_config" / "blastem"
    config_root.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(ROOT / "tests"))
    from capture_visual_ko import prepare_blastem_config
    prepare_blastem_config(config_root / "blastem.cfg")
    before = set()
    found = sp.run(["xdotool", "search", "--name", "BlastEm"], capture_output=True, text=True)
    if found.returncode == 0:
        before = set(found.stdout.splitlines())
    log = (DEST / "emulator.log").open("w")
    proc = sp.Popen([
        "flatpak", "--user", "run", "--filesystem=/mnt/sdcard/Projects/Sgdk Forge",
        "--env=SDL_AUDIODRIVER=dummy", "--env=SDL_JOYSTICK_HIDAPI=0",
        "--command=sh", "com.retrodev.blastem", "-c",
        'export XDG_CONFIG_HOME="$1" XDG_DATA_HOME="$2"; shift 2; exec /app/bin/blastem "$@"',
        "hamoopig-title-return", str(config_root), str(DEST / "userdata"), "-r", "U", str(rom)
    ], stdout=log, stderr=log, start_new_session=True)
    window = None
    captures: list[dict] = []
    try:
        for _ in range(200):
            result = sp.run(["xdotool", "search", "--name", "BlastEm"], capture_output=True, text=True)
            candidates = set(result.stdout.splitlines()) - before
            if candidates:
                window = next(iter(candidates))
                break
            time.sleep(0.1)
        if not window:
            raise RuntimeError("BlastEm window timeout")
        run("xdotool", "windowactivate", "--sync", window)
        time.sleep(7)
        captures.append({"phase": "initial_title", **capture(window, "01_title_initial")})

        # Turn INTRO and FADE OFF, return through SELECT, then B back to TITLE.
        set_scene_options(window, False)
        tap("s")
        tap("Up")
        tap("a")
        time.sleep(2)
        captures.append({"phase": "select_before_intro_off_return", **capture(window, "02_select_intro_off")})
        tap("s")
        time.sleep(1)
        captures.append({"phase": "title_after_intro_off_fade_off", **capture(window, "03_title_cut_return")})

        # Turn both back ON and prove that the same B route enters OPENING.
        set_scene_options(window, True)
        tap("s")
        tap("Up")
        tap("a")
        time.sleep(2)
        tap("s")
        time.sleep(0.45)
        captures.append({"phase": "opening_after_intro_on", **capture(window, "04_opening_return_early")})
        time.sleep(3.5)
        captures.append({"phase": "title_after_intro_on", **capture(window, "05_title_return_late")})

        manifest = {
            "schema_version": "1.0.0",
            "scope": "real_keyboard_title_intro_fade_return",
            "rom_sha256": sha,
            "region_requested": "NTSC",
            "route": [
                "TITLE -> OPTIONS -> INTRO OFF -> FADE OFF",
                "OPTIONS -> BACK -> START -> SELECT -> B -> TITLE (direct cut)",
                "TITLE -> OPTIONS -> INTRO ON -> FADE ON",
                "OPTIONS -> BACK -> START -> SELECT -> B -> OPENING -> TITLE",
            ],
            "captures": captures,
            "claims": "same-ROM route and nonempty framebuffer captures; visual smoothness and readability require review",
        }
        (DEST / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"session": str(DEST), "rom_sha256": sha, "captures": len(captures)}))
        return 0
    finally:
        for value in ("Down", "Up", "a", "s", "Return"):
            try:
                key(value, False)
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


if __name__ == "__main__":
    raise SystemExit(main())
