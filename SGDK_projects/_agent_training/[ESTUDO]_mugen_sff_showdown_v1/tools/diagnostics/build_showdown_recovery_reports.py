from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from math import sqrt
from pathlib import Path
import colorsys
import json

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
VIEW_W = 320
VIEW_H = 224


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def rgb_distance(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def crop_blastem(raw_path: Path, out_path: Path) -> Image.Image:
    raw = Image.open(raw_path).convert("RGB")
    px = raw.load()
    xs: list[int] = []
    ys: list[int] = []
    for y in range(raw.height):
        for x in range(raw.width):
            r, g, b = px[x, y]
            if (r + g + b) > 24:
                xs.append(x)
                ys.append(y)
    if not xs:
        cropped = raw
    else:
        bbox = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
        cropped = raw.crop(bbox)
    normalized = cropped.resize((VIEW_W, VIEW_H), Image.Resampling.NEAREST)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    normalized.save(out_path)
    return normalized


def useful_color_count(img: Image.Image) -> int:
    colors = Counter(img.convert("RGB").getdata())
    return sum(1 for rgb, count in colors.items() if count >= 4 and sum(rgb) > 24)


def avg_saturation(img: Image.Image) -> float:
    sats = []
    for r, g, b in img.convert("RGB").getdata():
        _, s, _ = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
        sats.append(float(s))
    return mean(sats)


def compare_to_source(source: Image.Image, candidate: Image.Image) -> dict:
    src = list(source.convert("RGB").getdata())
    dst = list(candidate.convert("RGB").getdata())
    distances = [rgb_distance(a, b) for a, b in zip(src, dst)]
    over_40 = sum(1 for d in distances if d > 40.0)
    return {
        "mean_rgb_distance": round(mean(distances), 4),
        "pixels_distance_gt_40": int(over_40),
        "percent_distance_gt_40": round((over_40 / len(distances)) * 100.0, 4) if distances else 0.0,
    }


def role_for_viewport_pixel(rgb: tuple[int, int, int], x: int, y: int) -> str:
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255.0, g / 255.0, b / 255.0)
    hue = h * 360.0
    if y < 88 and b >= g >= r:
        return "sky_and_distant_buildings"
    if 80 <= y <= 170 and b >= g and b >= r:
        return "water_and_reflections"
    if 70 <= hue <= 165 and g >= r and g >= b and y >= 40:
        return "live_vegetation"
    if y >= 136 and r >= g and v >= 0.28:
        return "rocks_floor_foreground"
    if s < 0.25 and y < 116:
        return "sky_and_distant_buildings"
    if y >= 136:
        return "rocks_floor_foreground"
    return "water_and_reflections"


def role_means(img: Image.Image, role_masks: dict[str, list[int]]) -> dict[str, list[float]]:
    pixels = list(img.convert("RGB").getdata())
    out: dict[str, list[float]] = {}
    for role, indices in role_masks.items():
        if not indices:
            out[role] = [0.0, 0.0, 0.0]
            continue
        rs = [pixels[i][0] for i in indices]
        gs = [pixels[i][1] for i in indices]
        bs = [pixels[i][2] for i in indices]
        out[role] = [round(mean(rs), 4), round(mean(gs), 4), round(mean(bs), 4)]
    return out


