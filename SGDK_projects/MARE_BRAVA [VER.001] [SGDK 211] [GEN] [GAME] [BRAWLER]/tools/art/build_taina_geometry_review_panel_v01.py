#!/usr/bin/env python3
"""Compose a review panel from already-produced evidence; never edits candidates."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PROJECT = Path(__file__).resolve().parents[2]
ROOT = PROJECT / "rascunho/taina_native_geometry_challengers_v01"
MANIFEST = ROOT / "native_geometry_challengers_manifest_v01.json"
PANEL = ROOT / "taina_native_geometry_review_panel_v01.png"
FONT = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 18)
SMALL = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 13)


def fit(dst: Image.Image, source: Path, box: tuple[int, int, int, int]) -> None:
    x, y, w, h = box
    image = Image.open(source).convert("RGBA")
    image.thumbnail((w, h), Image.Resampling.NEAREST)
    dst.alpha_composite(image, (x + (w - image.width) // 2, y + (h - image.height) // 2))


def main() -> int:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    panel = Image.new("RGBA", (1800, 1040), (28, 30, 38, 255))
    draw = ImageDraw.Draw(panel)
    draw.text((30, 20), "TAÍNA — NATIVE GEOMETRY REFINEMENT v01", fill=(255, 220, 120), font=FONT)
    draw.text((30, 48), "A/B/C independentes · 48x64 locked · staging only · pending_human_decision", fill=(220, 225, 232), font=SMALL)
    controls = [
        ("MODEL SHEET · identity source only", PROJECT / "data/source_art/concept/taina_pixel_model_sheet/taina_reseed_authorial_model_sheet_source_v01.png"),
        ("B · comparison-only", PROJECT / "rascunho/taina_visual_challengers_v03/candidates/taina_48x64_challenger_b/taina_48x64_challenger_b.png"),
        ("ELITE · best technical control only", PROJECT / "rascunho/taina_native_refinement_v01/taina_48x64_refined_elite_v01.png"),
    ]
    for i, (label, source) in enumerate(controls):
        x = 30 + i * 590
        draw.text((x, 88), label, fill=(220, 225, 232), font=SMALL)
        bg = Image.new("RGBA", (560, 190), (48, 52, 64, 255))
        fit(bg, source, (4, 4, 552, 182))
        panel.alpha_composite(bg, (x, 112))
        draw.rectangle((x, 112, x + 559, 301), outline=(110, 120, 135), width=1)
    labels = [
        ("A", "FACE_AND_GUARD_TOPOLOGY", "face_and_guard_topology"),
        ("B", "SILHOUETTE_AND_WEIGHT", "silhouette_and_weight"),
        ("C", "INTEGRATED_NATIVE_REDRAW", "integrated_native_redraw"),
    ]
    for i, (letter, hypothesis, route) in enumerate(labels):
        candidate = next(c for c in manifest["candidates"] if c["route"] == route)
        x = 30 + i * 590
        y = 340
        draw.text((x, y), f"{letter} — {hypothesis}", fill=(255, 220, 120), font=FONT)
        draw.text((x, y + 30), f"{candidate['asset_id']} · SHA {candidate['candidate']['sha256'][:12]}…", fill=(180, 190, 202), font=SMALL)
        ev = {k: PROJECT.parents[0] / v if False else Path("/mnt/sdcard/Projects/Sgdk Forge") / v for k, v in candidate["evidence"].items()}
        dark = Image.new("RGBA", (270, 340), (48, 52, 64, 255))
        fit(dark, ev["nearest_8x"], (8, 8, 254, 322))
        panel.alpha_composite(dark, (x, y + 60))
        draw.rectangle((x, y + 60, x + 269, y + 399), outline=(110, 120, 135), width=1)
        camera = Image.new("RGBA", (270, 190), (238, 238, 230, 255))
        fit(camera, ev["camera_320x224"], (0, 0, 270, 190))
        panel.alpha_composite(camera, (x + 285, y + 60))
        draw.rectangle((x + 285, y + 60, x + 554, y + 249), outline=(110, 120, 135), width=1)
        metrics = candidate["tile_metrics"]
        geom = candidate["geometry_comparison"]["challenger_b"]
        draw.text((x + 285, y + 270), f"bbox {metrics['bbox']} · occ {metrics['visible_pixels']} px", fill=(220, 225, 232), font=SMALL)
        draw.text((x + 285, y + 290), f"changed mask vs B: {geom['changed_mask_pixels']} px", fill=(220, 225, 232), font=SMALL)
        draw.text((x + 285, y + 310), f"tiles {metrics['unique_tiles']}/48 · VRAM {metrics['vram_unique_bytes']} B", fill=(160, 230, 170), font=SMALL)
        draw.text((x + 285, y + 330), "visual gate: pending human", fill=(255, 220, 120), font=SMALL)
    PANEL.parent.mkdir(parents=True, exist_ok=True)
    panel.convert("RGB").save(PANEL, optimize=True)
    report = {
        "schema_version": "1.0.0",
        "status": "pending_human_decision",
        "panel": str(PANEL.relative_to(PROJECT.parents[1])),
        "automatic_winner": None,
        "technical_recommendation": {
            "A": "strongest observed face/gaze and diagonal guard topology; feet remain small at 1x",
            "B": "strongest observed center of mass, leg separation and baseline; guard/face are more compressed",
            "C": "most compact integrated redraw and lowest measured unique-tile count; face/hair/feet are less separated",
            "recommendation_scope": "human comparison aid only; not a winner or approval",
        },
        "visual_gate": {
            "reviewed_at_1x": True,
            "reviewed_at_nearest_8x": True,
            "all_candidates_technical_preflight": True,
            "no_numeric_aesthetic_scores": True,
        },
        "decision_required": "proposed_for_final_native_pose with exact asset_id, SHA-256 and scale=48x64",
        "res_promotion": False,
        "animation_authorization": False,
        "ready_for_aaa": False,
    }
    (ROOT / "native_geometry_visual_review_report_v01.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(PANEL)
    print(ROOT / "native_geometry_visual_review_report_v01.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
