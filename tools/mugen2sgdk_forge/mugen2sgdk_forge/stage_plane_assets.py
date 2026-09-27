"""Create two shared-palette, indexed stage planes from authored source plates.

The command is a staging converter, not an art generator. It requires the
flattened composite to have already passed the canonical forge-art palette
converter, then splits those exact CRAM colors back into far/near planes. It
fails if recomposition cannot reproduce the flat palette candidate pixel for
pixel. Outputs stay in ``rascunho/`` or ``out/`` and are never promoted.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops

try:
    from forge_art import pixel_contract, vdp_color, visual_workset
except ImportError:  # allow the workspace module to be invoked via PYTHONPATH
    _tools_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(_tools_root / "sgdk_wrapper"))
    from forge_art import pixel_contract, vdp_color, visual_workset


SPEC_SCHEMA = "mugen2sgdk_forge.stage_plane_assets_spec/v1"
TOOL_NAME = "mugen2sgdk_forge.stage_plane_assets"
TOOL_VERSION = "0.2.0"
REQUIRED_SPEC_FIELDS = {
    "schema", "asset_id", "target", "far_source", "near_source",
    "composite_source", "alpha_threshold", "palette_candidate",
    "palette_conversion_report", "palette_conversion_spec", "output_dir",
}


class StagePlaneAssetsError(ValueError):
    """Invalid, stale, or non-reproducible stage asset contract."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _resolve_project_path(root: Path, value: str, *, allowed_roots: set[str], must_exist: bool = True) -> Path:
    raw = Path(value)
    if raw.is_absolute() or ".." in raw.parts or not raw.parts:
        raise StagePlaneAssetsError(f"non_portable_path:{value}")
    resolved = (root / raw).resolve()
    try:
        relative = resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise StagePlaneAssetsError(f"path_escapes_project:{value}") from exc
    if relative.parts[0] not in allowed_roots:
        raise StagePlaneAssetsError(f"path_root_not_allowed:{value}")
    if must_exist and not resolved.is_file():
        raise StagePlaneAssetsError(f"file_not_found:{value}")
    return resolved


def _check_file_binding(root: Path, entry: dict[str, Any], name: str,
                        allowed_roots: set[str]) -> Path:
    if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
        raise StagePlaneAssetsError(f"invalid_file_binding:{name}")
    path = _resolve_project_path(root, entry["path"], allowed_roots=allowed_roots)
    actual = _sha256(path)
    if actual != str(entry["sha256"]).lower():
        raise StagePlaneAssetsError(f"sha256_mismatch:{name}")
    return path


