#!/usr/bin/env python3
"""Measure the Scene 1 panel manifest for BENCHMARK_VISUAL_LAB_V3.

This builder stays intentionally below asset promotion:
- no writes to res/
- no resources.res edits
- no runtime artifacts

It reads the planning contract, composes the working BG planes from the
curated vertical forest pack, measures panel candidates, and emits only
machine-readable reports for the next gate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from PIL import Image

from build_bvl_showcase_assets import build_opaque_palette, ensure_dir
from build_bvl_v2_scene1_assets import compose_backgrounds, count_unique_tiles, panel_origins


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_PROJECT_ROOT = WORKSPACE_ROOT / "SGDK_projects" / "BENCHMARK_VISUAL_LAB_V3"
DEFAULT_PLAN_PATH = DEFAULT_PROJECT_ROOT / "doc" / "scene1-panel-manifest-plan.json"
DEFAULT_FOREST_ROOT = WORKSPACE_ROOT / "SGDK_projects" / "data" / "Forest parallax - Parallax (Forest) vertical"
DEFAULT_CASE_ROOT = DEFAULT_PROJECT_ROOT / "doc" / "source_cases" / "scene_multiplane_showcase_v3"
DEFAULT_REPORTS_ROOT = DEFAULT_CASE_ROOT / "reports"
DEFAULT_MANIFEST_OUT = DEFAULT_REPORTS_ROOT / "scene1_panel_manifest_measured.json"
DEFAULT_LOG_OUT = DEFAULT_PROJECT_ROOT / "out" / "logs" / "scene1_builder_gate_report.json"
MAX_BG_COLORS = 16

BAND_SOURCE_RANGES = {
    "sky": (0, 224),
    "transition": (144, 368),
    "forest_ground": (288, 512),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def count_palette_entries(image: Image.Image, colors: int = MAX_BG_COLORS) -> dict[str, int | bool]:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    opaque_mask = alpha.point(lambda value: 255 if value > 0 else 0)
    visible_rgb = Image.new("RGBA", rgba.size, (0, 0, 0, 255))
    visible_rgb.paste(rgba, mask=opaque_mask)
    indexed_visible = visible_rgb.convert("RGB").quantize(
        palette=build_opaque_palette(rgba, colors),
        dither=Image.Dither.NONE,
    )

    alpha_pixels = list(alpha.tobytes())
    visible_pixels = list(indexed_visible.tobytes())
    visible_indices = {pixel for alpha_value, pixel in zip(alpha_pixels, visible_pixels) if alpha_value > 0}
    transparent_pixels = sum(1 for alpha_value in alpha_pixels if alpha_value == 0)
    transparent_required = transparent_pixels > 0
    palette_slots_required = len(visible_indices) + (1 if transparent_required else 0)

    return {
        "visible_colors_used": len(visible_indices),
        "transparent_required": transparent_required,
        "transparent_pixels": transparent_pixels,
        "palette_slots_required": min(colors, palette_slots_required),
    }


def validate_source_extent(plane_name: str, image: Image.Image, expected_size: list[int]) -> dict[str, Any]:
    actual_size = [image.width, image.height]
    return {
        "plane": plane_name,
        "expected_px": expected_size,
        "actual_px": actual_size,
        "matches_plan": actual_size == expected_size,
    }


def measure_panel(
    panel: Image.Image,
    origin_px: list[int],
    panel_size_px: list[int],
    planned_max_tiles: int,
    plane_name: str,
    band_name: str,
    panel_index: int,
) -> dict[str, Any]:
    palette_stats = count_palette_entries(panel)
    unique_tiles_measured = count_unique_tiles(panel)
    return {
        "index": panel_index,
        "plane": plane_name,
        "band": band_name,
        "origin_px": origin_px,
        "size_px": panel_size_px,
        "unique_tiles_measured": unique_tiles_measured,
        "tile_budget_max": planned_max_tiles,
        "tile_budget_ok": unique_tiles_measured <= planned_max_tiles,
        "palette_stats": palette_stats,
    }


def measure_candidate(
    candidate: dict[str, Any],
    plane_images: dict[str, Image.Image],
) -> dict[str, Any]:
    plane_name = candidate["plane"]
    band_name = candidate["band"]
    image = plane_images[plane_name]
    panel_width, panel_height = candidate["panel_size_px"]
    stride_px = candidate["stride_px"]
    y0, y1 = BAND_SOURCE_RANGES[band_name]

    if (y1 - y0) != panel_height:
        raise ValueError(
            f"Band '{band_name}' height {y1 - y0} does not match panel height {panel_height} for {plane_name}."
        )

    origins = panel_origins(image.width, panel_width, stride_px)
    band_crop = image.crop((0, y0, image.width, y1)).convert("RGBA")

    measured_panels: list[dict[str, Any]] = []
    planned_max_tiles = int(candidate["unique_tiles"]["planned_max"])
    for panel_index, origin_x in enumerate(origins):
        panel = band_crop.crop((origin_x, 0, origin_x + panel_width, panel_height)).convert("RGBA")
        measured_panels.append(
            measure_panel(
                panel=panel,
                origin_px=[origin_x, y0],
                panel_size_px=[panel_width, panel_height],
                planned_max_tiles=planned_max_tiles,
                plane_name=plane_name,
                band_name=band_name,
                panel_index=panel_index,
            )
        )

    unique_tiles = [entry["unique_tiles_measured"] for entry in measured_panels]
    palette_slots = [entry["palette_stats"]["palette_slots_required"] for entry in measured_panels]
    return {
        "plane": plane_name,
        "role": candidate["role"],
        "band": band_name,
        "source_y_px": [y0, y1],
        "panel_size_px": candidate["panel_size_px"],
        "stride_px": stride_px,
        "overlap_px": panel_width - stride_px,
        "panel_count_measured": len(measured_panels),
        "resident_slots_target": candidate["resident_slots_target"],
        "palette_plan": candidate["palette_plan"],
        "rom_vram_target": candidate["rom_vram_target"],
        "seams_fallback": candidate["seams_fallback"],
        "tile_budget_max": planned_max_tiles,
        "max_unique_tiles_measured": max(unique_tiles),
        "min_unique_tiles_measured": min(unique_tiles),
        "all_panels_within_tile_budget": all(entry["tile_budget_ok"] for entry in measured_panels),
        "max_palette_slots_required": max(palette_slots),
        "panels": measured_panels,
    }


def build_measured_manifest(
    plan: dict[str, Any],
    bg_b: Image.Image,
    bg_a: Image.Image,
    forest_root: Path,
) -> dict[str, Any]:
    manifest_plan = plan["manifest_plan"]
    plane_images = {
        "BG_B": bg_b,
        "BG_A": bg_a,
    }

    source_extent_checks = [
        validate_source_extent("BG_B", bg_b, manifest_plan["source_extent"]["bg_b_board_px"]),
        validate_source_extent("BG_A", bg_a, manifest_plan["source_extent"]["bg_a_board_px"]),
    ]
    if not all(check["matches_plan"] for check in source_extent_checks):
        raise ValueError("Measured source extent does not match the planned board size.")

    candidates = [measure_candidate(candidate, plane_images) for candidate in manifest_plan["panel_candidates"]]
    tile_budget_ok = all(candidate["all_panels_within_tile_budget"] for candidate in candidates)
    max_palette_slots = max(candidate["max_palette_slots_required"] for candidate in candidates)

    return {
        "schema_version": "1.0.0",
        "project": plan["project"],
        "scene_id": plan["scene_id"],
        "status": "measured_manifest_only",
        "promotion_state": "documentado",
        "source_pack": {
            "forest_root": str(forest_root),
        },
        "builder_gate": {
            "decision": plan["builder_gate"]["decision"],
            "builder_script": "tools/image-tools/build_bvl_v3_scene1_manifest_gate.py",
            "asset_promotion_performed": False,
            "runtime_touched": False,
            "resources_res_touched": False,
        },
        "runtime_status": plan["runtime_status"],
        "visible_window": manifest_plan["visible_window"],
        "motion_path": manifest_plan["motion_path"],
        "source_extent_checks": source_extent_checks,
        "band_source_ranges": {
            band: list(bounds) for band, bounds in BAND_SOURCE_RANGES.items()
        },
        "panel_candidates_measured": candidates,
        "overlay_and_reserved_palettes": manifest_plan["overlay_and_reserved_palettes"],
        "budget_summary": {
            "tile_budget_ok": tile_budget_ok,
            "max_palette_slots_required": max_palette_slots,
            "candidate_count": len(candidates),
        },
    }


def build_gate_report(manifest: dict[str, Any], plan_path: Path, manifest_path: Path) -> dict[str, Any]:
    budget_summary = manifest["budget_summary"]
    return {
        "scene_id": manifest["scene_id"],
        "status": "ok",
        "gate_kind": "builder_manifest_measurement",
        "plan_path": str(plan_path),
        "measured_manifest_path": str(manifest_path),
        "asset_promotion_performed": False,
        "runtime_touched": False,
        "resources_res_touched": False,
        "tile_budget_ok": budget_summary["tile_budget_ok"],
        "max_palette_slots_required": budget_summary["max_palette_slots_required"],
        "candidate_count": budget_summary["candidate_count"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Measure Scene 1 panel candidates for BENCHMARK_VISUAL_LAB_V3 without asset promotion."
    )
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT_ROOT)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN_PATH)
    parser.add_argument("--forest-root", type=Path, default=DEFAULT_FOREST_ROOT)
    parser.add_argument("--manifest-out", type=Path, default=DEFAULT_MANIFEST_OUT)
    parser.add_argument("--log-out", type=Path, default=DEFAULT_LOG_OUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = args.project_root.resolve()
    plan_path = args.plan.resolve()
    forest_root = args.forest_root.resolve()
    manifest_out = args.manifest_out.resolve()
    log_out = args.log_out.resolve()

    if project_root != DEFAULT_PROJECT_ROOT.resolve():
        ensure_dir(project_root)
    ensure_dir(manifest_out.parent)
    ensure_dir(log_out.parent)

    plan = load_json(plan_path)
    bg_b, bg_a = compose_backgrounds(forest_root)
    measured_manifest = build_measured_manifest(plan, bg_b, bg_a, forest_root)
    gate_report = build_gate_report(measured_manifest, plan_path, manifest_out)

    manifest_out.write_text(json.dumps(measured_manifest, indent=2), encoding="utf-8")
    log_out.write_text(json.dumps(gate_report, indent=2), encoding="utf-8")
    print(f"OK measured Scene 1 manifest written to {manifest_out}")
    print(f"OK builder gate report written to {log_out}")


if __name__ == "__main__":
    main()
