from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow not installed. Run: pip install Pillow", file=sys.stderr)
    raise


TOOL_NAME = "analyze_tilemap_dedup_flags"
TOOL_VERSION = "0.1"
TILE_SIZE = 8


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _tile_bytes(img: Image.Image, tile_x: int, tile_y: int) -> bytes:
    base_x = tile_x * TILE_SIZE
    base_y = tile_y * TILE_SIZE
    px = img.load()
    out = bytearray(TILE_SIZE * TILE_SIZE)
    cursor = 0
    for y in range(TILE_SIZE):
        for x in range(TILE_SIZE):
            out[cursor] = int(px[base_x + x, base_y + y])
            cursor += 1
    return bytes(out)


def _flip_h(tile: bytes) -> bytes:
    out = bytearray(len(tile))
    for y in range(TILE_SIZE):
        row = tile[y * TILE_SIZE : (y + 1) * TILE_SIZE]
        out[y * TILE_SIZE : (y + 1) * TILE_SIZE] = row[::-1]
    return bytes(out)


def _flip_v(tile: bytes) -> bytes:
    out = bytearray(len(tile))
    for y in range(TILE_SIZE):
        src_y = TILE_SIZE - 1 - y
        out[y * TILE_SIZE : (y + 1) * TILE_SIZE] = tile[src_y * TILE_SIZE : (src_y + 1) * TILE_SIZE]
    return bytes(out)


def _flip_hv(tile: bytes) -> bytes:
    return _flip_h(_flip_v(tile))


@dataclass(frozen=True)
class TileHashes:
    normal: str
    hflip: str
    vflip: str
    hvflip: str

    def canonical(self) -> str:
        return min(self.normal, self.hflip, self.vflip, self.hvflip)


def _hashes_for_tile(tile: bytes) -> TileHashes:
    h = _sha256_hex(tile)
    hh = _sha256_hex(_flip_h(tile))
    hv = _sha256_hex(_flip_v(tile))
    hhv = _sha256_hex(_flip_hv(tile))
    return TileHashes(normal=h, hflip=hh, vflip=hv, hvflip=hhv)


def _unique_count_allowing_hflip(hashes: list[TileHashes]) -> int:
    return len({min(h.normal, h.hflip) for h in hashes})


def _unique_count_allowing_vflip(hashes: list[TileHashes]) -> int:
    return len({min(h.normal, h.vflip) for h in hashes})


def _unique_count_allowing_hvflip(hashes: list[TileHashes]) -> int:
    return len({h.canonical() for h in hashes})


def _tile_index_set(tile: bytes) -> set[int]:
    return set(tile)


def _analyze_palette_conflicts(
    tile: bytes,
    tile_x: int,
    tile_y: int,
    transparency_expected: bool,
) -> list[dict]:
    used = _tile_index_set(tile)
    non_zero = {idx for idx in used if idx != 0}
    conflicts: list[dict] = []

    if not transparency_expected and 0 in used:
        conflicts.append(
            {
                "rule_id": "index0_contamination",
                "severity": "error",
                "tile_x": tile_x,
                "tile_y": tile_y,
                "details": "Tile uses palette index 0 while transparency_expected=false"
            }
        )

    if any(idx >= 16 for idx in non_zero):
        conflicts.append(
            {
                "rule_id": "palette_index_out_of_domain",
                "severity": "error",
                "tile_x": tile_x,
                "tile_y": tile_y,
                "details": "Tile uses palette indices >=16 (not sub-palette safe)"
            }
        )

    if len(non_zero) > 15:
        conflicts.append(
            {
                "rule_id": "tile_exceeds_subpalette_color_budget",
                "severity": "error",
                "tile_x": tile_x,
                "tile_y": tile_y,
                "details": "Tile uses more than 15 visible colors (excluding index 0)"
            }
        )

    return conflicts


