from __future__ import annotations

import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

EXPECTED_PNGS = {
    "res/blue_circuit/title_logo.png": (128, 48, True),
    "res/blue_circuit/stage_01_bg.png": (320, 224, False),
    "res/blue_circuit/stage_01_fg.png": (320, 224, True),
    "res/blue_circuit/player_idle.png": (32, 32, True),
    "res/blue_circuit/player_run.png": (96, 32, True),
    "res/blue_circuit/player_jump.png": (32, 32, True),
    "res/blue_circuit/player_shoot.png": (64, 32, True),
    "res/blue_circuit/line_sentry_idle.png": (32, 24, True),
    "res/blue_circuit/breaker_core_idle.png": (48, 48, True),
    "res/blue_circuit/projectile_pulse.png": (16, 8, True),
}

EXPECTED_REPORTS = [
    "out/logs/model_sheet_to_sprite_fidelity_report.json",
    "out/logs/sprite_artifact_report.json",
    "out/logs/pixel_compliance_report.json",
    "out/logs/scene_tilemap_conversion_report.json",
    "out/logs/per_tile_palette_conflict_report.json",
    "out/logs/asset_optimization_report.json",
    "out/logs/source_to_rom_asset_map.json",
]

EXPECTED_RESOURCE_SYMBOLS = [
    "img_bc_title_logo",
    "img_bc_stage_bg",
    "img_bc_stage_fg",
    "spr_bc_player_idle",
    "spr_bc_player_run",
    "spr_bc_player_jump",
    "spr_bc_player_shoot",
    "spr_bc_line_sentry_idle",
    "spr_bc_breaker_core_idle",
    "spr_bc_projectile_pulse",
]


def read_chunks(path: Path) -> dict[str, list[bytes]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise AssertionError(f"{path}: not a PNG")

    chunks: dict[str, list[bytes]] = {}
    offset = 8
    while offset + 8 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8].decode("ascii")
        start = offset + 8
        end = start + length
        chunks.setdefault(kind, []).append(data[start:end])
        offset = end + 4
        if kind == "IEND":
            break
    return chunks


def validate_png(rel: str, width: int, height: int, transparent: bool) -> None:
    path = ROOT / rel
    assert path.exists(), f"missing {rel}"
    chunks = read_chunks(path)
    ihdr = chunks["IHDR"][0]
    actual_width, actual_height, bit_depth, color_type = struct.unpack(">IIBB", ihdr[:10])

    assert (actual_width, actual_height) == (width, height), (
        f"{rel}: expected {width}x{height}, got {actual_width}x{actual_height}"
    )
    assert width % 8 == 0 and height % 8 == 0, f"{rel}: dimensions must align to 8px grid"
    assert color_type == 3, f"{rel}: expected indexed PNG color type 3, got {color_type}"
    assert bit_depth == 4, f"{rel}: expected 4bpp indexed PNG, got {bit_depth}bpp"

    palette = chunks.get("PLTE", [b""])[0]
    entries = len(palette) // 3
    assert 1 <= entries <= 16, f"{rel}: expected PLTE <= 16 entries, got {entries}"

    for index in range(entries):
        r, g, b = palette[index * 3 : index * 3 + 3]
        assert r % 0x22 == 0 and g % 0x22 == 0 and b % 0x22 == 0, (
            f"{rel}: palette index {index} is not snapped to Mega Drive 9-bit grid"
        )

    if transparent:
        assert palette[:3] == bytes([0xEE, 0x00, 0xEE]), f"{rel}: palette index 0 must be #EE00EE"
        assert "tRNS" in chunks, f"{rel}: missing tRNS transparency chunk"
        assert chunks["tRNS"][0][0] == 0, f"{rel}: transparent index must be 0"


def validate_reports() -> None:
    for rel in EXPECTED_REPORTS:
        path = ROOT / rel
        assert path.exists(), f"missing report {rel}"
        payload = json.loads(path.read_text(encoding="utf-8"))
        if rel.endswith("scene_tilemap_conversion_report.json"):
            assert payload.get("status") == "ok", f"{rel}: status must be ok"
            assert payload.get("final_unique_tiles", 0) > 0, f"{rel}: final_unique_tiles must be measured"
            continue
        if rel.endswith("per_tile_palette_conflict_report.json"):
            assert payload.get("conflicts_total") == 0, f"{rel}: conflicts_total must be 0"
            continue
        assert payload.get("status") == "passed", f"{rel}: status must be passed"


def validate_resources_res() -> None:
    text = (ROOT / "res/resources.res").read_text(encoding="utf-8")
    for symbol in EXPECTED_RESOURCE_SYMBOLS:
        assert symbol in text, f"res/resources.res missing {symbol}"


def main() -> int:
    failures: list[str] = []

    for rel, (width, height, transparent) in EXPECTED_PNGS.items():
        try:
            validate_png(rel, width, height, transparent)
        except AssertionError as exc:
            failures.append(str(exc))

    for check in (validate_reports, validate_resources_res):
        try:
            check()
        except AssertionError as exc:
            failures.append(str(exc))

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1

    print("PASS: BLUE_CIRCUIT VDP asset contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