def role_separation(means_by_role: dict[str, list[float]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for left, right in combinations(sorted(means_by_role), 2):
        a = tuple(int(v) for v in means_by_role[left])
        b = tuple(int(v) for v in means_by_role[right])
        out[f"{left}__vs__{right}"] = round(rgb_distance(a, b), 4)
    return out


def build_role_masks(source: Image.Image) -> dict[str, list[int]]:
    masks: dict[str, list[int]] = {
        "sky_and_distant_buildings": [],
        "live_vegetation": [],
        "water_and_reflections": [],
        "rocks_floor_foreground": [],
    }
    pixels = source.convert("RGB").load()
    for y in range(source.height):
        for x in range(source.width):
            role = role_for_viewport_pixel(pixels[x, y], x, y)
            masks[role].append((y * source.width) + x)
    return masks


def image_metrics(name: str, image: Image.Image, source: Image.Image | None = None) -> dict:
    report = {
        "name": name,
        "useful_colors": useful_color_count(image),
        "average_saturation": round(avg_saturation(image), 4),
    }
    if source is not None:
        report["source_comparison"] = compare_to_source(source, image)
    return report


def write_board(
    source: Image.Image,
    export_preview: Image.Image,
    blastem: Image.Image,
    camera_report: dict,
    palette_report: dict,
    budget_report: dict,
    out_path: Path,
) -> None:
    font = ImageFont.load_default()
    panel_w = VIEW_W
    label_h = 18
    report_h = 138
    board = Image.new("RGB", (panel_w * 3, VIEW_H + label_h + report_h), (24, 24, 28))
    draw = ImageDraw.Draw(board)
    panels = [
        ("source viewport", source),
        ("export preview", export_preview),
        ("blastem screenshot", blastem),
    ]
    for i, (label, img) in enumerate(panels):
        x = i * panel_w
        board.paste(img.convert("RGB"), (x, label_h))
        draw.text((x + 6, 4), label, fill=(238, 238, 238), font=font)

    lines = [
        f"camera: {camera_report['status']} | x={camera_report['camera_px']['x']} y={camera_report['camera_px']['y']} | autopan={camera_report['autopan_status']}",
        f"palette: {palette_report['status']} | export dist={palette_report['metrics']['export_preview']['source_comparison']['mean_rgb_distance']} | blastem dist={palette_report['metrics']['blastem_320']['source_comparison']['mean_rgb_distance']}",
        f"budget: {budget_report['status']} | unique={budget_report['tiles']['unique_tiles']} | cache={budget_report['vram']['streaming_cache_capacity_tiles']} tiles | vdp_dump={budget_report['evidence']['vdp_dump_present']}",
        f"route: {budget_report['route_status']} | closeout={budget_report['closeout_recommendation']}",
    ]
    y = VIEW_H + label_h + 8
    for line in lines:
        draw.text((8, y), line, fill=(238, 238, 238), font=font)
        y += 18

    out_path.parent.mkdir(parents=True, exist_ok=True)
    board.save(out_path)


def main() -> int:
    source_path = ROOT / "work" / "reconstructed_viewports" / "frame_0000_mugen_start.png"
    export_path = ROOT / "work" / "diagnostics" / "exported_bin_viewport_default.png"
    blastem_raw_path = ROOT / "sgdk_viewer" / "showdown_viewer" / "out" / "evidence" / "blastem" / "screenshot.png"
    blastem_320_path = ROOT / "work" / "diagnostics" / "blastem_showdown_semantic_palette_320.png"
    comparison_path = ROOT / "work" / "diagnostics" / "showdown_recovery_comparison_v001.png"

    meta = read_json(ROOT / "work" / "sgdk_bins" / "showdown_export_meta.json")
    palette_violations = read_json(ROOT / "analysis" / "palette_violations.json")
    blastem_evidence = read_json(ROOT / "sgdk_viewer" / "showdown_viewer" / "out" / "logs" / "blastem_evidence.json")
    vdp_contract_audit_path = ROOT / "analysis" / "showdown_vdp_contract_audit_v001.json"
    vdp_contract_audit = read_json(vdp_contract_audit_path) if vdp_contract_audit_path.exists() else {}

    source = Image.open(source_path).convert("RGB")
    export_preview = Image.open(export_path).convert("RGB")
    blastem = crop_blastem(blastem_raw_path, blastem_320_path)

    role_masks = build_role_masks(source)
    source_means = role_means(source, role_masks)
    export_means = role_means(export_preview, role_masks)
    blastem_means = role_means(blastem, role_masks)
    source_sep = role_separation(source_means)
    export_sep = role_separation(export_means)
    blastem_sep = role_separation(blastem_means)

    separation_loss = {
        key: {
            "source": source_sep[key],
            "export_preview": export_sep[key],
            "blastem_320": blastem_sep[key],
            "export_loss": round(source_sep[key] - export_sep[key], 4),
            "blastem_loss": round(source_sep[key] - blastem_sep[key], 4),
        }
        for key in source_sep
    }

    generated_at = datetime.now(timezone.utc).isoformat()
    camera = meta["runtime_streaming"]["camera"]
    camera_report = {
        "schema_version": "1.0.0",
        "generated_at": generated_at,
        "status": "dual_focus_fixture_runtime_route_a_multi_plane",
        "camera_px": {
            "x": int(camera["viewer_default_scroll_px"]["x"]),
            "y": int(camera["viewer_default_scroll_px"]["y"]),
        },
        "bounds_px": camera["scroll_bounds_px"],
        "mugen_contract": {
            "zoffset": 215,
            "boundleft": -224,
            "boundright": 224,
            "boundhigh": -240,
            "boundlow": 0,
            "verticalfollow": 0.5,
        },
        "floor_anchor": {
            "screen_y": 215,
            "world_y_at_default_camera": int(camera["viewer_default_scroll_px"]["y"]) + 215,
        },
        "fighter_focus": {
            "p1startx": -70,
            "p2startx": 70,
            "runtime_fixture_world_start": {
                "p1": {
                    "x": int(camera["viewer_default_scroll_px"]["x"]) + (VIEW_W // 2) - 70,
                    "floor_y": int(camera["viewer_default_scroll_px"]["y"]) + 215,
                },
                "p2": {
                    "x": int(camera["viewer_default_scroll_px"]["x"]) + (VIEW_W // 2) + 70,
                    "floor_y": int(camera["viewer_default_scroll_px"]["y"]) + 215,
                },
            },
            "world_focus_x_at_default_camera": int(camera["viewer_default_scroll_px"]["x"]) + (VIEW_W // 2),
        },
        "runtime_camera_model": {
            "model": "dual_focus_midpoint_fixture",
            "camera_x_rule": "camera_x follows clamp(((p1_world_x + p2_world_x) / 2) - viewport_w/2, 0, 448)",
            "camera_y_rule": "camera_y stays at 256 until airborne_delta exceeds 100 px, then applies verticalfollow 1/2 and clamps 0..256",
            "fighter_visibility_rule": "fixture clamps each fighter to stage x and caps horizontal separation to 224 px",
            "floor_anchor_rule": "floor anchor remains zoffset=215 at the default fight camera",
            "super_jump_fixture": {
                "p1_trigger": "BUTTON_A",
                "p2_trigger": "BUTTON_B",
                "arc_ticks": 96,
                "rise_ticks": 48,
                "height_step_px": 6,
            },
            "exploration_input": {
                "status": "disabled_as_camera_logic",
                "p1_horizontal": "LEFT/RIGHT",
                "p2_horizontal": "hold C + LEFT/RIGHT",
            },
        },
        "runtime_parallax_model": {
            "model": "BG_B_BG_A_multi_plane_window_streaming_with_row_multicamera_and_line_scroll",
            "far_band": {
                "screen_y_lt": 72,
                "x_delta": "43/100",
                "y_delta": "285/1000",
            },
            "mid_band": {
                "screen_y_lt": 176,
                "x_delta": "71/100",
                "y_delta": "635/1000",
            },
            "floor_band": {
                "screen_y_gte": 176,
                "x_delta": "1/1",
                "y_delta": "1/1",
            },
            "water_line_scroll": {
                "screen_y_range": [88, 176],
                "status": "implemented_as_line_scroll_offset_gradient",
            },
            "claim_limit": "route_a depth is implemented as two SGDK planes plus row-multicamera and BG_B occlusion culling; foreground priority split remains a lab approximation without fighter sprite overlap capture",
        },
        "autopan_status": "disabled_as_evidence",
        "manual_dpad_status": "fighter_fixture_input_only",
        "parallax_camera_status": {
            "horizontal_depth_contract_documented": True,
            "runtime_multi_plane_status": "BG_B_BG_A_route_a_window_streaming",
            "water_line_scroll_status": "implemented_partial",
            "current_runtime_route": meta["runtime_streaming"]["route_status"],
        },
        "blockers": [
            "camera uses study fixture points, not final fighter entities",
            "foreground priority/sprite-graft behavior is not validated against real fighter sprites",
            "moving-camera parallax capture is still required for full camera QA",
        ],
    }

    palette_report = {
        "schema_version": "1.0.0",
        "generated_at": generated_at,
        "status": "vivid_anchor_palette_repaired_export_pending_art_review",
        "inputs": {
            "source_viewport": rel(source_path),
            "export_preview": rel(export_path),
            "blastem_raw": rel(blastem_raw_path),
            "blastem_320": rel(blastem_320_path),
        },
        "strategy": meta["palettes"]["strategy"],
        "nearest_color_remaps": int(palette_violations["nearest_color_remaps"]),
        "nearest_color_remaps_by_assigned_role": palette_violations["nearest_color_remaps_by_assigned_role"],
        "metrics": {
            "source_viewport": image_metrics("source_viewport", source),
            "export_preview": image_metrics("export_preview", export_preview, source),
            "blastem_320": image_metrics("blastem_320", blastem, source),
        },
        "role_means_rgb": {
            "source_viewport": source_means,
            "export_preview": export_means,
            "blastem_320": blastem_means,
        },
        "role_separation_loss": separation_loss,
        "visual_notes": [
            "manual contextual MD palettes keep separate vivid roles for sky/buildings, vegetation, water/reflections and rocks/floor",
            "BG_B simplification is constrained to the distant plane; floor and near rocks keep sharper palette mapping",
            "BlastEm screenshot aligns with the default floor camera after input cooldown",
            "nearest-color remap count remains measured evidence; this is a controlled fixture, not authorial final art approval",
        ],
    }

    runtime = meta["runtime_streaming"]
    budget_report = {
        "schema_version": "1.0.0",
        "generated_at": generated_at,
        "status": "documented_not_validated_budget",
        "route_status": runtime["route_status"],
        "closeout_recommendation": "route_a_runtime_reworked_emulator_seen_budget_dump_pending",
        "tiles": {
            "raw_tiles": int(meta["raw_tiles"]),
            "unique_tiles": int(meta["unique_tiles"]),
            "global_tile_id_limit_ok": bool(meta["global_tile_id_limit_ok"]),
            "lossy_tile_merges": int(meta["dedup"]["lossy_tile_merges"]),
        },
        "vram": {
            "tile_user_index": int(meta["tile_user_index"]),
            "streaming_cache_capacity_tiles": int(runtime["streaming_cache_capacity_tiles"]),
            "estimated_streaming_cache_vram_bytes": int(runtime["estimated_streaming_cache_vram_bytes"]),
            "max_window_unique_tiles": int(runtime["max_window_unique_tiles"]),
            "max_window_unique_tiles_without_bg_b_cull": int(runtime.get("max_window_unique_tiles_without_bg_b_cull", runtime["max_window_unique_tiles"])),
            "max_bg_b_culled_cells": int(runtime.get("max_bg_b_culled_cells", 0)),
            "tile_data_vram_end_exclusive": 512 + int(runtime["estimated_streaming_cache_vram_bytes"]),
            "first_tilemap_vram": 49152,
            "palette_bytes": 128,
        },
        "streaming": {
            "strategy": runtime["strategy"],
            "plane_count": int(runtime.get("plane_count", 1)),
            "plane_order": runtime.get("plane_order", ["BG_A"]),
            "window_tiles_w": int(runtime["window_tiles_w"]),
            "window_tiles_h": int(runtime["window_tiles_h"]),
            "window_bytes_per_update": int(runtime["window_bytes_per_update"]),
            "max_window_unique_tiles": int(runtime["max_window_unique_tiles"]),
            "transfer_mode": "CPU tile data in small contiguous batches plus CPU tilemap upload on tile-window changes; not proven tear-free",
            "line_scroll_dma_per_frame_bytes": 896,
            "line_scroll_status": "BG_A and BG_B HSCROLL_LINE with 224 line offsets each",
            "bg_b_occlusion_culling": runtime.get("bg_b_occlusion_culling", {"enabled": False}),
        },
        "evidence": {
            "rom_sha256": blastem_evidence["rom_sha256"],
            "screenshot_present": bool(blastem_evidence["screenshot_present"]),
            "sram_present": bool(blastem_evidence["sram_present"]),
            "vdp_dump_present": bool(blastem_evidence["vdp_dump_present"]),
            "readiness_ok": bool(blastem_evidence["readiness_ok"]),
            "ready_probe_source": blastem_evidence["ready_probe_source"],
            "vdp_contract_audit": rel(vdp_contract_audit_path) if vdp_contract_audit else None,
            "vdp_contract_audit_status": vdp_contract_audit.get("status", "missing"),
        },
        "blockers": [
            "no visual_vdp_dump.bin in current evidence",
            "no measured 60fps/frame-time telemetry attached to this attempt",
            "water H-scroll is implemented only as partial line-scroll repair, not full MUGEN layer reconstruction",
        ],
    }

    analysis_dir = ROOT / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    (analysis_dir / "showdown_camera_report_v001.json").write_text(
        json.dumps(camera_report, indent=2), encoding="utf-8"
    )
    (analysis_dir / "showdown_recovery_palette_measurement_v001.json").write_text(
        json.dumps(palette_report, indent=2), encoding="utf-8"
    )
    (analysis_dir / "showdown_budget_report_v001.json").write_text(
        json.dumps(budget_report, indent=2), encoding="utf-8"
    )
    (ROOT / "doc" / "contracts" / "palette_vitality_report_v001.json").write_text(
        json.dumps(palette_report, indent=2), encoding="utf-8"
    )
    write_board(source, export_preview, blastem, camera_report, palette_report, budget_report, comparison_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
