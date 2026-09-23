#!/usr/bin/env python3
"""Build the v10 runtime-review candidate from persisted visual sources.

This is a staging/review producer, not a native-pixel author. ImageMagick is
used only for connected-background removal, crop and the declared Lanczos
translation route; Pillow only seals a binary-alpha, index-0 PNG. The output
is deliberately classified as assisted_native_translation.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image


PROJECT = Path(sys.argv[1]).resolve()
OUT = PROJECT / "out/forward_test_v10_runtime_visual_review"
TMP = OUT / "tmp"
FRAMES = OUT / "frames"
STRIPS = OUT / "strips"
REPORTS = OUT / "reports"

R1 = PROJECT / "data/source_art/r1/r1-01/concept.png"
RUN_ROOT = PROJECT / "out/forward_test_run_keyposes_20260903"
INHALE = PROJECT / "data/staging/visual_production_inhale_jump_20260903/inhale_visual_pose_guide.png"
JUMP = PROJECT / "data/staging/visual_production_inhale_jump_20260903/jump_launch_visual_pose_guide.png"
FIRE = PROJECT / "data/staging/visual_production_ability_fx_20260903/fire_ability_fx_visual_source.png"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def seal_index0(src: Path, dst: Path) -> None:
    """Quantize without inventing marks and reserve palette index 0 for alpha."""
    rgba = Image.open(src).convert("RGBA")
    alpha = rgba.getchannel("A").point(lambda p: 255 if p else 0)
    rgb = Image.new("RGB", rgba.size, (0, 0, 0))
    rgb.paste(rgba.convert("RGB"), mask=alpha)
    quant = rgb.quantize(colors=15, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    out = Image.new("P", rgba.size, 0)
    pixels = list(quant.getdata())
    opaque = list(alpha.getdata())
    qpal = quant.getpalette()[:45]
    raw_palette = [tuple(qpal[i:i + 3]) for i in range(0, len(qpal), 3)]
    snap = lambda value: max(0, min(238, int(value) // 34 * 34))
    canonical = []
    remap = {}
    for index, colour in enumerate(raw_palette):
        snapped = tuple(snap(c) for c in colour)
        if snapped not in canonical:
            canonical.append(snapped)
        remap[index] = 1 + canonical.index(snapped)
    palette = [(0, 0, 0)] + canonical
    palette += [(0, 0, 0)] * (16 - len(palette))
    out.putpalette([channel for colour in palette[:16] for channel in colour])
    out.putdata([remap.get(int(p), 1) if a else 0 for p, a in zip(pixels, opaque)])
    out.info["transparency"] = 0
    out.save(dst, format="PNG", optimize=False, bits=4)


def make_frame(name: str, src: Path, crop: str | None = None, bg: str | None = None,
               max_size: str = "29x29", resize: str | None = None) -> Path:
    tmp = TMP / f"{name}.rgba.png"
    dst = FRAMES / f"{name}.png"
    cmd = ["magick", str(src)]
    if crop:
        cmd += ["-crop", crop, "+repage"]
    if bg:
        cmd += ["-alpha", "off", "-fuzz", "8%", "-fill", "none", "-draw", f"color 0,0 floodfill"]
    else:
        cmd += ["-alpha", "on"]
    cmd += ["-trim", "+repage", "-background", "none", "-gravity", "center",
            "-filter", "Lanczos", "-resize", resize or max_size, "-extent", "32x32", str(tmp)]
    run(cmd)
    seal_index0(tmp, dst)
    return dst


def make_fire(name: str, size: str = "14x14") -> Path:
    tmp = TMP / f"{name}.rgba.png"
    dst = FRAMES / f"{name}.png"
    run(["magick", str(FIRE), "-alpha", "off", "-fuzz", "12%", "-fill", "none",
         "-draw", "color 0,0 floodfill", "-trim", "+repage", "-background", "none",
         "-gravity", "center", "-filter", "Lanczos", "-resize", size,
         "-extent", "16x16", str(tmp)])
    seal_index0(tmp, dst)
    return dst


def append_strip(names: list[str], out: Path, frame_size: int = 32) -> None:
    images = [Image.open(FRAMES / (f if f.endswith(".png") else f + ".png")).convert("RGBA") for f in names]
    canvas = Image.new("RGBA", (frame_size * len(images), frame_size), (0, 0, 0, 0))
    for index, image in enumerate(images):
        canvas.alpha_composite(image, (index * frame_size, 0))
    tmp = TMP / f"{out.stem}.rgba.png"
    canvas.save(tmp, format="PNG")
    seal_index0(tmp, out)


def main() -> int:
    for d in (TMP, FRAMES, STRIPS, REPORTS):
        d.mkdir(parents=True, exist_ok=True)

    # Idle: same R1 3/4 identity, two small timing variants (29px/28px).
    idle0 = make_frame("idle_00", R1, "225x190+25+45", "magenta", "29x29")
    idle1 = make_frame("idle_01", R1, "225x190+25+45", "magenta", "28x29")

    # Run: one shared im_lanczos3 route. The fourth pose is the canonical R1
    # lateral running drawing, processed by the same Lanczos route.
    run_contact = make_frame("run_00_contact", RUN_ROOT / "run_contact_routes/routes/im_lanczos3/raw_rgba.png")
    run_down = make_frame("run_01_down", R1, "180x130+105+410", "magenta", "29x29")
    run_passing = make_frame("run_02_passing", RUN_ROOT / "run_passing_routes/routes/im_lanczos3/raw_rgba.png")
    run_up = make_frame("run_03_up", RUN_ROOT / "run_flight_push_routes/routes/im_lanczos3/raw_rgba.png")

    # Jump/float: source guide plus the R1 canonical inflated-cheek float.
    jump0 = make_frame("jump_00_crouch", JUMP, bg="white", max_size="28x28")
    jump1 = make_frame("jump_01_launch", JUMP, bg="white", max_size="29x29", resize="30x29")
    jump2 = make_frame("jump_02_apex", R1, "175x150+410+392", "magenta", "29x29")
    jump3 = make_frame("jump_03_land", R1, "225x190+25+45", "magenta", "29x29")

    # Inhale: anticipation and release return to the same R1 identity; the
    # middle frames use the persisted open-mouth guide at the same route.
    inhale0 = make_frame("inhale_00_anticipation", R1, "225x190+25+45", "magenta", "29x29")
    inhale1 = make_frame("inhale_01_opening", INHALE, bg="white", max_size="28x28")
    inhale2 = make_frame("inhale_02_hold", INHALE, bg="white", max_size="29x29", resize="30x29")
    inhale3 = make_frame("inhale_03_release", R1, "225x190+25+45", "magenta", "29x29")

    fire0 = make_fire("fire_00")
    fire1 = make_fire("fire_01")
    fire2 = make_fire("fire_02", "15x14")

    action_names = {
        "idle": [idle0.name, idle1.name],
        "run": [run_contact.name, run_down.name, run_passing.name, run_up.name],
        "jump_float": [jump0.name, jump1.name, jump2.name, jump3.name],
        "inhale": [inhale0.name, inhale1.name, inhale2.name, inhale3.name],
    }
    gif_delays = {"idle": 50, "run": 8, "jump_float": 10, "inhale": 13}
    for action, files in action_names.items():
        append_strip([Path(f).stem for f in files], STRIPS / f"kirby_{action}.png")
        run(["magick", "-delay", str(gif_delays[action]), *[str(FRAMES / f) for f in files], "-loop", "0",
             str(REPORTS / f"kirby_{action}.gif")])
        run(["magick", "montage", *[str(FRAMES / f) for f in files], "-tile", f"{len(files)}x1",
             "-geometry", "+6+6", "-background", "#202030", str(REPORTS / f"kirby_{action}_contact_sheet.png")])
        for scale in (1, 2, 3, 8):
            run(["magick", str(STRIPS / f"kirby_{action}.png"), "-scale", f"{scale * 100}%",
                 str(REPORTS / f"kirby_{action}_{scale}x.png")])

    combined_names = [
        "idle_00.png", "idle_01.png",
        "run_00_contact.png", "run_01_down.png", "run_02_passing.png", "run_03_up.png",
        "jump_00_crouch.png", "jump_01_launch.png", "jump_02_apex.png", "jump_03_land.png",
        "jump_02_apex.png", "jump_03_land.png",
        "inhale_00_anticipation.png", "inhale_01_opening.png", "inhale_02_hold.png", "inhale_03_release.png",
    ]
    append_strip([Path(f).stem for f in combined_names], STRIPS / "review_kirby.png")

    append_strip(["fire_00", "fire_01", "fire_02"], STRIPS / "kirby_fire.png", frame_size=16)

    # 320x224 evidence: existing stage artwork is context only; the review
    # sprite is inserted at 1x and is never used as final background artwork.
    bg = REPORTS / "composition_background.png"
    run(["magick", "-size", "320x224", "xc:#284060", str(bg)])
    comp = REPORTS / "composition_320x224_1x.png"
    run(["magick", str(bg), str(FRAMES / "idle_00.png"), "-geometry", "+144+96", "-composite", str(comp)])

    manifest = {
        "version": "v10-runtime-visual-review",
        "status": "runtime_visual_review_candidate",
        "visual_pass": False,
        "final_acceptance": False,
        "production_method": "assisted_native_translation",
        "route_primary": "im_lanczos3",
        "route_secondary": "existing_persisted_source_guides",
        "authority": {"path": "data/source_art/r1/r1-01/concept.png", "sha256": sha(R1)},
        "source_sha256": {str(p.relative_to(PROJECT)): sha(p) for p in (R1, INHALE, JUMP, FIRE)},
        "frames": {a: [{"path": f"frames/{n}", "sha256": sha(FRAMES / n)} for n in ns] for a, ns in action_names.items()},
        "strips": {a: {"path": f"strips/kirby_{a}.png", "sha256": sha(STRIPS / f"kirby_{a}.png")} for a in action_names},
        "runtime_strip": {"path": "strips/review_kirby.png", "sha256": sha(STRIPS / "review_kirby.png"), "frames": 16, "frame_size": "32x32"},
        "ability": {"path": "strips/kirby_fire.png", "sha256": sha(STRIPS / "kirby_fire.png"), "ability": "Fire"},
        "semantic_limits": [
            "inbetweens remain assisted translations from persisted guides",
            "jump camera continuity requires diagnostic review",
            "inhale expansion is a route variation, not native reauthoring",
        ],
    }
    (REPORTS / "v10_visual_review_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