def _snap(rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    return vdp_color.snap_rgb_to_vdp_grid(rgb, oracle=vdp_color.ORACLE_RESCOMP)


def _nearest_index(rgb: tuple[int, int, int], palette: list[tuple[int, tuple[int, int, int]]]) -> int:
    snapped = _snap(rgb)
    return min(palette, key=lambda item: (sum((a - b) ** 2 for a, b in zip(snapped, item[1])), item[0]))[0]


def _read_shared_palette(path: Path, target: tuple[int, int]) -> tuple[list[tuple[int, int, int]], dict[str, Any]]:
    report = pixel_contract.validate_png(path, pixel_contract.ROLE_UNUSED0, oracle="rescomp")
    if report["blocking"]:
        raise StagePlaneAssetsError("palette_candidate_pixel_contract_failed:" + ",".join(report["blocking_statuses"]))
    info = pixel_contract.read_png_chunks(path)
    if (info["width"], info["height"]) != target:
        raise StagePlaneAssetsError("palette_candidate_dimensions_mismatch")
    with Image.open(path) as image:
        if image.mode != "P":
            raise StagePlaneAssetsError("palette_candidate_not_indexed")
        indices = set(image.get_flattened_data())
        if 0 in indices:
            raise StagePlaneAssetsError("palette_candidate_index0_must_be_unused")
        used = sorted(indices)
    palette = [(index, tuple(info["plte"][index])) for index in used]
    if not palette or len(palette) > 15:
        raise StagePlaneAssetsError("shared_palette_must_have_1_to_15_used_colors")
    if len({color for _, color in palette}) != len(palette):
        raise StagePlaneAssetsError("shared_palette_has_alias_colors")
    return palette, report


def _resize_source(path: Path, target: tuple[int, int], threshold: int | None) -> tuple[Image.Image, dict[str, int]]:
    with Image.open(path) as opened:
        image = opened.convert("RGBA")
    source_size = image.size
    if threshold is not None:
        alpha = image.getchannel("A")
        histogram = alpha.histogram()
        coverage = {
            "transparent": histogram[0],
            "partial": sum(histogram[1:255]),
            "opaque": histogram[255],
        }
        image.putalpha(alpha.point(lambda value: 255 if value >= threshold else 0))
    else:
        alpha = image.getchannel("A")
        if alpha.getextrema() != (255, 255):
            raise StagePlaneAssetsError("far_plane_must_be_fully_opaque")
        coverage = {"transparent": 0, "partial": 0, "opaque": image.width * image.height}
    if image.size != target:
        pixel_contract.assert_nearest_resample("NEAREST")
        image = image.resize(target, Image.Resampling.NEAREST)
    if threshold is not None:
        alpha = image.getchannel("A")
        if alpha.getextrema()[0] not in (0, 255) or alpha.getextrema()[1] not in (0, 255):
            raise StagePlaneAssetsError("near_plane_alpha_not_binary_after_threshold")
    if source_size[0] <= 0 or source_size[1] <= 0:
        raise StagePlaneAssetsError("empty_source_image")
    return image, coverage


def _palette_table_from_png(path: Path) -> list[tuple[int, int, int]]:
    info = pixel_contract.read_png_chunks(path)
    colors = [tuple(color) for color in info["plte"]]
    if len(colors) > 16:
        raise StagePlaneAssetsError("shared_palette_plte_over_16")
    colors.extend([(0, 0, 0)] * (16 - len(colors)))
    return colors[:16]


def _index_plane(image: Image.Image, palette: list[tuple[int, tuple[int, int, int]]],
                 table: list[tuple[int, int, int]], transparent0: bool) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    indexed = Image.new("P", rgba.size, 0)
    out = indexed.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, alpha = pixels[x, y]
            if transparent0 and alpha == 0:
                out[x, y] = 0
            else:
                out[x, y] = _nearest_index((r, g, b), palette)
    flat = [component for color in table for component in color]
    indexed.putpalette(flat)
    return indexed


def _canonical_tile(tile: bytes) -> bytes:
    """Canonicalize an 8x8 indexed tile under the H/V flips ResComp ALL permits."""
    rows = [tile[row * 8:(row + 1) * 8] for row in range(8)]
    variants = (
        b"".join(rows),
        b"".join(row[::-1] for row in rows),
        b"".join(rows[::-1]),
        b"".join(row[::-1] for row in rows[::-1]),
    )
    return min(variants)


def _canonical_tile_pool(path: Path) -> set[bytes]:
    with Image.open(path) as opened:
        if opened.mode != "P" or opened.width % 8 or opened.height % 8:
            raise StagePlaneAssetsError("tile_pool_probe_requires_indexed_8x8_png")
        pixels = opened.tobytes()
        width = opened.width
        pool: set[bytes] = set()
        for tile_y in range(0, opened.height, 8):
            for tile_x in range(0, width, 8):
                tile = bytes(
                    pixels[(tile_y + row) * width + tile_x + col]
                    for row in range(8)
                    for col in range(8)
                )
                pool.add(_canonical_tile(tile))
    return pool


def _tile_pool_reuse_probe(far_path: Path, near_path: Path,
                           flat_path: Path) -> dict[str, Any]:
    far_tiles = _canonical_tile_pool(far_path)
    near_tiles = _canonical_tile_pool(near_path)
    flat_tiles = _canonical_tile_pool(flat_path)
    shared = far_tiles & near_tiles
    union = far_tiles | near_tiles
    return {
        "method": "exact_indexed_tile_patterns_canonicalized_over_hv_flips",
        "flip_scope": "horizontal_and_vertical; corresponds to ResComp TILESET optimization ALL",
        "far_unique_tiles": len(far_tiles),
        "near_unique_tiles": len(near_tiles),
        "cross_plane_shared_tiles": len(shared),
        "separate_plane_unique_sum": len(far_tiles) + len(near_tiles),
        "common_tileset_unique_union": len(union),
        "cross_plane_savings_if_runtime_shares_tile_ids": len(shared),
        "flat_composite_unique_tiles": len(flat_tiles),
        "claim_ceiling": "exact_pattern_overlap_probe; common_tileset_runtime_layout_not_implemented_or_proven",
    }


def split_plane_images(
    far_source: Path,
    near_source: Path,
    composite_source: Path,
    palette_candidate: Path,
    output_dir: Path,
    *,
    target: tuple[int, int],
    alpha_threshold: int,
) -> dict[str, Any]:
    """Write shared-palette PNG planes and prove their flat reconstruction."""
    if target[0] < 8 or target[1] < 8 or target[0] % 8 or target[1] % 8:
        raise StagePlaneAssetsError("target_dimensions_must_be_positive_multiples_of_8")
    if not 0 <= alpha_threshold <= 255:
        raise StagePlaneAssetsError("alpha_threshold_out_of_range")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise StagePlaneAssetsError("output_dir_must_be_empty")
    output_dir.mkdir(parents=True, exist_ok=True)

    shared_palette, palette_contract = _read_shared_palette(palette_candidate, target)
    table = _palette_table_from_png(palette_candidate)
    far_rgba, far_alpha = _resize_source(far_source, target, None)
    near_rgba, near_alpha = _resize_source(near_source, target, alpha_threshold)

    # Rebuild the declared source composite independently; this catches a
    # palette candidate derived from different pixels or alpha semantics.
    rebuilt = far_rgba.copy()
    rebuilt.alpha_composite(near_rgba)
    rebuilt_rgb = rebuilt.convert("RGB")
    with Image.open(composite_source) as opened:
        declared_rgb = opened.convert("RGB")
    if declared_rgb.size != target:
        raise StagePlaneAssetsError("composite_source_dimensions_mismatch")
    if Image.eval(ImageChops.difference(rebuilt_rgb, declared_rgb), lambda p: p).getbbox():
        raise StagePlaneAssetsError("composite_source_does_not_match_authored_plates")

    far_indexed = _index_plane(far_rgba, shared_palette, table, False)
    near_indexed = _index_plane(near_rgba, shared_palette, table, True)
    far_path = output_dir / "bg_b_far_indexed.png"
    near_path = output_dir / "bg_a_near_indexed.png"
    far_indexed.save(far_path, "PNG", bits=4)
    near_indexed.save(near_path, "PNG", bits=4, transparency=0)

    far_compliance = pixel_contract.validate_png(far_path, pixel_contract.ROLE_UNUSED0, oracle="rescomp")
    near_compliance = pixel_contract.validate_png(near_path, pixel_contract.ROLE_TRANSPARENT0, oracle="rescomp")
    if far_compliance["blocking"] or near_compliance["blocking"]:
        raise StagePlaneAssetsError("split_plane_pixel_contract_failed")

    far_rgb = far_indexed.convert("RGB")
    near_rgb = near_indexed.convert("RGB")
    near_mask = Image.frombytes(
        "L", near_indexed.size,
        bytes(255 if value else 0 for value in near_indexed.tobytes()),
    )
    reconstructed = far_rgb.copy()
    reconstructed.paste(near_rgb, mask=near_mask)
    with Image.open(palette_candidate) as opened:
        expected_rgb = opened.convert("RGB")
    diff = ImageChops.difference(reconstructed, expected_rgb)
    mismatch_pixels = sum(1 for value in diff.convert("RGB").get_flattened_data()
                          if value != (0, 0, 0))
    reconstruction_path = output_dir / "reconstruction_rgb.png"
    reconstructed.save(reconstruction_path, "PNG")

    report = {
        "schema_version": "1.0.0",
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "status": "technical_candidate" if mismatch_pixels == 0 else "rejected",
        "blocking": mismatch_pixels != 0,
        "blockers": [] if mismatch_pixels == 0 else ["shared_palette_recomposition_mismatch"],
        "target": {"width": target[0], "height": target[1], "raw_tiles_per_plane": (target[0] // 8) * (target[1] // 8)},
        "shared_palette": [{"index": index, "rgb": list(color)} for index, color in shared_palette],
        "palette_source": {"path": palette_candidate.name, "sha256": _sha256(palette_candidate),
                           "content_sha256": palette_contract["content_sha256"]},
        "alpha_threshold": alpha_threshold,
        "far_plane": {"path": far_path.name, "sha256": _sha256(far_path),
                      "pixel_contract": far_compliance, "alpha_source_counts": far_alpha},
        "near_plane": {"path": near_path.name, "sha256": _sha256(near_path),
                       "pixel_contract": near_compliance, "alpha_source_counts": near_alpha},
        "reconstruction": {"path": reconstruction_path.name, "sha256": _sha256(reconstruction_path),
                           "mismatch_pixels_vs_palette_candidate": mismatch_pixels},
        "tile_pool_reuse_probe": _tile_pool_reuse_probe(far_path, near_path, palette_candidate),
        "claim_ceiling": "shared_palette_indexed_planes_no_rescomp_or_runtime_proof",
    }
    report_path = output_dir / "stage_plane_assets_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report


def convert_from_spec(project_root: Path, spec_path: Path) -> dict[str, Any]:
    root = project_root.resolve()
    spec_file = spec_path.resolve() if spec_path.is_absolute() else (root / spec_path).resolve()
    try:
        spec_file.relative_to(root)
    except ValueError as exc:
        raise StagePlaneAssetsError("spec_outside_project") from exc
    try:
        spec = json.loads(spec_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise StagePlaneAssetsError(f"invalid_spec:{exc}") from exc
    if not isinstance(spec, dict) or set(spec) != REQUIRED_SPEC_FIELDS or spec.get("schema") != SPEC_SCHEMA:
        raise StagePlaneAssetsError("spec_schema_or_fields_invalid")
    if not isinstance(spec["asset_id"], str) or not re.fullmatch(r"[a-z0-9_]+", spec["asset_id"]):
        raise StagePlaneAssetsError("asset_id_invalid")
    target_obj = spec["target"]
    if not isinstance(target_obj, dict) or set(target_obj) != {"width", "height"}:
        raise StagePlaneAssetsError("target_invalid")
    target = (target_obj["width"], target_obj["height"])
    if any(isinstance(v, bool) or not isinstance(v, int) for v in target):
        raise StagePlaneAssetsError("target_dimensions_invalid")
    if isinstance(spec["alpha_threshold"], bool) or not isinstance(spec["alpha_threshold"], int):
        raise StagePlaneAssetsError("alpha_threshold_invalid")

    visual_workset.enforce_operation(root, "technical_conversion")
    far_path = _check_file_binding(root, spec["far_source"], "far_source", {"rascunho", "data"})
    near_path = _check_file_binding(root, spec["near_source"], "near_source", {"rascunho", "data"})
    composite_path = _check_file_binding(root, spec["composite_source"], "composite_source", {"rascunho", "data"})
    for source in (far_path, near_path, composite_path):
        visual_workset.enforce_declared_source(root, source, require_production_eligible=True)
    palette_path = _check_file_binding(root, spec["palette_candidate"], "palette_candidate", {"out"})
    conversion_report_path = _check_file_binding(root, spec["palette_conversion_report"], "palette_conversion_report", {"out"})
    conversion_spec_path = _check_file_binding(root, spec["palette_conversion_spec"], "palette_conversion_spec", {"rascunho"})

    conversion_report = json.loads(conversion_report_path.read_text(encoding="utf-8"))
    if (conversion_report.get("tool") != "forge_art.convert" or
            conversion_report.get("route") != "technical_conversion" or
            conversion_report.get("status") != "technical_candidate" or
            conversion_report.get("blocking") is not False or
            conversion_report.get("source_sha256") != _sha256(composite_path) or
            conversion_report.get("spec_sha256") != _sha256(conversion_spec_path) or
            conversion_report.get("content_sha256") != pixel_contract.validate_png(
                palette_path, pixel_contract.ROLE_UNUSED0, oracle="rescomp")["content_sha256"]):
        raise StagePlaneAssetsError("palette_candidate_provenance_mismatch")
    expected_palette_path = conversion_report_path.parent.parent / conversion_report.get("output", "")
    if expected_palette_path.resolve() != palette_path.resolve():
        raise StagePlaneAssetsError("palette_candidate_path_not_bound_to_report")

    output_dir = _resolve_project_path(root, spec["output_dir"], allowed_roots={"rascunho", "out"}, must_exist=False)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise StagePlaneAssetsError("output_dir_must_be_empty")
    result = split_plane_images(
        far_path, near_path, composite_path, palette_path, output_dir,
        target=target, alpha_threshold=spec["alpha_threshold"],
    )
    result["asset_id"] = spec["asset_id"]
    result["source_bindings"] = {
        "spec_path": spec_file.relative_to(root).as_posix(),
        "spec_sha256": _sha256(spec_file),
        "far_source_sha256": _sha256(far_path),
        "near_source_sha256": _sha256(near_path),
        "composite_source_sha256": _sha256(composite_path),
        "palette_conversion_report_sha256": _sha256(conversion_report_path),
        "palette_conversion_spec_sha256": _sha256(conversion_spec_path),
    }
    report_path = output_dir / "stage_plane_assets_report.json"
    result["report_path"] = report_path.relative_to(root).as_posix()
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result
