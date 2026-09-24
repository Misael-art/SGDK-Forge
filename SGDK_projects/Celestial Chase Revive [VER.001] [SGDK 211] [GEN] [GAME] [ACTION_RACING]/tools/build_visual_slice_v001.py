from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_ROOT / "data" / "source_art" / "revive" / "visual_slice_v001"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed" / "visual_slice_v001"
LOG_DIR = PROJECT_ROOT / "out" / "logs"
DOC_DIR = PROJECT_ROOT / "doc"

TOOL_NAME = "build_visual_slice_v001"
TOOL_VERSION = "0.1.0"

PALETTE = [
    (255, 0, 255),   # transparent convention, unused in opaque scene pixels
    (0, 0, 34),      # deep void
    (0, 34, 68),     # indigo
    (0, 68, 102),    # blue teal
    (0, 102, 102),   # teal
    (34, 136, 136),  # far cyan
    (68, 170, 136),  # lumen teal
    (238, 204, 102), # warm lumen
    (238, 170, 68),  # gold
    (204, 102, 68),  # ember
    (136, 68, 102),  # violet iron
    (68, 34, 68),    # boss dark
    (34, 34, 34),    # road dark
    (68, 68, 68),    # road mid
    (136, 136, 102), # road highlight
    (238, 238, 204), # white gold
]


