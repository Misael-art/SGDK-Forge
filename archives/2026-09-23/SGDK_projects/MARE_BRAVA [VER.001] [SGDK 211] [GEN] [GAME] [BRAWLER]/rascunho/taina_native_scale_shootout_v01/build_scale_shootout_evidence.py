#!/usr/bin/env python3
"""Build diagnostic-only scale evidence from persisted source/probe files.

This composes inspection panels; it does not author sprite pixels. Every
resizing operation is NEAREST and every output stays under rascunho/.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT / "SGDK_projects" / "MARE_BRAVA [VER.001] [SGDK 211] [GEN] [GAME] [BRAWLER]"
BASE = PROJECT / "rascunho" / "taina_native_scale_shootout_v01"
SOURCE_DIR = PROJECT / "data" / "source_art" / "visual_producer_outputs" / "taina_idle_guard_scale_shootout_v01"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nearest_fit(image: Image.Image, box: tuple[int, int]) -> Image.Image:
    image = image.convert("RGBA")
    image.thumbnail(box, Image.Resampling.NEAREST)
    return image


def paste_center(canvas: Image.Image, image: Image.Image, box: tuple[int, int, int, int]) -> None:
    x, y, w, h = box
    fitted = nearest_fit(image, (w, h))
    px = x + (w - fitted.width) // 2
    py = y + (h - fitted.height) // 2
    canvas.alpha_composite(fitted, (px, py))


def label(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, color=(235, 230, 198)) -> None:
    draw.text((x, y), text, fill=color, font=ImageFont.load_default())


def probe_path(scale: str) -> Path:
    jobs = sorted((PROJECT / "out" / "visual_jobs" / f"taina_idle_guard_{scale}_mechanical_probe_v01").glob("*/basic/*.png"))
    if not jobs:
        raise FileNotFoundError(f"probe_missing:{scale}")
    return jobs[-1]


def main() -> int:
    panel = Image.new("RGBA", (1600, 1120), (13, 18, 28, 255))
    draw = ImageDraw.Draw(panel)
    label(draw, 24, 18, "TAINA — NATIVE SCALE SHOOTOUT v01", (252, 218, 118))
    label(draw, 24, 40, "visual sources are independent; probes are mechanical controls only; no res/", (185, 198, 210))

    scales = [("48x64", "economic_control"), ("56x80", "compromise"), ("64x96", "fidelity_challenger")]
    records = []
    for idx, (scale, role) in enumerate(scales):
        x0 = 24 + idx * 520
        source = SOURCE_DIR / f"taina_idle_guard_{scale}_visual_source_v01.png"
        probe = probe_path(scale)
        draw.rectangle((x0, 72, x0 + 496, 1080), outline=(67, 95, 119), width=2)
        label(draw, x0 + 16, 88, f"{scale} — {role}", (252, 218, 118))
        label(draw, x0 + 16, 112, f"source SHA {sha(source)[:16]}…", (185, 198, 210))
        label(draw, x0 + 16, 130, f"probe SHA {sha(probe)[:16]}…", (185, 198, 210))

        label(draw, x0 + 16, 158, "visual producer output", (185, 198, 210))
        with Image.open(source) as image:
            paste_center(panel, image, (x0 + 16, 178, 224, 360))
        label(draw, x0 + 16, 548, "single pose / identity review", (140, 160, 176))

        label(draw, x0 + 264, 158, "mechanical probe 1x", (185, 198, 210))
        with Image.open(probe) as image:
            paste_center(panel, image, (x0 + 264, 178, 192, 256))
        label(draw, x0 + 264, 448, "technical_candidate", (236, 196, 72))
        label(draw, x0 + 264, 466, "opaque / index0 unused0", (236, 196, 72))

        label(draw, x0 + 16, 584, "8x NEAREST", (185, 198, 210))
        with Image.open(probe) as image:
            nearest = image.convert("RGBA").resize((image.width * 8, image.height * 8), Image.Resampling.NEAREST)
            paste_center(panel, nearest, (x0 + 16, 604, 224, 300))
        label(draw, x0 + 16, 916, "light / dark / chroma: not semantically valid", (236, 196, 72))
        label(draw, x0 + 16, 934, "background is baked into this control", (236, 196, 72))
        label(draw, x0 + 16, 972, "silhouette: withheld — opaque canvas would be a false green", (140, 160, 176))
        label(draw, x0 + 16, 1000, "native lineart, color blocking and palette clean: pending", (140, 160, 176))
        records.append({
            "scale": scale,
            "role": role,
            "visual_source": {"path": str(source.relative_to(PROJECT)), "sha256": sha(source)},
            "mechanical_probe": {"path": str(probe.relative_to(PROJECT)), "sha256": sha(probe)},
            "panel_interpretation": "diagnostic_only",
            "opaque_probe": True,
            "native_authoring_status": "pending_capable_native_pixel_authoring",
        })

    panel_path = BASE / "taina_native_scale_shootout_evidence_panel.png"
    panel.convert("RGB").save(panel_path, "PNG")

    control_panel = Image.new("RGBA", (1600, 620), (13, 18, 28, 255))
    control_draw = ImageDraw.Draw(control_panel)
    label(control_draw, 24, 18, "TAINA — DIRECT CONTROL COMPARISON", (252, 218, 118))
    label(control_draw, 24, 40, "model sheet is identity source; challenger B is historical technical control only", (185, 198, 210))
    model = PROJECT / "data" / "source_art" / "concept" / "taina_pixel_model_sheet" / "taina_reseed_authorial_model_sheet_source_v01.png"
    challenger_b = PROJECT / "rascunho" / "taina_visual_challengers_v03" / "candidates" / "taina_48x64_challenger_b" / "taina_48x64_challenger_b.png"
    control_items = [
        ("model sheet", model, (252, 245, 230)),
        ("challenger B 1x", challenger_b, (20, 24, 32)),
        ("48x64 source", SOURCE_DIR / "taina_idle_guard_48x64_visual_source_v01.png", (252, 245, 230)),
        ("56x80 source", SOURCE_DIR / "taina_idle_guard_56x80_visual_source_v01.png", (252, 245, 230)),
        ("64x96 source", SOURCE_DIR / "taina_idle_guard_64x96_visual_source_v01.png", (252, 245, 230)),
    ]
    for idx, (title, path, bg) in enumerate(control_items):
        x0 = 24 + idx * 312
        control_draw.rectangle((x0, 76, x0 + 288, 590), outline=(67, 95, 119), width=2)
        label(control_draw, x0 + 12, 90, title, (252, 218, 118))
        label(control_draw, x0 + 12, 108, f"SHA {sha(path)[:16]}…", (185, 198, 210))
        with Image.open(path) as image:
            if title == "challenger B 1x":
                image = image.convert("RGBA").resize((image.width * 8, image.height * 8), Image.Resampling.NEAREST)
            paste_center(control_panel, image, (x0 + 12, 132, 264, 420))
        label(control_draw, x0 + 12, 566, "comparison_only / no pixel reuse", (140, 160, 176))
    control_panel_path = BASE / "taina_direct_control_comparison_panel.png"
    control_panel.convert("RGB").save(control_panel_path, "PNG")
    manifest = {
        "schema_version": "1.0.0",
        "status": "diagnostic_evidence_only",
        "panel": str(panel_path.relative_to(PROJECT)),
        "direct_control_panel": str(control_panel_path.relative_to(PROJECT)),
        "resize_policy": "NEAREST_only",
        "source_of_truth": "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png",
        "no_res_touched": True,
        "records": records,
        "notes": [
            "The panel does not create or approve sprite pixels.",
            "Mechanical probes have an opaque background and index0_role=unused0; they are not native sprite candidates.",
            "No silhouette or matte is claimed for the opaque controls.",
        ],
    }
    manifest_path = BASE / "taina_native_scale_shootout_evidence_manifest_v01.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"panel": str(panel_path), "direct_control_panel": str(control_panel_path), "manifest": str(manifest_path)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
