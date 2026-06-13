#!/usr/bin/env python3
"""Probe panel-layout variants for BENCHMARK_VISUAL_LAB_V3 Scene 1.

This tool exists to compare candidate panel widths/strides before any asset
promotion. It rewrites only temporary plans/reports inside out/logs.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
WORKSPACE_ROOT = SCRIPT_DIR.parent.parent
PROJECT_ROOT = WORKSPACE_ROOT / "SGDK_projects" / "BENCHMARK_VISUAL_LAB_V3"
PLAN_PATH = PROJECT_ROOT / "doc" / "scene1-panel-manifest-plan.json"
OUT_DIR = PROJECT_ROOT / "out" / "logs" / "variant_probe"
BUILDER = WORKSPACE_ROOT / "tools" / "image-tools" / "build_bvl_v3_scene1_manifest_gate.py"


VARIANTS: list[dict[str, Any]] = [
    {
        "name": "baseline_reference",
        "changes": [],
    },
    {
        "name": "bgb_sky_144_112",
        "changes": [
            {"plane": "BG_B", "band": "sky", "panel_size_px": [144, 224], "stride_px": 112},
        ],
    },
    {
        "name": "bgb_sky_144_96",
        "changes": [
            {"plane": "BG_B", "band": "sky", "panel_size_px": [144, 224], "stride_px": 96},
        ],
    },
    {
        "name": "bgb_sky_136_104",
        "changes": [
            {"plane": "BG_B", "band": "sky", "panel_size_px": [136, 224], "stride_px": 104},
        ],
    },
    {
        "name": "bgb_sky_128_96",
        "changes": [
            {"plane": "BG_B", "band": "sky", "panel_size_px": [128, 224], "stride_px": 96},
        ],
    },
    {
        "name": "bgb_sky_128_80",
        "changes": [
            {"plane": "BG_B", "band": "sky", "panel_size_px": [128, 224], "stride_px": 80},
        ],
    },
    {
        "name": "bga_fg_112_112",
        "changes": [
            {"plane": "BG_A", "band": "forest_ground", "panel_size_px": [112, 224], "stride_px": 112},
        ],
    },
    {
        "name": "bga_fg_112_96",
        "changes": [
            {"plane": "BG_A", "band": "forest_ground", "panel_size_px": [112, 224], "stride_px": 96},
        ],
    },
    {
        "name": "bga_fg_120_96",
        "changes": [
            {"plane": "BG_A", "band": "forest_ground", "panel_size_px": [120, 224], "stride_px": 96},
        ],
    },
    {
        "name": "combo_a",
        "changes": [
            {"plane": "BG_B", "band": "sky", "panel_size_px": [144, 224], "stride_px": 112},
            {"plane": "BG_A", "band": "forest_ground", "panel_size_px": [112, 224], "stride_px": 96},
        ],
    },
    {
        "name": "combo_b",
        "changes": [
            {"plane": "BG_B", "band": "sky", "panel_size_px": [128, 224], "stride_px": 96},
            {"plane": "BG_A", "band": "forest_ground", "panel_size_px": [112, 224], "stride_px": 96},
        ],
    },
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def apply_changes(plan: dict[str, Any], changes: list[dict[str, Any]]) -> dict[str, Any]:
    updated = json.loads(json.dumps(plan))
    for change in changes:
        for candidate in updated["manifest_plan"]["panel_candidates"]:
            if candidate["plane"] == change["plane"] and candidate["band"] == change["band"]:
                candidate["panel_size_px"] = change["panel_size_px"]
                candidate["stride_px"] = change["stride_px"]
    return updated


def candidate_summary(manifest: dict[str, Any], plane: str, band: str) -> dict[str, Any] | None:
    for candidate in manifest["panel_candidates_measured"]:
        if candidate["plane"] == plane and candidate["band"] == band:
            return {
                "panel_size_px": candidate["panel_size_px"],
                "stride_px": candidate["stride_px"],
                "panel_count_measured": candidate["panel_count_measured"],
                "max_unique_tiles_measured": candidate["max_unique_tiles_measured"],
                "max_palette_slots_required": candidate["max_palette_slots_required"],
                "all_panels_within_tile_budget": candidate["all_panels_within_tile_budget"],
            }
    return None


def run_variant(base_plan: dict[str, Any], variant: dict[str, Any]) -> dict[str, Any]:
    variant_name = variant["name"]
    variant_dir = OUT_DIR / variant_name
    plan_path = variant_dir / "plan.json"
    manifest_path = variant_dir / "manifest.json"
    report_path = variant_dir / "report.json"

    write_json(plan_path, apply_changes(base_plan, variant["changes"]))
    subprocess.run(
        [
            "python",
            str(BUILDER),
            "--plan",
            str(plan_path),
            "--manifest-out",
            str(manifest_path),
            "--log-out",
            str(report_path),
        ],
        check=True,
        cwd=WORKSPACE_ROOT,
    )

    manifest = load_json(manifest_path)
    report = load_json(report_path)
    return {
        "variant": variant_name,
        "tile_budget_ok": report["tile_budget_ok"],
        "max_palette_slots_required": report["max_palette_slots_required"],
        "bg_b_sky": candidate_summary(manifest, "BG_B", "sky"),
        "bg_a_forest_ground": candidate_summary(manifest, "BG_A", "forest_ground"),
        "report_path": str(report_path),
        "manifest_path": str(manifest_path),
    }


def main() -> None:
    base_plan = load_json(PLAN_PATH)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summaries = [run_variant(base_plan, variant) for variant in VARIANTS]
    summary_path = OUT_DIR / "summary.json"
    summary_txt = OUT_DIR / "summary.txt"
    write_json(summary_path, summaries)
    lines = [json.dumps(item, ensure_ascii=True) for item in summaries]
    summary_txt.write_text("\n".join(lines), encoding="utf-8")
    print(summary_txt)


if __name__ == "__main__":
    main()
