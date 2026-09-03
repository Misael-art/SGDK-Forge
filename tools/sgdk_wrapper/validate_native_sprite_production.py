#!/usr/bin/env python3
"""Semantic validator for the native-sprite production record.

This is the *source of executable truth* for the artigian pipe. It is NOT a
schema-only checker. Given a `native_sprite_production_record.json`, it:

  - resolves every artifact path safely inside the project root (rejects active
    absolute path, traversal, external symlink and wrong-root casing);
  - re-derives PNG measurements from disk (dimension, mode, visible colors,
    occupancy) instead of trusting the JSON;
  - re-runs forge-art's pixel contract on the candidate;
  - proves the five visual evidences (native_1x, nearest, light, dark, chroma) exist,
    are DISTINCT files, are derived from the SAME candidate sha256, and that
    native_1x is byte-identical to the candidate;
  - cross-checks provenance: interaction_channel vs source_kind vs action log;
  - enforces gate independence: scale_pass, visual_pass, budget_pass and
    human_pass stay separate and no promotion happens while any required gate is
    pending/failed;
  - requires incumbent + methodology references to exist with a valid hash and a
    declared role (comparison, never a pixel source);
  - rejects false greens even when the JSON hashes are re-sealed, e.g. every
    visual_evidence pointing to the same panel.

Interface (documented in native-sprite-production-loop.md):
    python validate_native_sprite_production.py --project-root <p> --record <r>
    python validate_native_sprite_production.py <r>   (positional, kept for compat)

This tool NEVER writes artifacts, never promotes, never changes res/. It fails
closed and is consumed by aaa-pipeline-guardian for the visual claim ceiling.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from forge_art import pixel_contract, vdp_color
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from forge_art import pixel_contract, vdp_color

TOOL_NAME = "validate_native_sprite_production"
TOOL_VERSION = "2.5.0"
SCHEMA_VERSION = "1.4.0"

# Semantic regions required for a legible native character silhouette.
REQUIRED_REGIONS = {
    "head_or_face", "hair", "torso", "arms_or_guard", "hands",
    "legs", "feet", "sash",
}

# Gates that are mandatory (never "not_applicable") for a critical character.
MANDATORY_GATES = {
    "pixel_contract", "native_visual", "scale", "budget", "human",
}


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve(project_root: Path, raw: str) -> Path | None:
    """Resolve a path against project_root, safely. Returns None on any escape."""
    if not raw:
        return None
    p = Path(raw)
    try:
        resolved = p.resolve()
    except OSError:
        return None
    if p.is_absolute():
        # Allow an absolute path only if it ends up inside the project root.
        if _inside(project_root, resolved):
            return resolved
        return None
    resolved = (project_root / p).resolve()
    if not _inside(project_root, resolved):
        return None
    return resolved


def _inside(project_root: Path, path: Path) -> bool:
    try:
        path.resolve().relative_to(project_root)
        return True
    except ValueError:
        return False


def _transparent_indices(img) -> set[int]:
    """Return the set of palette indices that are transparent (tRNS alpha 0).

    For a mode-P indexed PNG, transparency is declared in the tRNS chunk (not by
    RGB value). For a mode with an alpha channel, the transparent pixels are
    those with alpha == 0. This deliberately does NOT assume index 0.
    """
    info = img.info
    trns = info.get("transparency")
    transparent: set[int] = set()
    if isinstance(trns, bytes):
        transparent = {i for i, a in enumerate(trns) if a == 0}
    elif isinstance(trns, int):
        transparent = {trns}
    return transparent


def _png_metrics(path: Path) -> dict[str, Any]:
    """Measure a PNG from disk, counting only VISIBLE (non-transparent) pixels.

    `filled_pixels` excludes transparent pixels. `visible_colors` excludes any
    palette index that is transparent. `canvas_pixels` is the full bounding area.
    `bbox` is the bounding box of visible (non-transparent) pixels only.
    """
    from PIL import Image
    with Image.open(path) as img:
        width, height = img.size
        mode = img.mode
        total = width * height

        if mode == "P":
            transparent = _transparent_indices(img)
            px = img.tobytes()
            visible_pixels = sum(1 for idx in px if idx not in transparent)
            # Count distinct visible colors (by palette index, excluding transparent).
            visible_indices = {idx for idx in px if idx not in transparent}
            visible_color_count = len([i for i in visible_indices])  # indices, not RGB yet
            # bbox of visible pixels.
            xs: list[int] = []
            ys: list[int] = []
            for i, idx in enumerate(px):
                if idx in transparent:
                    continue
                x = i % width
                y = i // width
                xs.append(x)
                ys.append(y)
            bbox = [min(xs), min(ys), max(xs) + 1, max(ys) + 1] if xs else None
            # Resolve distinct visible RGB colors from the palette.
            palette = img.getpalette() or []
            palette_rgb = [tuple(palette[i * 3:i * 3 + 3]) for i in range(len(palette) // 3)]
            distinct_rgb = {palette_rgb[i] for i in visible_indices if i < len(palette_rgb)}
            visible_colors = len(distinct_rgb)
        else:
            rgba = img.convert("RGBA")
            a = 0  # placeholder
            alpha = rgba.getchannel("A")
            raw = rgba.tobytes()
            visible_pixels = 0
            distinct_rgb = set()
            stride = 4
            for i in range(0, len(raw), stride):
                r, g, b, al = raw[i], raw[i + 1], raw[i + 2], raw[i + 3]
                if al == 0:
                    continue
                visible_pixels += 1
                distinct_rgb.add((r, g, b))
            visible_colors = len(distinct_rgb)
            bbox = None  # derive if needed
            xs = []
            ys = []
            for i in range(0, len(raw), stride):
                al = raw[i + 3]
                if al == 0:
                    continue
                p = i // stride
                xs.append(p % width)
                ys.append(p // width)
            bbox = [min(xs), min(ys), max(xs) + 1, max(ys) + 1] if xs else None

        occupancy_pct = round(visible_pixels / total * 100, 2) if total else 0.0
        return {
            "width": width,
            "height": height,
            "mode": mode,
            "visible_colors": visible_colors,
            "filled_pixels": visible_pixels,
            "canvas_pixels": total,
            "occupancy_pct": occupancy_pct,
            "bbox": bbox,
        }


def _producer_png_metadata(path: Path) -> dict[str, Any]:
    """Return producer metadata re-derived from the PNG, including alpha values."""
    from PIL import Image
    metrics = _png_metrics(path)
    with Image.open(path) as img:
        if img.mode == "P":
            transparent = _transparent_indices(img)
            raw = img.tobytes()
            alpha_values = {0 if idx in transparent else 255 for idx in raw}
        else:
            alpha_values = set(img.convert("RGBA").getchannel("A").getdata())
    return {
        "width": metrics["width"], "height": metrics["height"],
        "mode": metrics["mode"], "visible_rgb_colors": metrics["visible_colors"],
        "alpha_values": sorted(alpha_values),
    }


def _visible_mask(path: Path) -> list[bool]:
    """Return the exact binary visibility mask used by shape-block checks."""
    from PIL import Image
    with Image.open(path) as img:
        if img.mode == "P":
            transparent = _transparent_indices(img)
            return [idx not in transparent for idx in img.tobytes()]
        return [alpha != 0 for alpha in img.convert("RGBA").getchannel("A").getdata()]


def _boundary_mask(mask: list[bool], width: int, height: int) -> list[bool]:
    result = [False] * len(mask)
    for y in range(height):
        for x in range(width):
            pos = y * width + x
            if not mask[pos]:
                continue
            result[pos] = any(nx < 0 or ny < 0 or nx >= width or ny >= height
                              or not mask[ny * width + nx]
                              for nx, ny in ((x - 1, y), (x + 1, y),
                                             (x, y - 1), (x, y + 1)))
    return result


def _material_boundary_mask(labels: list[int], width: int, height: int) -> list[bool]:
    """Mark visible pixels touching a different visible material label."""
    result = [False] * len(labels)
    for y in range(height):
        for x in range(width):
            pos = y * width + x
            label = labels[pos]
            if label == 0:
                continue
            result[pos] = any(
                0 <= nx < width and 0 <= ny < height
                and labels[ny * width + nx] not in (0, label)
                for nx, ny in ((x - 1, y), (x + 1, y),
                               (x, y - 1), (x, y + 1))
            )
    return result


def _validate_material_region_contract(project_root: Path, rec: dict[str, Any],
                                       nc: dict[str, Any], native_path: Path,
                                       metrics: dict[str, Any], fail, warn) -> None:
    """Re-derive material ownership and reject cross-material palette leakage.

    Anatomy and material are intentionally independent contracts. A torso label
    cannot prove where a crop top ends and exposed skin begins. This gate binds
    every visible candidate pixel to one explicit material owner and checks that
    its palette index is legal for that owner (or is a declared shared outline).
    """
    from PIL import Image

    contract = nc.get("material_region_contract")
    version = str(rec.get("schema_version", ""))
    gate = _gate_status(rec.get("gates", {}), "material_topology")
    required = version == "1.4.0"

    if not isinstance(contract, dict):
        if required:
            fail("material_region_contract_missing",
                 "schema 1.4.0 requires an explicit material ownership map; "
                 "anatomical semantic regions do not prove garment/skin boundaries")
        if gate == "passed":
            fail("material_topology_pass_without_contract",
                 "gate.material_topology=passed but material_region_contract is missing")
        return

    if required and gate == "not_started":
        fail("material_topology_gate_missing",
             "schema 1.4.0 requires gates.material_topology")

    source_ref = contract.get("source_reference") or {}
    source_path = _resolve(project_root, source_ref.get("path", ""))
    if source_path is None or not source_path.is_file():
        fail("material_source_reference_missing",
             "material_region_contract.source_reference must resolve inside the project")
    elif source_ref.get("sha256") != _sha256_file(source_path):
        fail("material_source_reference_hash_mismatch",
             "material topology reference hash does not match disk")

    paths: dict[str, Path] = {}
    for key in ("material_region_map", "material_boundary_overlay"):
        artifact = contract.get(key)
        raw = artifact.get("path") if isinstance(artifact, dict) else ""
        path = _resolve(project_root, raw)
        if path is None or not path.is_file():
            fail(f"{key}_missing", f"material_region_contract.{key} missing: {raw!r}")
            continue
        paths[key] = path
        try:
            with Image.open(path) as image:
                if image.size != (metrics["width"], metrics["height"]):
                    fail(f"{key}_dimension_mismatch",
                         f"{key} {image.size} != candidate "
                         f"{metrics['width']}x{metrics['height']}")
        except OSError:
            fail(f"{key}_unreadable", f"{key} could not be read")
            continue
        if not isinstance(artifact, dict):
            fail(f"{key}_link_missing", f"{key} must be a bound artifact object")
            continue
        if artifact.get("sha256") != _sha256_file(path):
            fail(f"{key}_hash_mismatch", f"{key}.sha256 does not match artifact bytes")
        if artifact.get("asset_id") != rec.get("asset_id"):
            fail(f"{key}_asset_id_mismatch", f"{key}.asset_id does not match record")
        expected_scale = f"{nc.get('width')}x{nc.get('height')}"
        if artifact.get("scale") != expected_scale:
            fail(f"{key}_scale_mismatch", f"{key}.scale != {expected_scale}")
        if _resolve(project_root, artifact.get("source", "")) != native_path:
            fail(f"{key}_source_mismatch", f"{key}.source must resolve to candidate")

    if len(paths) != 2:
        return
    if paths["material_region_map"] == paths["material_boundary_overlay"]:
        fail("material_artifacts_not_distinct",
             "material map and boundary overlay must be distinct files")
        return

    try:
        with Image.open(native_path) as image:
            if image.mode != "P":
                fail("material_candidate_not_indexed",
                     "material ownership validation requires indexed candidate pixels")
                return
            candidate_indices = list(image.tobytes())
        with Image.open(paths["material_region_map"]) as image:
            labels = list(image.convert("P").tobytes())
        with Image.open(paths["material_boundary_overlay"]) as image:
            overlay = list(image.convert("P").tobytes())
    except OSError as exc:
        fail("material_contract_artifact_unreadable", str(exc))
        return

    candidate_mask = _visible_mask(native_path)
    if [label != 0 for label in labels] != candidate_mask:
        fail("material_union_candidate_mismatch",
             "material-region union must exactly equal candidate visibility")

    legend = contract.get("material_label_legend") or {}
    counts = contract.get("material_label_counts") or {}
    allowed = contract.get("allowed_palette_indices") or {}
    shared = set(contract.get("shared_outline_indices") or [])
    if set(legend) != set(counts) or set(legend) != set(allowed):
        fail("material_contract_roles_mismatch",
             "legend, counts and allowed_palette_indices must declare identical roles")
    legend_values = [int(value) for value in legend.values()]
    if len(set(legend_values)) != len(legend_values):
        fail("material_label_legend_alias",
             "each material role needs a unique region-map label")
    invalid_labels = set(labels) - {0} - set(legend_values)
    if invalid_labels:
        fail("material_region_map_invalid_labels",
             f"material map contains undeclared labels {sorted(invalid_labels)}")
    actual_counts = {name: labels.count(int(value)) for name, value in legend.items()}
    if any(value <= 0 for value in actual_counts.values()):
        fail("material_regions_empty", f"material roles have no pixels: {actual_counts}")
    if counts != actual_counts:
        fail("material_label_counts_mismatch",
             f"declared material counts {counts} != re-derived {actual_counts}")

    material_roles = set((rec.get("palette_contract") or {}).get("material_roles") or [])
    if material_roles != set(legend):
        fail("palette_material_roles_mismatch",
             "palette_contract.material_roles must equal material map roles")

    owners: dict[int, str] = {}
    for material, raw_indices in allowed.items():
        for index in raw_indices:
            if index in shared:
                fail("shared_outline_redeclared_as_material",
                     f"palette index {index} is both shared outline and owned by {material}")
            previous = owners.get(index)
            if previous and previous != material:
                fail("material_palette_role_overlap",
                     f"palette index {index} is owned by both {previous} and {material}")
            owners[index] = material

    label_to_material = {int(value): name for name, value in legend.items()}
    leakage: list[dict[str, int | str]] = []
    for pos, label in enumerate(labels):
        if label == 0:
            continue
        material = label_to_material.get(label)
        index = candidate_indices[pos]
        if material is None or (index not in set(allowed.get(material, [])) and index not in shared):
            if len(leakage) < 12:
                leakage.append({"x": pos % metrics["width"], "y": pos // metrics["width"],
                                "material": material or "undeclared", "palette_index": index})
    if leakage:
        fail("material_palette_leakage",
             f"candidate uses palette indices outside their material owner; samples={leakage}")

    expected_boundary = _material_boundary_mask(labels, metrics["width"], metrics["height"])
    actual_boundary = [value == 1 for value in overlay]
    actual_interior = [value == 2 for value in overlay]
    if set(overlay) - {0, 1, 2} or actual_boundary != expected_boundary \
            or any(actual_interior[i] != (labels[i] != 0 and not expected_boundary[i])
                   for i in range(len(labels))):
        fail("material_boundary_overlay_not_derived",
             "boundary overlay must use 1 between different materials and 2 inside a material")

    for item in contract.get("critical_boundaries") or []:
        a = legend.get(item.get("material_a"))
        b = legend.get(item.get("material_b"))
        if a is None or b is None or a == b:
            fail("critical_material_boundary_invalid",
                 f"boundary {item.get('boundary_id')!r} names missing/equal materials")
            continue
        region = item.get("region") or [0, 0, metrics["width"], metrics["height"]]
        x0, y0, x1, y1 = [int(value) for value in region]
        if not (0 <= x0 < x1 <= metrics["width"] and
                0 <= y0 < y1 <= metrics["height"]):
            fail("critical_material_boundary_region_invalid",
                 f"boundary {item.get('boundary_id')!r} region {region!r} is outside candidate")
            continue
        contacts = 0
        for y in range(y0, y1):
            for x in range(x0, x1):
                pos = y * metrics["width"] + x
                if labels[pos] not in (a, b):
                    continue
                for nx, ny in ((x + 1, y), (x, y + 1)):
                    if nx < x1 and ny < y1:
                        pair = {labels[pos], labels[ny * metrics["width"] + nx]}
                        if pair == {a, b}:
                            contacts += 1
        if contacts < int(item.get("minimum_contact_edges", 1)):
            fail("critical_material_boundary_missing",
                 f"boundary {item.get('boundary_id')!r} has {contacts} contact edges; "
                 f"needs {item.get('minimum_contact_edges')}")

    blockers = contract.get("blocking_statuses") or []
    if gate == "passed" and (contract.get("status") != "passed" or blockers):
        fail("material_topology_pass_without_contract",
             "gate.material_topology=passed requires contract.status=passed and no blockers")
    if _gate_status(rec.get("gates", {}), "color_blocking") == "passed" \
            and contract.get("status") != "passed":
        fail("color_blocking_pass_without_material_topology",
             "color_blocking cannot pass before material ownership passes")
    if not leakage and contract.get("status") == "passed" and not blockers:
        warn(f"material topology re-derived OK ({len(legend)} materials, "
             f"{len(contract.get('critical_boundaries') or [])} critical boundaries)")


def _gate_status(gates: dict[str, Any], name: str) -> str:
    return str(gates.get(name, "not_started"))


def _recheck_visual_evidence(ev_paths: dict[str, Path], nc: dict,
                             native_path: Path, candidate_sha: str,
                             fail, warn) -> None:
    """Deterministically re-derive the five visual evidences from the candidate.

    native_1x must be byte-identical to the candidate. nearest_preview must be
    generated at preview_scale by NEAREST from the candidate. light/dark/chroma
    must be recomposited on the declared RGB backgrounds. Distinct PATHS are not
    enough — the CONTENT must actually correspond to each role.
    """
    from PIL import Image

    # native_1x byte-identical.
    try:
        if _sha256_file(ev_paths["native_1x"]) != candidate_sha:
            fail("native_1x_not_candidate",
                 "native_1x sha256 != candidate sha256 (must be byte-identical)")
    except OSError:
        fail("native_1x_unreadable", "native_1x could not be read")

    scale = int(nc.get("visual_evidence", {}).get("preview_scale") or 8)
    try:
        with Image.open(native_path) as base:
            expected_nearest = base.resize((base.width * scale, base.height * scale),
                                           Image.NEAREST)
            with Image.open(ev_paths["nearest_preview"]) as got:
                if got.size != expected_nearest.size:
                    fail("nearest_preview_size_wrong",
                         f"nearest_preview {got.size} != candidate*{scale} = {expected_nearest.size}")
                a = base.convert("RGBA")
                b = got.convert("RGBA")
                if a.size == (b.width // scale, b.height // scale):
                    # Downscale got back to native and compare pixel-by-pixel.
                    reduced = got.resize(a.size, Image.NEAREST).convert("RGBA")
                    if _img_pixels(a) != _img_pixels(reduced):
                        fail("nearest_preview_not_nearest",
                             "nearest_preview content is not the candidate scaled by NEAREST")
                elif got.size == expected_nearest.size:
                    # Make a reference of the candidate scaled and compare content.
                    if _img_pixels(expected_nearest.convert("RGBA")) != _img_pixels(b):
                        fail("nearest_preview_not_nearest",
                             "nearest_preview content is a recomposite, not NEAREST of candidate")
    except OSError as exc:
        fail("nearest_preview_unreadable", f"nearest_preview could not be read: {exc}")

    # light/dark/chroma recomposited on declared RGB backgrounds.
    ve = nc.get("visual_evidence", {})
    light_rgb = ve.get("light_rgb")
    dark_rgb = ve.get("dark_rgb")
    chroma_rgb = ve.get("chroma_rgb")
    for role, rgb, path in (("light_background", light_rgb, ev_paths["light_background"]),
                            ("dark_background", dark_rgb, ev_paths["dark_background"]),
                            ("chroma_background", chroma_rgb, ev_paths["chroma_background"])):
        if not (isinstance(rgb, list) and len(rgb) == 3):
            fail(f"{role}_rgb_invalid", f"visual_evidence.{role} needs a 3-int RGB")
            continue
        try:
            with Image.open(native_path) as cand:
                alpha_cand = cand.convert("RGBA")
            bg = Image.new("RGBA", alpha_cand.size, (rgb[0], rgb[1], rgb[2], 255))
            bg.alpha_composite(alpha_cand)
            with Image.open(path) as got:
                if got.size != bg.size:
                    fail(f"{role}_size_wrong",
                         f"{role} {got.size} != candidate size {bg.size}")
                if _img_pixels(bg.convert("RGBA")) != _img_pixels(got.convert("RGBA")):
                    fail(f"{role}_not_recomposite",
                         f"{role} content is not the candidate recomposited on RGB {rgb}")
        except OSError as exc:
            fail(f"{role}_unreadable", f"{role} could not be read: {exc}")


def _img_pixels(img) -> bytes:
    return img.tobytes()


def _validate_record_schema(record: Any, schema_path: Path) -> tuple[list[str], str]:
    """Validate the record against its schema (Draft 2020-12).

    This schema uses Draft 2020-12 features ($ref/oneOf/type unions) that the
    lightweight forge-art schema gate does not implement completely. Therefore
    only the reference `jsonschema` executor is accepted here. The workspace's
    prepared, repository-local dependency directory is tried before failing
    closed.
    """
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"schema_invalid_json: {exc}"], "none"

    # Reference Draft 2020-12 implementation. The environment guard prepares
    # this dependency under out/host_tools without mutating the system Python.
    try:
        import jsonschema  # type: ignore
        from jsonschema import Draft202012Validator  # type: ignore
    except Exception:
        jsonschema = None
    if jsonschema is None:
        local_site = (Path(__file__).resolve().parents[2] / "out" / "host_tools" /
                      "python" / "site-packages")
        if local_site.is_dir() and str(local_site) not in sys.path:
            sys.path.insert(0, str(local_site))
        try:
            import jsonschema  # type: ignore
            from jsonschema import Draft202012Validator  # type: ignore
        except Exception as exc:
            return [
                "schema_dependency_unavailable: Draft 2020-12 validation requires "
                "jsonschema; run tools/sgdk_wrapper/ensure_linux_python_deps.sh "
                f"after the environment guard ({exc})"
            ], "none"
    if jsonschema is not None:
        validator = Draft202012Validator(schema)
        errors = sorted(validator.iter_errors(record), key=lambda e: list(e.absolute_path))
        msgs = [f"{'.'.join(map(str, e.absolute_path)) or '$'}: {e.message}" for e in errors]
        return msgs, "jsonschema:draft202012"

    return ["schema_dependency_unavailable: jsonschema could not be loaded"], "none"


def _validate_pixel_report(pr_doc: dict[str, Any], schema_path: Path) -> tuple[list[str], str]:
    """Validate the canonical pixel report using the same Draft 2020-12 engine."""
    return _validate_record_schema(pr_doc, schema_path)


def validate_record(project_root: Path | None, record_path: Path,
                    require_shape_block_contract: bool = False) -> dict[str, Any]:
    errors: list[dict[str, str]] = []
    warnings: list[str] = []

    def fail(code: str, detail: str) -> None:
        errors.append({"code": code, "message": detail})

    def warn(detail: str) -> None:
        warnings.append(detail)

    # --- load record ---
    if not record_path.is_file():
        fail("record_missing", f"record not found: {record_path}")
        return {"status": "failed", "errors": errors, "warnings": warnings,
                "promotable": False}

    try:
        rec = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail("record_invalid_json", f"record is not valid JSON: {exc}")
        return {"status": "failed", "errors": errors, "warnings": warnings,
                "promotable": False}

    # Execute the full Draft 2020-12 schema inside the validator. A partial
    # schema executor is not sufficient for a production claim.
    schema_path = Path(__file__).with_name("schemas") / "native_sprite_production_record.schema.json"
    schema_errors, schema_executor = _validate_record_schema(rec, schema_path)
    if schema_errors:
        for msg in schema_errors:
            fail("record_schema_violation", msg)
    else:
        warn(f"record schema validated by {schema_executor}")

    # project_root is REQUIRED for safe path resolution. Portability/casing of the
    # repo root is NOT a sprite-validator concern (the host/root contract owns it);
    # the caller passes a resolved, existing, canonical project root.
    if project_root is None:
        fail("project_root_required",
             "pass --project-root so artifact paths resolve safely")
        return {"status": "failed", "errors": errors, "warnings": warnings,
                "promotable": False}
    if not project_root.is_dir():
        fail("project_root_not_exist",
             f"project root does not exist or is not a directory: {project_root}")

    # --- structural guards: required package-level fields ---
    required_fields = ["schema_version", "asset_id", "source", "scale_contract",
                       "producer_output", "native_candidate", "gates",
                       "promotion", "status"]
    for f in required_fields:
        if f not in rec:
            fail("record_field_missing", f"missing top-level field '{f}'")

    promotion = rec.get("promotion", {})
    promotable = bool(promotion.get("promotable"))
    promotion_target = promotion.get("target", "none")

    gates = rec.get("gates", {})

    # --- source ---
    source = rec.get("source", {})
    src_path = _resolve(project_root, source.get("path", ""))
    if src_path is None:
        fail("source_unresolvable", "source.path escapes project or is empty")
    elif not src_path.is_file():
        fail("source_missing", f"source file not found: {source.get('path')}")
    else:
        real_sha = _sha256_file(src_path)
        if real_sha != source.get("sha256"):
            fail("source_hash_mismatch",
                 f"source sha256 {real_sha[:16]}.. != record {str(source.get('sha256'))[:16]}..")
        classification = source.get("classification")
        if classification not in {"concept_high_res", "ai_generated_high_res",
                                  "authored_raster", "native_pixel_source"}:
            fail("source_classification_invalid", f"source.classification={classification!r}")

    # --- producer_output : all metadata is re-derived from the PNG ---
    po = rec.get("producer_output", {})
    po_path = _resolve(project_root, po.get("path", ""))
    if po_path is None or not po_path.is_file():
        fail("producer_output_missing", f"producer_output.path not found: {po.get('path')}")
    else:
        actual_po = _producer_png_metadata(po_path)
        for key in ("width", "height", "mode", "visible_rgb_colors", "alpha_values"):
            if po.get(key) != actual_po[key]:
                fail("producer_output_metadata_mismatch",
                     f"producer_output.{key}={po.get(key)!r} but PNG re-derives {actual_po[key]!r}")

    # --- provenance : validate the dedicated field, NEVER accidental producer_output fields ---
    prov = rec.get("provenance", {})
    prov_channel = prov.get("interaction_channel", "")
    prov_kind = prov.get("source_kind", "")
    prov_id = prov.get("producer_identity", "")
    prov_action_log = prov.get("action_log", "")

    if prov_channel not in {
        "native_image_tool", "cli_headless", "agent_operated_native_editor_draft",
        "human_pixel_editor", "generative_image_producer", "native_pixel_source",
    }:
        fail("provenance_channel_invalid", f"provenance.interaction_channel={prov_channel!r}")

    if prov_kind not in {
        "ai_authored_pixel", "native_pixel", "hand_authored_pixel",
        "photo_or_render_derived", "procedural_primitive",
    }:
        fail("provenance_source_kind_invalid", f"provenance.source_kind={prov_kind!r}")

    # Human claim must be backed by a REAL human approval file, human identity,
    # a recorded decision, and the exact candidate SHA-256.
    if prov_channel == "human_pixel_editor":
        ha_path = prov.get("human_approval", "")
        ha_resolved = _resolve(project_root, ha_path)
        if not ha_resolved or not ha_resolved.is_file():
            fail("provenance_human_unproven",
                 "provenance.interaction_channel=human_pixel_editor but no real human_approval file")
        if not (prov_id or "").strip():
            fail("provenance_human_identity_missing",
                 "human authoring requires a producer_identity (a named human)")
        if prov_kind == "ai_authored_pixel":
            fail("provenance_contradiction",
                 "human_pixel_editor contradicts provenance.source_kind=ai_authored_pixel")
        decision = va_evidence_sha = None
        # the record must tie the human approval to the exact candidate
        nc_sha = (rec.get("native_candidate") or {}).get("visual_evidence", {}).get("candidate_sha256")
        try:
            ha_doc = json.loads(ha_resolved.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            ha_doc = {}
        if nc_sha:
            if ha_doc.get("sha256") != nc_sha:
                fail("human_approval_sha_mismatch",
                     "human approval sha256 != candidate sha256 (must approve the exact asset)")
            if not ha_doc.get("decision"):
                fail("human_approval_decision_missing", "human approval lacks a recorded decision")
    elif prov_channel in ("agent_operated_native_editor_draft",) and prov_kind == "ai_authored_pixel":
        # Agent-operated binary editor is NOT autoria humana — no human gate allowed.
        if _gate_status(gates, "human") == "passed":
            fail("human_gate_ai_editor",
                 "agent_operated_native_editor_draft cannot claim human gate passed")

    # --- native_candidate : validate against disk (never trust JSON) ---
    nc = rec.get("native_candidate")
    native_path = None
    if isinstance(nc, dict):
        native_path = _resolve(project_root, nc.get("path", ""))
        if native_path is None or not native_path.is_file():
            fail("native_candidate_missing", f"native_candidate.path not found: {nc.get('path')}")
        else:
            # (3a) disk values (width/height/mode/hash) must match the record.
            metrics = _png_metrics(native_path)
            if metrics["width"] != nc.get("width") or metrics["height"] != nc.get("height"):
                fail("candidate_dimension_mismatch",
                     f"candidate on disk {metrics['width']}x{metrics['height']} != record "
                     f"{nc.get('width')}x{nc.get('height')}")
            candidate_sha = _sha256_file(native_path)
            # Canonical content hash (per forge-art pixel contract), for binding
            # the pixel report to the candidate: both sides use the SAME hash
            # semantics (dimensions + depth + PLTE + indices), NOT raw bytes.
            try:
                pc = pixel_contract.validate_png(native_path, pixel_contract.ROLE_TRANSPARENT0)
                canonical_sha = pc.get("content_sha256")
            except pixel_contract.PixelContractError as exc:
                canonical_sha = None
                pc = {"blocking": True, "blocking_statuses": [exc.blocker]}

            # (3b) pixel_report must exist, be schema-valid and bound to the same
            #      canonical content hash as the re-derived pixel contract.
            pr_raw = nc.get("pixel_report", "")
            pr_path = _resolve(project_root, pr_raw)
            if pr_path is None or not pr_path.is_file():
                fail("pixel_report_missing", f"native_candidate.pixel_report not found: {pr_raw!r}")
            else:
                try:
                    pr_doc = json.loads(pr_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    fail("pixel_report_invalid_json", "pixel_report is not valid JSON")
                    pr_doc = {}
                pixel_schema = Path(__file__).with_name("schemas") / "pixel_compliance_report.schema.json"
                pixel_schema_errors, pixel_schema_executor = _validate_pixel_report(pr_doc, pixel_schema)
                if pixel_schema_errors:
                    fail("pixel_report_schema_violation", "; ".join(pixel_schema_errors[:4]))
                else:
                    warn(f"pixel report schema validated by {pixel_schema_executor}")
                pr_content = pr_doc.get("content_sha256")
                if canonical_sha and pr_content and pr_content != canonical_sha:
                    fail("pixel_report_sha_mismatch",
                         f"pixel_report content_sha256 {pr_content[:16]}.. != re-derived "
                         f"{canonical_sha[:16]}.. (both are canonical content hashes)")
                report_candidate = _resolve(project_root, pr_doc.get("candidate_path", ""))
                if report_candidate != native_path:
                    fail("pixel_report_candidate_unbound",
                         "pixel_report.candidate_path does not resolve to native_candidate.path")
                if pr_doc.get("candidate_sha256") != candidate_sha:
                    fail("pixel_report_raw_sha_mismatch",
                         "pixel_report.candidate_sha256 does not match candidate bytes")
                report_checks = {
                    "asset_id": rec.get("asset_id"), "width": metrics["width"],
                    "height": metrics["height"], "mode": metrics["mode"],
                    "visible_colors": metrics["visible_colors"],
                    "filled_pixels": metrics["filled_pixels"],
                    "canvas_pixels": metrics["canvas_pixels"],
                    "bbox": metrics["bbox"], "occupancy_pct": metrics["occupancy_pct"],
                }
                for key, expected in report_checks.items():
                    if pr_doc.get(key) != expected:
                        fail("pixel_report_metadata_mismatch",
                             f"pixel_report.{key}={pr_doc.get(key)!r} but PNG re-derives {expected!r}")

            # (3c) use the re-derived pixel contract verdict; a claimed pass without
            #      a real candidate/report must fail.
            if pc.get("blocking"):
                fail("pixel_contract_rejected",
                     "candidate fails forge-art pixel contract: " +
                     ",".join(pc.get("blocking_statuses") or []))
            else:
                warn(f"pixel_contract re-derived OK ({pc.get('visible_colors')} visible, "
                     f"{pc.get('width')}x{pc.get('height')})")
            if _gate_status(gates, "pixel_contract") == "passed" and pc.get("blocking"):
                fail("pixel_contract_pass_without_candidate",
                     "gate.pixel_contract=passed but the candidate fails re-derived pixel contract")
            if _gate_status(gates, "pixel_contract") == "passed" and not pr_path:
                fail("pixel_contract_pass_without_report",
                     "gate.pixel_contract=passed but no pixel_report bound to the candidate")

            # (3d) density: filled_pixels MUST NOT equal canvas_pixels (transparency
            #      excluded); a binary lineart is flagged as low-information.
            if metrics["filled_pixels"] == metrics["canvas_pixels"]:
                fail("canvas_confused_with_visible",
                     "filled_pixels == canvas_pixels: the report used canvas area as "
                     "visible; transparency was not excluded. Expected a real silhouette.")
            if metrics["visible_colors"] and metrics["visible_colors"] <= 2:
                warn(f"low_info_lineart: {metrics['visible_colors']} visible colors, "
                     f"{metrics['filled_pixels']} filled px (binary skeleton, not a "
                     f"translated character)")

            # --- visual_evidence: 5 DISTINCT + deterministically re-derived ---
            ve = nc.get("visual_evidence", {})
            ev_paths: dict[str, Path] = {}
            for role in ("native_1x", "nearest_preview", "light_background", "dark_background",
                         "chroma_background"):
                raw = ve.get(role)
                p = _resolve(project_root, raw)
                if p is None or not p.is_file():
                    fail(f"{role}_missing", f"visual_evidence.{role} missing: {raw!r}")
                else:
                    ev_paths[role] = p
            if len(ev_paths) == 5:
                distinct = {str(p) for p in ev_paths.values()}
                if len(distinct) < 5:
                    fail("visual_evidence_not_distinct",
                         f"only {len(distinct)} distinct path(s) for 5 evidence roles")
                    # Distinct paths are necessary but not sufficient; content must differ.
                else:
                    _recheck_visual_evidence(ev_paths, nc, native_path, candidate_sha, fail, warn)

            if ve.get("candidate_sha256") != candidate_sha:
                fail("candidate_hash_not_bound",
                     "visual_evidence.candidate_sha256 does not match candidate on disk")

            # Assisted/mechanical translation from raster source must prove the
            # matte operation instead of presenting threshold residue as alpha.
            if nc.get("method") in ("assisted_native_translation", "mechanical_scale_probe"):
                matte_path = _resolve(project_root, nc.get("foreground_matte_report", ""))
                if matte_path is None or not matte_path.is_file():
                    fail("foreground_matte_report_missing",
                         "assisted/mechanical translation requires a bound foreground matte report")
                else:
                    try:
                        matte = json.loads(matte_path.read_text(encoding="utf-8"))
                        source_path = _resolve(project_root, matte.get("input_source_path", ""))
                        if matte.get("tool") != "forge_art.foreground_matte" \
                                or matte.get("method") != "border_connected_color_flood_v1" \
                                or matte.get("status") != "passed" \
                                or matte.get("blocking_statuses"):
                            fail("foreground_matte_report_invalid",
                                 "matte report must be a clean border-connected foreground_matte pass")
                        if source_path is None or not source_path.is_file() \
                                or matte.get("input_source_sha256") != _sha256_file(source_path):
                            fail("foreground_matte_source_unbound",
                                 "matte report input source path/hash does not match disk")
                    except (OSError, json.JSONDecodeError):
                        fail("foreground_matte_report_invalid",
                             "foreground matte report is unreadable or invalid JSON")

    # --- gates: independence + required-gate gating of promotion ---
    visual = _gate_status(gates, "native_visual")
    scale = _gate_status(gates, "scale")
    budget = _gate_status(gates, "budget")
    human = _gate_status(gates, "human")
    pixel = _gate_status(gates, "pixel_contract")

    # A binary lineart must not claim palette_lock passed.
    if _gate_status(gates, "palette_lock") == "passed":
        mat_roles = rec.get("palette_contract", {}).get("material_roles") or []
        if mat_roles == ["lineart_control_only"]:
            fail("palette_lock_on_binary_lineart",
                 "palette_lock=passed but only 'lineart_control_only' material exists "
                 "(binary lineart has no palette to lock)")

    # scale=passed requires scale_report.status=passed AND probe measurements.
    sr = rec.get("scale_report") or {}
    if scale == "passed":
        if sr.get("status") != "passed":
            fail("scale_pass_without_report",
                 "gate.scale=passed but scale_report.status != passed (got "
                 f"{sr.get('status')!r}); scale gate must stay independent of visual")
        probes = rec.get("scale_contract", {}).get("probes") or []
        if not probes:
            fail("scale_pass_without_probes",
                 "gate.scale=passed but no probe measurements (48x64 / 64x96) present")

    # budget=passed requires a real VDP report bound to the candidate.
    if budget == "passed" and not rec.get("budget_report"):
        fail("budget_pass_without_report",
             "gate.budget=passed but budget_report (VDP/scanline/VRAM) is missing")

    # visual=passed requires a visual report and candidate hash binding.
    if visual == "passed" and not rec.get("visual_report"):
        fail("visual_pass_without_report",
             "gate.native_visual=passed but visual_report is missing")
    if visual == "passed" and not rec.get("native_candidate"):
        fail("visual_pass_without_candidate",
             "gate.native_visual=passed but no native_candidate exists")

    # Mandatory gates must never be marked not_applicable for a critical character.
    for g in MANDATORY_GATES:
        if _gate_status(gates, g) == "not_applicable":
            fail(f"{g}_not_applicable_for_critical",
                 f"critical character: gate.{g} cannot be not_applicable")

    # Scale vs visual independence: a passed scale must not mask a failed visual.
    if scale == "passed" and visual in ("failed", "blocked"):
        warn(f"scale=passed while visual={visual}: the two gates are independent; "
             "scale pass does not advance the visual claim")

    # Challenger must beat the incumbent perceptually AND systemically to substitute.
    if rec.get("challenger_win"):
        cw = rec.get("challenger_win", {})
        if not (cw.get("perceptual_win") and cw.get("system_win")):
            fail("challenger_not_justified",
                 "challenger replaces incumbent only with perceptual_win AND system_win")

    # Promotion requires ALL applicable gates green.
    required_for_promotion = {
        "pixel_contract": pixel, "native_visual": visual, "scale": scale,
        "budget": budget, "human": human,
    }
    if rec.get("schema_version") == "1.4.0" or "material_topology" in gates:
        required_for_promotion["material_topology"] = _gate_status(gates, "material_topology")
    pending = [g for g, s in required_for_promotion.items() if s not in ("passed", "not_applicable")]
    if promotable:
        if pending:
            fail("promotion_with_pending_gates",
                 f"promotable=true but gates pending/failed: {pending}")
        if promotion_target == "res" and "ready_for_res" != rec.get("status"):
            fail("promotion_target_res_without_status",
                 "promotion.target=res but record.status is not ready_for_res")

    # --- incumbent + methodology reference must exist, no pixel-source role ---
    # Both are REQUIRED in the native-spring flow for a critical character.
    inc = rec.get("incumbent")
    if inc is None:
        fail("incumbent_missing", "incumbent is required (best accepted route, comparison_only)")
    elif isinstance(inc, dict):
        inc_path = _resolve(project_root, inc.get("path", ""))
        if inc_path is None or not inc_path.is_file():
            fail("incumbent_missing", f"incumbent.path not found: {inc.get('path')}")
        else:
            if inc.get("role") == "pixel_source":
                fail("incumbent_as_pixel_source",
                     "incumbent must be comparison_only, never a pixel generation source")
            if inc.get("sha256") and _sha256_file(inc_path) != inc.get("sha256"):
                fail("incumbent_hash_mismatch", "incumbent sha256 mismatch")

    meth = rec.get("methodology_reference")
    if meth is None:
        fail("methodology_reference_missing", "methodology_reference is required")
    elif isinstance(meth, dict):
        meth_path = _resolve(project_root, meth.get("path", ""))
        if meth_path is None or not meth_path.is_file():
            fail("methodology_reference_missing", f"methodology_reference.path not found: {meth.get('path')}")
        else:
            if meth.get("role") not in ("methodology_reference", "comparison_only", "quality_reference_only"):
                fail("methodology_reference_role_invalid",
                     "methodology_reference must be comparison/quality_reference_only")

    # --- shape-block contract (required before lineart for a NEW candidate) ---
    sb_required = require_shape_block_contract or isinstance(nc, dict) or rec.get("status") in {
        "native_authoring", "technical_candidate", "rework",
        "ready_for_animation", "ready_for_res",
    }
    sb = nc.get("shape_block_contract") if isinstance(nc, dict) else None
    if sb_required:
        if not isinstance(sb, dict):
            fail("shape_block_contract_missing",
                 "shape_block_contract required before lineart: silhouette_mask, "
                 "semantic_region_map, contour_overlay and the 8 semantic regions")
        else:
            shape_paths: dict[str, Path] = {}
            for k in ("silhouette_mask", "semantic_region_map", "contour_overlay"):
                artifact = sb.get(k)
                raw = artifact.get("path") if isinstance(artifact, dict) else artifact
                path = _resolve(project_root, raw)
                if not path or not path.is_file():
                    fail(f"shape_block_{k}_missing", f"shape_block_contract.{k} missing: {raw!r}")
                    continue
                shape_paths[k] = path
                # high-res measurement masks do NOT satisfy native shape block.
                from PIL import Image
                try:
                    with Image.open(path) as im:
                        if im.size[0] != nc.get("width") or im.size[1] != nc.get("height"):
                            fail(f"shape_block_{k}_dimension_mismatch",
                                 f"shape_block_contract.{k} {im.size} != candidate "
                                 f"{nc.get('width')}x{nc.get('height')} (must be native grid)")
                    if not isinstance(artifact, dict):
                        fail(f"shape_block_{k}_link_missing",
                             f"shape_block_contract.{k} must include path, sha256, asset_id, scale and source")
                    else:
                        if artifact.get("sha256") != _sha256_file(path):
                            fail(f"shape_block_{k}_hash_mismatch",
                                 f"shape_block_contract.{k}.sha256 does not match artifact bytes")
                        expected_scale = f"{nc.get('width')}x{nc.get('height')}"
                        if artifact.get("asset_id") != rec.get("asset_id"):
                            fail(f"shape_block_{k}_asset_id_mismatch",
                                 f"shape artifact asset_id {artifact.get('asset_id')!r} != record asset_id")
                        if artifact.get("scale") != expected_scale:
                            fail(f"shape_block_{k}_scale_mismatch",
                                 f"shape artifact scale {artifact.get('scale')!r} != {expected_scale}")
                        if _resolve(project_root, artifact.get("source", "")) != native_path:
                            fail(f"shape_block_{k}_source_mismatch",
                                 "shape artifact source must resolve to the candidate PNG")
                except OSError:
                    fail(f"shape_block_{k}_unreadable", f"shape_block_contract.{k} unreadable")
            if len(shape_paths) == 3 and len({str(p) for p in shape_paths.values()}) < 3:
                fail("shape_block_artifacts_not_distinct",
                     "silhouette_mask, semantic_region_map and contour_overlay must be "
                     "three distinct artifacts; one mask cannot prove three roles")
            regions = set(sb.get("required_semantic_regions", [])) if isinstance(sb, dict) else set()
            missing = REQUIRED_REGIONS - regions
            if missing:
                fail("semantic_regions_incomplete",
                     f"missing required semantic regions: {sorted(missing)}")
            if sb.get("occupancy_metrics") is None or sb.get("bbox") is None:
                fail("shape_block_metrics_missing",
                     "shape_block_contract requires occupancy_metrics and bbox measurements")
            occ = sb.get("occupancy_metrics") or {}
            if occ.get("filled_pixels") and occ.get("canvas_pixels") \
                    and occ["filled_pixels"] == occ["canvas_pixels"]:
                fail("canvas_confused_with_visible",
                     "shape_block occupancy_metrics reports filled == canvas; transparency "
                     "was not excluded (a real silhouette is never the full canvas)")
            if native_path and "metrics" in locals():
                expected_metrics = {
                    "filled_pixels": metrics["filled_pixels"],
                    "canvas_pixels": metrics["canvas_pixels"],
                    "occupancy_pct": metrics["occupancy_pct"],
                }
                for key, expected in expected_metrics.items():
                    if occ.get(key) != expected:
                        fail("shape_block_occupancy_mismatch",
                             f"shape_block occupancy {key}={occ.get(key)!r} != candidate {expected!r}")
                if sb.get("bbox") != metrics["bbox"]:
                    fail("shape_block_bbox_mismatch",
                         f"shape_block bbox {sb.get('bbox')!r} != candidate {metrics['bbox']!r}")
            if native_path and "metrics" in locals() and len(shape_paths) == 3:
                try:
                    candidate_mask = _visible_mask(native_path)
                    with Image.open(shape_paths["silhouette_mask"]) as sil_img:
                        sil_pixels = list(sil_img.convert("P").tobytes())
                    with Image.open(shape_paths["semantic_region_map"]) as sem_img:
                        sem_pixels = list(sem_img.convert("P").tobytes())
                    with Image.open(shape_paths["contour_overlay"]) as con_img:
                        con_pixels = list(con_img.convert("P").tobytes())
                    silhouette_mask = [value != 0 for value in sil_pixels]
                    semantic_mask = [value != 0 for value in sem_pixels]
                    contour_mask = [value != 0 for value in con_pixels]
                    if set(sil_pixels) - {0, 1}:
                        fail("silhouette_mask_not_binary",
                             "silhouette_mask must contain only labels 0 and 1")
                    if silhouette_mask != candidate_mask:
                        fail("silhouette_candidate_mismatch",
                             "silhouette_mask visibility differs from candidate alpha/index-0 mask")
                    if semantic_mask != candidate_mask:
                        fail("semantic_union_candidate_mismatch",
                             "semantic-region union differs from candidate visibility mask")
                    if contour_mask != candidate_mask:
                        fail("contour_union_candidate_mismatch",
                             "contour overlay union differs from candidate visibility mask")
                    expected_boundary = _boundary_mask(candidate_mask, metrics["width"], metrics["height"])
                    actual_boundary = [value == 1 for value in con_pixels]
                    actual_interior = [value == 2 for value in con_pixels]
                    if set(con_pixels) - {0, 1, 2} or actual_boundary != expected_boundary \
                            or any(actual_interior[i] != (candidate_mask[i] and not expected_boundary[i])
                                   for i in range(len(candidate_mask))):
                        fail("contour_overlay_not_derived",
                             "contour labels must be 1 on the 4-neighbor boundary and 2 in the interior")

                    bbox = metrics.get("bbox")
                    if bbox:
                        bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                        solidity = metrics["filled_pixels"] / bbox_area if bbox_area else 0.0
                        if solidity >= 0.98:
                            fail("silhouette_rectangular_matte",
                                 f"silhouette fills {solidity:.3f} of its bbox; likely unremoved matte/rectangle")
                    legend = sb.get("semantic_label_legend") or {}
                    counts = sb.get("semantic_label_counts") or {}
                    expected_values = {int(v) for v in legend.values()}
                    actual_counts = {name: sem_pixels.count(int(value))
                                     for name, value in legend.items()}
                    if set(legend) != REQUIRED_REGIONS or expected_values != set(range(1, 9)):
                        fail("semantic_label_legend_invalid",
                             "semantic_label_legend must map the 8 required regions to labels 1..8")
                    if any(v <= 0 for v in actual_counts.values()):
                        fail("semantic_labels_missing_on_disk",
                             f"semantic_region_map has empty labels: {actual_counts}")
                    major = {"head_or_face", "hair", "torso", "arms_or_guard", "legs"}
                    too_small = {}
                    for name, count in actual_counts.items():
                        ratio = 0.005 if name in major else 0.002
                        floor = max(3 if name in major else 2,
                                    int(metrics["filled_pixels"] * ratio + 0.999))
                        if count < floor:
                            too_small[name] = {"pixels": count, "minimum": floor}
                    if too_small:
                        fail("semantic_labels_tokenized_not_meaningful",
                             f"semantic labels are token pixels, not regions: {too_small}")
                    if counts != actual_counts:
                        fail("semantic_label_counts_mismatch",
                             f"declared semantic_label_counts {counts} != re-derived {actual_counts}")
                    invalid = set(sem_pixels) - {0} - expected_values
                    if invalid:
                        fail("semantic_region_map_invalid_labels",
                             f"semantic_region_map contains undeclared labels {sorted(invalid)}")
                except OSError:
                    fail("semantic_region_map_unreadable", "semantic_region_map could not be read")

    if isinstance(nc, dict) and native_path is not None and "metrics" in locals():
        _validate_material_region_contract(project_root, rec, nc, native_path,
                                           metrics, fail, warn)

    status = "passed" if not errors else "failed"
    return {
        "status": status,
        "promotable": promotable and not errors,
        "errors": errors,
        "warnings": warnings,
        "asset_id": rec.get("asset_id"),
        "record_status": rec.get("status"),
        "gates": gates,
        "verb": "semantic_gate",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=None,
                        help="Absolute path to the project root (required for safe resolution)")
    parser.add_argument("--record", type=Path, default=None,
                        help="Path to native_sprite_production_record.json")
    parser.add_argument("--shape-block-contract", action="store_true",
                        help="Require the full native shape-block contract (silhouette/semantic/contour)")
    # Positional record kept for backward compatibility.
    parser.add_argument("record_pos", nargs="?", type=Path, default=None,
                        help="(compat) positional path to the record")
    args = parser.parse_args(argv)

    record_path = args.record or args.record_pos
    if record_path is None:
        parser.error("provide --record <path> or a positional <path>")

    project_root = args.project_root
    if project_root is None:
        # Infer the project root by walking up from the record to a structural
        # marker (src/, .mddev, or doc/). Resolve and require existence.
        guess = record_path.resolve()
        for _ in range(12):
            if (guess / "src").is_dir() or (guess / ".mddev").exists() or (guess / "doc").is_dir():
                break
            guess = guess.parent
        project_root = guess
    project_root = project_root.resolve()

    result = validate_record(project_root, record_path,
                             require_shape_block_contract=args.shape_block_contract)
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