def analyze_indexed_png(
    source_path: Path,
    source_sha256: str,
    conversion_target: str,
    output_tileset_path: str,
    output_tilemap_path: str,
    output_palette_path: str,
    rom_resource_strategy: str,
    transparency_expected: bool,
    generated_at: str,
) -> tuple[dict, dict, dict]:
    with Image.open(source_path) as img:
        if img.mode != "P":
            raise ValueError("Input PNG must be indexed (mode 'P')")
        w, h = img.size
        if w % TILE_SIZE != 0 or h % TILE_SIZE != 0:
            raise ValueError("Input PNG dimensions must be multiples of 8")

        tile_cols = w // TILE_SIZE
        tile_rows = h // TILE_SIZE
        total_tiles = tile_cols * tile_rows

        all_hashes: list[TileHashes] = []
        palette_conflicts: list[dict] = []
        flag_entries: list[dict] = []
        max_palette_index = -1

        for ty in range(tile_rows):
            for tx in range(tile_cols):
                tile = _tile_bytes(img, tx, ty)
                max_palette_index = max(max_palette_index, max(tile))
                hashes = _hashes_for_tile(tile)
                all_hashes.append(hashes)

                canonical_hash = hashes.canonical()
                hflip = canonical_hash == hashes.hflip
                vflip = canonical_hash == hashes.vflip
                hvflip = canonical_hash == hashes.hvflip
                flag_entries.append(
                    {
                        "tile_x": tx,
                        "tile_y": ty,
                        "tile_index": ty * tile_cols + tx,
                        "palette_id": 0,
                        "priority": False,
                        "hflip": hflip or hvflip,
                        "vflip": vflip or hvflip,
                        "source_tile_hash": hashes.normal,
                        "canonical_tile_hash": canonical_hash
                    }
                )

                palette_conflicts.extend(_analyze_palette_conflicts(tile, tx, ty, transparency_expected))

        unique_tiles_exact = len({h.normal for h in all_hashes})
        unique_tiles_hflip = _unique_count_allowing_hflip(all_hashes)
        unique_tiles_vflip = _unique_count_allowing_vflip(all_hashes)
        unique_tiles_hvflip = _unique_count_allowing_hvflip(all_hashes)
        final_unique_tiles = unique_tiles_hvflip

        dedup_savings_tiles = total_tiles - final_unique_tiles
        dedup_savings_percent = (dedup_savings_tiles / total_tiles * 100.0) if total_tiles else 0.0

        hflip_tile_count = sum(1 for e in flag_entries if e["hflip"] and not e["vflip"])
        vflip_tile_count = sum(1 for e in flag_entries if e["vflip"] and not e["hflip"])
        hvflip_tile_count = sum(1 for e in flag_entries if e["hflip"] and e["vflip"])
        priority_tile_count = 0

        palette_count = int(math.ceil((max_palette_index + 1) / 16.0)) if max_palette_index >= 0 else 0

        estimated_vram_bytes = final_unique_tiles * 32
        estimated_map_bytes = total_tiles * 2

        blockers: list[str] = []
        status = "ok"

        conflicts_total = len(palette_conflicts)
        if conflicts_total > 0:
            blockers.append("PER_TILE_PALETTE_CONFLICTS_DETECTED")
            status = "blocked"

        unique_ratio = (final_unique_tiles / total_tiles) if total_tiles else 0.0
        if rom_resource_strategy == "IMAGE" and total_tiles >= (320 // 8) * (224 // 8) and unique_ratio >= 0.80:
            blockers.append("WHOLE_IMAGE_UNIQUE_RATIO_HIGH")
            if status == "ok":
                status = "needs_review"

        scene_report = {
            "source_path": str(source_path),
            "source_sha256": source_sha256,
            "conversion_target": conversion_target,
            "output_tileset_path": output_tileset_path,
            "output_tilemap_path": output_tilemap_path,
            "output_palette_path": output_palette_path,
            "tile_size_px": TILE_SIZE,
            "total_tiles": total_tiles,
            "unique_tiles_exact": unique_tiles_exact,
            "unique_tiles_hflip": unique_tiles_hflip,
            "unique_tiles_vflip": unique_tiles_vflip,
            "unique_tiles_hvflip": unique_tiles_hvflip,
            "final_unique_tiles": final_unique_tiles,
            "dedup_savings_tiles": dedup_savings_tiles,
            "dedup_savings_percent": dedup_savings_percent,
            "palette_count": palette_count,
            "per_tile_palette_conflicts": conflicts_total,
            "priority_tile_count": priority_tile_count,
            "hflip_tile_count": hflip_tile_count,
            "vflip_tile_count": vflip_tile_count,
            "hvflip_tile_count": hvflip_tile_count,
            "estimated_vram_bytes": estimated_vram_bytes,
            "estimated_map_bytes": estimated_map_bytes,
            "rom_resource_strategy": rom_resource_strategy,
            "status": status,
            "blockers": blockers,
            "generated_at": generated_at,
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION
        }

        flag_report = {
            "generated_at": generated_at,
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "entries": flag_entries
        }

        conflict_report = {
            "generated_at": generated_at,
            "tool_name": TOOL_NAME,
            "tool_version": TOOL_VERSION,
            "conflicts_total": conflicts_total,
            "conflicts": palette_conflicts
        }

        return scene_report, flag_report, conflict_report


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog=TOOL_NAME)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--conversion-target", required=True, choices=["scene_slice", "tilemap", "background_layer", "foreground_layer"])
    parser.add_argument("--output-tileset-path", required=True)
    parser.add_argument("--output-tilemap-path", required=True)
    parser.add_argument("--output-palette-path", required=True)
    parser.add_argument("--rom-resource-strategy", required=True, choices=["IMAGE", "TILESET_MAP", "BIN_CUSTOM", "COMPARE_FLAT"])
    parser.add_argument("--transparency-expected", choices=["true", "false"], default="true")
    parser.add_argument("--generated-at", required=True)
    args = parser.parse_args(argv)

    source_path = Path(args.input)
    out_dir = Path(args.out_dir)

    try:
        scene_report, flag_report, conflict_report = analyze_indexed_png(
            source_path=source_path,
            source_sha256=args.source_sha256,
            conversion_target=args.conversion_target,
            output_tileset_path=args.output_tileset_path,
            output_tilemap_path=args.output_tilemap_path,
            output_palette_path=args.output_palette_path,
            rom_resource_strategy=args.rom_resource_strategy,
            transparency_expected=args.transparency_expected == "true",
            generated_at=args.generated_at
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    _write_json(out_dir / "scene_tilemap_conversion_report.json", scene_report)
    _write_json(out_dir / "tilemap_flag_report.json", flag_report)
    _write_json(out_dir / "per_tile_palette_conflict_report.json", conflict_report)

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