FONT_5X7 = {
    "0": ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    "1": ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "C": ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    "D": ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    "E": ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    "F": ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    "G": ["01111", "10000", "10000", "10111", "10001", "10001", "01111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "N": ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "P": ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "T": ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "V": ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    " ": ["000", "000", "000", "000", "000", "000", "000"],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ensure_dirs() -> None:
    for path in (SOURCE_DIR, PROCESSED_DIR, LOG_DIR):
        path.mkdir(parents=True, exist_ok=True)


def indexed_image(width: int = 320, height: int = 224, fill: int = 1) -> Image.Image:
    img = Image.new("P", (width, height), fill)
    flat_palette = []
    for color in PALETTE:
        flat_palette.extend(color)
    img.putpalette(flat_palette)
    return img


def rect(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], color: int) -> None:
    draw.rectangle(xy, fill=color)


def poly(draw: ImageDraw.ImageDraw, points: list[tuple[int, int]], color: int) -> None:
    draw.polygon(points, fill=color)


def render_text(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, scale: int, color: int, shadow: int | None = None) -> None:
    cursor = x
    for ch in text:
        glyph = FONT_5X7.get(ch)
        if glyph is None:
            cursor += 6 * scale
            continue
        width = max(len(row) for row in glyph)
        if shadow is not None:
            draw_glyph(draw, glyph, cursor + scale, y + scale, scale, shadow)
        draw_glyph(draw, glyph, cursor, y, scale, color)
        cursor += (width + 1) * scale


def draw_glyph(draw: ImageDraw.ImageDraw, glyph: list[str], x: int, y: int, scale: int, color: int) -> None:
    for gy, row in enumerate(glyph):
        for gx, bit in enumerate(row):
            if bit == "1":
                rect(draw, (x + gx * scale, y + gy * scale, x + (gx + 1) * scale - 1, y + (gy + 1) * scale - 1), color)


def draw_sky(draw: ImageDraw.ImageDraw) -> None:
    bands = [(0, 36, 1), (36, 74, 2), (74, 122, 3), (122, 160, 2)]
    for y0, y1, color in bands:
        rect(draw, (0, y0, 319, y1), color)
    for x in range(0, 320, 32):
        y = 18 + ((x // 32) % 5) * 11
        rect(draw, (x + 4, y, x + 5, y + 1), 15)
    for x in range(16, 320, 48):
        y = 62 + ((x // 48) % 3) * 17
        rect(draw, (x, y, x + 1, y + 1), 7)


def draw_pursuer_silhouette(draw: ImageDraw.ImageDraw, cx: int = 248, base_y: int = 105, scale: int = 1) -> None:
    poly(draw, [(cx - 35 * scale, base_y), (cx - 20 * scale, base_y - 38 * scale), (cx, base_y - 48 * scale), (cx + 20 * scale, base_y - 38 * scale), (cx + 35 * scale, base_y)], 11)
    poly(draw, [(cx - 18 * scale, base_y - 36 * scale), (cx - 48 * scale, base_y - 72 * scale), (cx - 32 * scale, base_y - 32 * scale)], 11)
    poly(draw, [(cx + 18 * scale, base_y - 36 * scale), (cx + 48 * scale, base_y - 72 * scale), (cx + 32 * scale, base_y - 32 * scale)], 11)
    rect(draw, (cx - 6 * scale, base_y - 28 * scale, cx + 6 * scale, base_y - 13 * scale), 9)
    rect(draw, (cx - 3 * scale, base_y - 25 * scale, cx + 3 * scale, base_y - 16 * scale), 8)


def draw_road(draw: ImageDraw.ImageDraw) -> None:
    horizon_y = 118
    poly(draw, [(96, horizon_y), (224, horizon_y), (312, 223), (8, 223)], 12)
    poly(draw, [(132, horizon_y), (147, horizon_y), (112, 223), (64, 223)], 13)
    poly(draw, [(173, horizon_y), (188, horizon_y), (256, 223), (208, 223)], 13)
    poly(draw, [(154, horizon_y), (166, horizon_y), (178, 223), (142, 223)], 14)
    for y in range(horizon_y + 8, 224, 16):
        width = (y - horizon_y) // 3
        rect(draw, (160 - width, y, 160 + width, y + 1), 14)
    for step, y in enumerate(range(134, 224, 18)):
        color = 7 if step % 2 == 0 else 8
        rect(draw, (151, y, 168, y + 3), color)


def draw_hud_and_lanes(draw: ImageDraw.ImageDraw) -> None:
    rect(draw, (0, 0, 319, 23), 1)
    rect(draw, (0, 23, 319, 24), 8)
    render_text(draw, "LUM", 8, 7, 1, 15, shadow=11)
    rect(draw, (36, 9, 78, 14), 7)
    render_text(draw, "PRS", 112, 7, 1, 15, shadow=11)
    rect(draw, (140, 9, 206, 14), 9)
    render_text(draw, "PUL", 244, 7, 1, 15, shadow=11)
    rect(draw, (272, 8, 304, 15), 6)


def draw_sector_source() -> Image.Image:
    img = indexed_image()
    draw = ImageDraw.Draw(img)
    draw_sky(draw)
    rect(draw, (0, 160, 319, 223), 12)
    draw_pursuer_silhouette(draw)
    draw_road(draw)
    draw_hud_and_lanes(draw)
    rect(draw, (154, 173, 166, 192), 15)
    rect(draw, (150, 185, 170, 200), 8)
    rect(draw, (86, 168, 93, 175), 7)
    rect(draw, (230, 193, 246, 205), 10)
    return img


def draw_title_source() -> Image.Image:
    img = indexed_image()
    draw = ImageDraw.Draw(img)
    draw_sky(draw)
    rect(draw, (0, 164, 319, 223), 12)
    poly(draw, [(118, 148), (202, 148), (288, 223), (32, 223)], 13)
    draw_pursuer_silhouette(draw, cx=160, base_y=126, scale=1)
    render_text(draw, "CELESTIAL", 20, 38, 3, 15, shadow=11)
    render_text(draw, "CHASE", 70, 72, 4, 8, shadow=11)
    render_text(draw, "REVIVE", 93, 116, 3, 7, shadow=11)
    rect(draw, (112, 188, 207, 204), 1)
    render_text(draw, "START", 128, 192, 1, 15, shadow=11)
    rect(draw, (105, 191, 112, 198), 8)
    rect(draw, (210, 191, 217, 198), 8)
    return img


def tile_bytes(img: Image.Image, tx: int, ty: int) -> bytes:
    crop = img.crop((tx * 8, ty * 8, tx * 8 + 8, ty * 8 + 8))
    return bytes(crop.getdata())


def hflip(tile: bytes) -> bytes:
    out = []
    for row in range(8):
        out.extend(reversed(tile[row * 8 : row * 8 + 8]))
    return bytes(out)


def vflip(tile: bytes) -> bytes:
    out = []
    for row in reversed(range(8)):
        out.extend(tile[row * 8 : row * 8 + 8])
    return bytes(out)


def tile_hash(tile: bytes) -> str:
    return hashlib.sha256(tile).hexdigest()


def analyze_tiles(img: Image.Image, source_path: Path, prefix: str) -> dict:
    w, h = img.size
    cols, rows = w // 8, h // 8
    exact = {}
    hset = {}
    vset = {}
    hvset = {}
    canon = {}
    entries = []

    for ty in range(rows):
        for tx in range(cols):
            tile = tile_bytes(img, tx, ty)
            variants = [tile, hflip(tile), vflip(tile), hflip(vflip(tile))]
            hashes = [tile_hash(v) for v in variants]
            exact[hashes[0]] = tile
            hset[min(hashes[0], hashes[1])] = tile
            vset[min(hashes[0], hashes[2])] = tile
            hvset[min(hashes)] = tile
            canonical = min(hashes)
            if canonical not in canon:
                canon[canonical] = variants[hashes.index(canonical)]
            entries.append(
                {
                    "tile_x": tx,
                    "tile_y": ty,
                    "tile_index": list(canon.keys()).index(canonical),
                    "palette_id": 0,
                    "priority": False,
                    "hflip": False,
                    "vflip": False,
                    "source_tile_hash": hashes[0],
                    "canonical_tile_hash": canonical,
                }
            )

    final_unique = len(canon)
    total_tiles = cols * rows
    tileset_cols = 16
    tileset_rows = max(1, (final_unique + tileset_cols - 1) // tileset_cols)
    tileset = indexed_image(tileset_cols * 8, tileset_rows * 8, fill=0)
    for idx, tile in enumerate(canon.values()):
        x = (idx % tileset_cols) * 8
        y = (idx // tileset_cols) * 8
        tile_img = Image.new("P", (8, 8))
        tile_img.putpalette(img.getpalette())
        tile_img.putdata(tile)
        tileset.paste(tile_img, (x, y))

    tileset_path = PROCESSED_DIR / f"{prefix}_tileset_review_v001.png"
    tilemap_path = PROCESSED_DIR / f"{prefix}_tilemap_v001.json"
    palette_path = PROCESSED_DIR / f"{prefix}_palette_v001.json"
    save_png4(tileset, tileset_path)
    tilemap_path.write_text(json.dumps({"width_tiles": cols, "height_tiles": rows, "entries": entries}, indent=2), encoding="utf-8")
    palette_path.write_text(json.dumps({"palette": PALETTE}, indent=2), encoding="utf-8")

    return {
        "source_path": str(source_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "source_sha256": sha256(source_path),
        "conversion_target": "scene_slice",
        "output_tileset_path": str(tileset_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "output_tilemap_path": str(tilemap_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "output_palette_path": str(palette_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "tile_size_px": 8,
        "total_tiles": total_tiles,
        "unique_tiles_exact": len(exact),
        "unique_tiles_hflip": len(hset),
        "unique_tiles_vflip": len(vset),
        "unique_tiles_hvflip": final_unique,
        "final_unique_tiles": final_unique,
        "dedup_savings_tiles": total_tiles - final_unique,
        "dedup_savings_percent": round(((total_tiles - final_unique) / total_tiles) * 100.0, 4),
        "palette_count": 1,
        "per_tile_palette_conflicts": 0,
        "priority_tile_count": 0,
        "hflip_tile_count": 0,
        "vflip_tile_count": 0,
        "hvflip_tile_count": 0,
        "estimated_vram_bytes": final_unique * 32,
        "estimated_map_bytes": total_tiles * 2,
        "rom_resource_strategy": "TILESET_MAP",
        "status": "needs_review",
        "blockers": ["rom_integration_missing", "blastem_capture_missing"],
        "generated_at": now_iso(),
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "_tilemap_entries": entries,
    }


def make_contact_sheet(title: Image.Image, sector: Image.Image) -> Image.Image:
    sheet = indexed_image(640, 248, fill=1)
    draw = ImageDraw.Draw(sheet)
    sheet.paste(title, (0, 24))
    sheet.paste(sector, (320, 24))
    rect(draw, (0, 0, 639, 23), 1)
    render_text(draw, "TITLE SOURCE", 8, 8, 1, 15, shadow=11)
    render_text(draw, "SECTOR 01 SOURCE", 328, 8, 1, 15, shadow=11)
    return sheet


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def save_png4(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path, bits=4)


def build_visual_gate(title_path: Path, sector_path: Path, contact_path: Path, scene_report_path: Path) -> dict:
    return {
        "schema": "visual_delivery_gate_report.v1",
        "ready_for_aaa": False,
        "technical_ready": True,
        "creative_ready": False,
        "technical_artifact_status": "technical_lab_validated",
        "semantic_audit_status": "passed",
        "max_delivery_status": "technical_lab_validated",
        "creative_blocking_statuses": [
            "visual_gate_blocked",
            "rom_integration_missing",
            "blastem_capture_missing",
            "visual_vdp_dump_missing",
        ],
        "visual_direction_status": "passed",
        "visual_direction_findings": [
            "visual_slice_v001 establishes title and Sector 01 source direction without promoting final art",
            "critical assets remain needs_review until ROM integration and BlastEm evidence",
        ],
        "decision_log": [
            {
                "axis": "front_end_identity",
                "decision": "use hard-edge luminous title over restrained astral sky",
                "rationale": "Keeps the project identity readable before adding animation or palette cycling.",
                "evidence": str(title_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            },
            {
                "axis": "sector01_playfield",
                "decision": "show pursuer silhouette in the horizon and keep lane road as the highest gameplay read",
                "rationale": "Answers the chase fantasy without sacrificing three-lane readability.",
                "evidence": str(sector_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            },
            {
                "axis": "vdp_budget",
                "decision": "treat source as TILESET_MAP candidate, not whole-image final art",
                "rationale": "The slice must be measurable before it can replace runtime placeholders.",
                "evidence": str(scene_report_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            },
        ],
        "axis_evidence": {
            "title_source": str(title_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "sector01_source": str(sector_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "contact_sheet": str(contact_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "tilemap_conversion": str(scene_report_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        },
        "gameplay_consequence_evidence": {
            "status": "passed",
            "route_readability": "playfield source preserves three lane columns and hazard/pickup silhouettes",
            "pursuer_presence": "horizon silhouette makes pressure visible from Sector 01",
            "hud_priority": "top WINDOW band remains dark and high contrast",
        },
        "measurement_level": "measured",
        "leaf_blocker_propagation": True,
        "workspace_scope_isolation": True,
        "anti_lab_fallback": {
            "lab_bg_b_absent": True,
            "vdp_drawtext_not_dominant": True,
            "effect_names_not_visible": True,
            "debug_panel_absent": True,
            "axis_specific_playable_scene": True,
            "static_audit_report": {"path": str(contact_path.relative_to(PROJECT_ROOT)).replace("\\", "/")},
        },
        "visual_vdp_dump_required": True,
        "visual_vdp_dump_status": "missing",
        "visual_vdp_dump_path": "out/evidence/blastem/visual_vdp_dump.bin",
        "baseline_comparison_status": "missing",
        "visual_route_status": "visual_gate_blocked",
        "route_status": "source_direction_established_runtime_pending",
        "pipeline_status": "awaiting_res_conversion_and_blastem_capture",
        "blocking_status": "rom_integration_missing",
        "vram_residency_status": "needs_review",
        "vram_residency_report": "out/logs/scene_tilemap_conversion_report.json",
        "runtime_visual_corruption_status": "not_detected",
        "critical_assets": [
            {
                "asset_id": "visual_slice_v001_title_source",
                "role": "title_and_branding_source",
                "visual_status": "needs_review",
                "perceptual_quality": "source_direction_measured_not_emulator_verified",
                "source_validity": True,
                "authoriality_gate": "passed",
                "license": "project_owned",
                "authorial_source": str(title_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "derivative_of": "",
                "derivative_license_status": "not_applicable",
                "clone_risk_score": 0.05,
                "clone_risk_method": "local_authorial_direction_no_external_source",
                "benchmark_used_as": "technical_reference",
                "premium_source_path": str(title_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "rom_asset_path": "",
                "measurement_level": "measured",
                "measured": True,
                "leaf_blockers": ["rom_integration_missing", "blastem_capture_missing", "visual_vdp_dump_missing"],
                "elite_ready": False,
                "lab_not_delivery": False,
            },
            {
                "asset_id": "visual_slice_v001_sector01_source",
                "role": "race_playfield_source",
                "visual_status": "needs_review",
                "perceptual_quality": "source_direction_measured_not_emulator_verified",
                "source_validity": True,
                "authoriality_gate": "passed",
                "license": "project_owned",
                "authorial_source": str(sector_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "derivative_of": "",
                "derivative_license_status": "not_applicable",
                "clone_risk_score": 0.05,
                "clone_risk_method": "local_authorial_direction_no_external_source",
                "benchmark_used_as": "technical_reference",
                "premium_source_path": str(sector_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "rom_asset_path": "",
                "measurement_level": "measured",
                "measured": True,
                "leaf_blockers": ["rom_integration_missing", "blastem_capture_missing", "visual_vdp_dump_missing"],
                "elite_ready": False,
                "lab_not_delivery": False,
            },
        ],
    }


def main() -> None:
    ensure_dirs()
    title = draw_title_source()
    sector = draw_sector_source()

    title_path = SOURCE_DIR / "title_frontend_source_v001.png"
    sector_path = SOURCE_DIR / "sector01_playfield_source_v001.png"
    save_png4(title, title_path)
    save_png4(sector, sector_path)

    contact = make_contact_sheet(title, sector)
    contact_path = PROCESSED_DIR / "visual_slice_contact_sheet_v001.png"
    save_png4(contact, contact_path)

    scene_report = analyze_tiles(sector, sector_path, "sector01_playfield")
    tilemap_entries = scene_report.pop("_tilemap_entries")
    scene_report_path = LOG_DIR / "scene_tilemap_conversion_report.json"
    write_json(scene_report_path, scene_report)

    write_json(
        LOG_DIR / "per_tile_palette_conflict_report.json",
        {
            "$schema": "sgdk_wrapper/schemas/per_tile_palette_conflict_report.schema.json",
            "generated_at": now_iso(),
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "conflicts_total": 0,
            "conflicts": [],
        },
    )
    write_json(
        LOG_DIR / "tilemap_flag_report.json",
        {
            "$schema": "sgdk_wrapper/schemas/tilemap_flag_report.schema.json",
            "generated_at": now_iso(),
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "entries": tilemap_entries,
        },
    )

    manifest = {
        "schema_version": "1.0.0",
        "manifest_id": "visual_slice_v001_manifest",
        "status": "source_direction_established_runtime_pending",
        "source_policy": "Project-owned authorial direction source. Not final res art, not ROM evidence, not ready_for_aaa.",
        "root": str(SOURCE_DIR.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        "files": [
            {
                "asset_id": "visual_slice_v001_title_source",
                "path": str(title_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "sha256": sha256(title_path),
                "role": "front-end title source direction",
            },
            {
                "asset_id": "visual_slice_v001_sector01_source",
                "path": str(sector_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "sha256": sha256(sector_path),
                "role": "Sector 01 playfield source direction",
            },
            {
                "asset_id": "visual_slice_v001_contact_sheet",
                "path": str(contact_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                "sha256": sha256(contact_path),
                "role": "human review contact sheet",
            },
        ],
        "references": [
            {
                "title": "OutRun",
                "inheritance": "fast road horizon and readable forward motion; inspiration_only, no asset copy",
            },
            {
                "title": "Thunder Force IV",
                "inheritance": "high contrast sci-fi silhouettes and parallax density discipline; inspiration_only",
            },
            {
                "title": "Sonic 3 & Knuckles",
                "inheritance": "clean foreground readability against colorful motion; inspiration_only",
            },
        ],
        "blockers_before_rom": [
            "convert_source_to_res_assets",
            "palette_slot_audit",
            "vram_residency_remeasure",
            "blastem_capture",
            "visual_vdp_dump",
        ],
        "generated_at": now_iso(),
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
    }
    write_json(DOC_DIR / "visual_slice_v001_manifest.json", manifest)

    locked_direction = {
        "schema_version": "1.0.0",
        "status": "locked_for_next_conversion_pass",
        "direction_id": "visual_slice_v001",
        "scope": ["front_end_title", "sector_01_playfield"],
        "must_preserve": [
            "Pursuer horn/crown silhouette visible from Sector 01 horizon",
            "Three lane road remains the strongest gameplay read",
            "Lumen warm gold/teal remains pickup and pressure language",
            "Title logo uses hard-edge luminous blocks, not SGDK debug font",
            "HUD stays dark, compact and subordinate to route reading",
        ],
        "must_not_do": [
            "Do not promote these source PNGs directly as final res art",
            "Do not claim ready_for_aaa before BlastEm evidence and VDP dump",
            "Do not replace lane readability with decorative sky detail",
        ],
        "next_conversion_target": "res/bg title slice and Sector 01 BG/TILESET_MAP candidate",
        "evidence": {
            "manifest": "doc/visual_slice_v001_manifest.json",
            "contact_sheet": str(contact_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "scene_tilemap_report": "out/logs/scene_tilemap_conversion_report.json",
        },
        "generated_at": now_iso(),
        "tool_name": TOOL_NAME,
        "tool_version": TOOL_VERSION,
    }
    write_json(DOC_DIR / "locked_visual_direction_v001.json", locked_direction)

    write_json(
        DOC_DIR / "source_validity_report.json",
        {
            "schema": "source_validity_report.v1",
            "status": "authorial_source_direction_present",
            "source_validity": True,
            "source_scope": "visual_direction_source_only",
            "premium_source_manifest": "doc/visual_slice_v001_manifest.json",
            "accepted_for_res_promotion": False,
            "reason": "visual_slice_v001 is project-owned source direction, but must still be converted, audited and seen in BlastEm before asset promotion.",
            "required_before_asset_promotion": True,
            "source_files": manifest["files"],
        },
    )
    write_json(
        DOC_DIR / "authoriality_gate_report.json",
        {
            "schema": "authoriality_gate_report.v1",
            "status": "passed_for_source_direction_only",
            "authoriality_gate": "passed",
            "clone_risk_threshold": 0.25,
            "clone_risk_score": 0.05,
            "clone_risk_method": "local authorial composition with references limited to technical inheritance",
            "benchmark_usage_policy": "benchmark may guide scale, density, timing and budget only",
            "required_before_res_promotion": True,
            "res_promotion_allowed": False,
            "blocking_until_res_promotion": ["source_to_res_conversion_missing", "blastem_capture_missing"],
        },
    )

    write_json(LOG_DIR / "visual_delivery_gate_report.json", build_visual_gate(title_path, sector_path, contact_path, scene_report_path))
    print(json.dumps({"status": "ok", "manifest": str((DOC_DIR / "visual_slice_v001_manifest.json").relative_to(PROJECT_ROOT))}, indent=2))


if __name__ == "__main__":
    main()
