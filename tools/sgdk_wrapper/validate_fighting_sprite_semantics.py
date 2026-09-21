#!/usr/bin/env python3
"""Fail-closed semantic and scale guard for full-body fighting sprites.

This gate prevents portraits/icons from defining fighter scale, re-derives the
GDD scale formula from real visible bounding boxes, classifies textual pixel
matrices as procedural probes, and rejects duplicate project identities before
visual production starts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from forge_art.schema_gate import SchemaError, validate as validate_schema_document


VERSION = "1.0.0"
SCHEMA_VERSION = "1.0.0"
SCALE_ROLE = "fighter_full_body_frame_or_strip"
TEXTUAL_SUFFIXES = {".xpm"}


class GuardError(ValueError):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def resolve_local(project_root: Path, raw: str) -> Path:
    candidate = (project_root / raw).resolve()
    if not inside(project_root, candidate):
        raise GuardError(f"path_outside_project:{raw}")
    return candidate


def normalized_project_identity(name: str) -> str:
    without_tags = re.sub(r"\[[^\]]+\]", " ", name)
    return re.sub(r"[^a-z0-9]+", "", without_tags.lower())


def duplicate_project_roots(project_root: Path) -> list[str]:
    identity = normalized_project_identity(project_root.name)
    if not identity or not project_root.parent.is_dir():
        return []
    return sorted(
        sibling.name
        for sibling in project_root.parent.iterdir()
        if sibling.is_dir()
        and sibling.resolve() != project_root.resolve()
        and normalized_project_identity(sibling.name) == identity
    )


def visible_mask(image: Image.Image) -> list[bool]:
    if image.mode == "P":
        # Mega Drive sprite contracts reserve index 0 for transparency even
        # when a legacy PNG omitted a tRNS chunk.
        return [value != 0 for value in image.getdata()]
    rgba = image.convert("RGBA")
    if image.mode in {"RGBA", "LA"} or "transparency" in image.info:
        return [pixel[3] != 0 for pixel in rgba.getdata()]
    # Reference-only RGB sheets often use a flat corner matte. This fallback
    # is measurable but never upgrades the source to native pixel authorship.
    corner = rgba.getpixel((0, 0))[:3]
    return [pixel[:3] != corner for pixel in rgba.getdata()]


def max_visible_height_by_cell(path: Path, cell_width: int, cell_height: int) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
        if width % cell_width or height % cell_height:
            raise GuardError(
                f"reference_cell_grid_mismatch:{path.name}:{width}x{height}:{cell_width}x{cell_height}"
            )
        mask = visible_mask(image)
    heights: list[int] = []
    columns = width // cell_width
    rows = height // cell_height
    for cell_y in range(rows):
        for cell_x in range(columns):
            ys: list[int] = []
            x0 = cell_x * cell_width
            y0 = cell_y * cell_height
            for local_y in range(cell_height):
                base = (y0 + local_y) * width + x0
                if any(mask[base + local_x] for local_x in range(cell_width)):
                    ys.append(local_y)
            heights.append(max(ys) - min(ys) + 1 if ys else 0)
    return {
        "image_size": [width, height],
        "cell_size": [cell_width, cell_height],
        "frame_count": columns * rows,
        "visible_heights": heights,
        "max_visible_height": max(heights, default=0),
    }


def candidate_metrics(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        width, height = image.size
        mask = visible_mask(image)
    coords = [(index % width, index // width) for index, visible in enumerate(mask) if visible]
    bbox = None
    if coords:
        xs = [x for x, _ in coords]
        ys = [y for _, y in coords]
        bbox = [min(xs), min(ys), max(xs) + 1, max(ys) + 1]
    return {
        "image_size": [width, height],
        "visible_bbox": bbox,
        "visible_height": 0 if bbox is None else bbox[3] - bbox[1],
        "visible_pixel_count": len(coords),
    }


def expected_gdd_formula_marker(rule_id: str, multiplier: int | float) -> str:
    normalized_multiplier = format(multiplier, "g")
    return (
        f"{rule_id}:minimum_visible_height="
        f"ceil({normalized_multiplier}*max(full_body_reference_visible_height))"
    )


def validate_schema(contract: dict[str, Any], schema_path: Path) -> list[str]:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        validate_schema_document(contract, schema)
        return []
    except (OSError, json.JSONDecodeError, SchemaError) as exc:
        return [f"contract_schema_invalid:{exc}"]


def validate_contract(project_root: Path, contract_path: Path) -> dict[str, Any]:
    project_root = project_root.resolve()
    blockers: list[str] = []
    warnings: list[str] = []
    measurements: dict[str, Any] = {"references": []}
    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "failed", "blockers": [f"contract_invalid_json:{exc}"], "warnings": []}

    schema_path = Path(__file__).resolve().parent / "schemas/fighting_sprite_semantic_contract.schema.json"
    blockers.extend(validate_schema(contract, schema_path))
    if blockers:
        return {"status": "failed", "blockers": blockers, "warnings": warnings}

    expected_name = contract["project_identity"]["canonical_directory_name"]
    if project_root.name != expected_name:
        blockers.append("canonical_project_directory_mismatch")
    duplicates = duplicate_project_roots(project_root)
    if duplicates:
        blockers.append("duplicate_project_identity_detected")

    source_by_path = {item["path"]: item for item in contract["source_assets"]}
    for item in contract["source_assets"]:
        raw = item["path"]
        try:
            path = resolve_local(project_root, raw)
        except GuardError as exc:
            blockers.append(str(exc))
            continue
        if not path.is_file():
            blockers.append(f"source_missing:{raw}")
            continue
        if sha256_file(path) != item["sha256"]:
            blockers.append(f"source_hash_mismatch:{raw}")
        textual = path.suffix.lower() in TEXTUAL_SUFFIXES
        if textual and (
            item["classification"] != "procedural_code_probe"
            or item["allowed_use"] != "diagnostic_only"
            or item["promotable"] is not False
        ):
            blockers.append(f"textual_pixel_matrix_requires_procedural_code_probe:{raw}")
        if item["semantic_role"] in {"portrait", "icon", "hud_icon"} and item["allowed_use"] == "scale_reference":
            blockers.append(f"portrait_or_icon_used_as_fighter_scale_reference:{raw}")
        if item["semantic_role"] in {"mechanical_underlay", "diagnostic_map"} and item["allowed_use"] in {
            "identity_authority", "visual_translation", "scale_reference"
        }:
            blockers.append(f"derived_artifact_promoted_to_production_source:{raw}")

    scale_rule = contract["scale_rule"]
    gdd_binding = scale_rule["gdd_binding"]
    expected_marker = expected_gdd_formula_marker(
        gdd_binding["rule_id"], scale_rule["multiplier"]
    )
    measurements["gdd_scale_formula_marker"] = expected_marker
    try:
        gdd_path = resolve_local(project_root, gdd_binding["path"])
    except GuardError as exc:
        blockers.append(str(exc))
    else:
        if not gdd_path.is_file():
            blockers.append("gdd_scale_source_missing")
        else:
            if sha256_file(gdd_path) != gdd_binding["sha256"]:
                blockers.append("gdd_scale_source_hash_mismatch")
            if gdd_binding["formula_marker"] != expected_marker:
                blockers.append("gdd_scale_formula_contract_mismatch")
            if gdd_binding["formula_marker"] not in gdd_path.read_text(encoding="utf-8-sig"):
                blockers.append("gdd_scale_formula_marker_missing")

    reference_maxima: list[int] = []
    for reference in contract["scale_rule"]["references"]:
        raw = reference["path"]
        source = source_by_path.get(raw)
        if source is None:
            blockers.append(f"scale_reference_not_declared_as_source:{raw}")
            continue
        if reference["semantic_role"] != SCALE_ROLE or source["semantic_role"] != SCALE_ROLE:
            blockers.append(f"invalid_fighter_scale_reference_role:{raw}")
            continue
        if source["allowed_use"] != "scale_reference":
            blockers.append(f"scale_reference_use_not_authorized:{raw}")
        try:
            path = resolve_local(project_root, raw)
        except GuardError as exc:
            blockers.append(str(exc))
            continue
        if not path.is_file():
            blockers.append(f"scale_reference_missing:{raw}")
            continue
        if sha256_file(path) != reference["sha256"] or source["sha256"] != reference["sha256"]:
            blockers.append(f"scale_reference_hash_mismatch:{raw}")
            continue
        try:
            metrics = max_visible_height_by_cell(path, reference["cell_width"], reference["cell_height"])
        except (OSError, GuardError) as exc:
            blockers.append(str(exc))
            continue
        metrics["path"] = raw
        measurements["references"].append(metrics)
        reference_maxima.append(metrics["max_visible_height"])

    computed_minimum = None
    if reference_maxima:
        computed_minimum = math.ceil(scale_rule["multiplier"] * max(reference_maxima))
        measurements["computed_minimum_visible_height_px"] = computed_minimum
        if computed_minimum != contract["scale_rule"]["declared_minimum_visible_height_px"]:
            blockers.append("declared_scale_formula_result_mismatch")

    candidate = contract["candidate"]
    if candidate is not None:
        raw = candidate["path"]
        try:
            path = resolve_local(project_root, raw)
        except GuardError as exc:
            blockers.append(str(exc))
        else:
            if not path.is_file():
                blockers.append(f"candidate_missing:{raw}")
            else:
                if sha256_file(path) != candidate["sha256"]:
                    blockers.append("candidate_hash_mismatch")
                try:
                    metrics = candidate_metrics(path)
                    measurements["candidate"] = metrics
                    if metrics["image_size"] != [candidate["declared_width"], candidate["declared_height"]]:
                        blockers.append("candidate_declared_dimensions_mismatch")
                    if computed_minimum is not None and metrics["visible_height"] < computed_minimum:
                        blockers.append("fighting_full_body_sprite_below_gdd_scale")
                except OSError as exc:
                    blockers.append(f"candidate_open_failed:{exc}")
    else:
        warnings.append("candidate_pending_preproduction_guard_only")

    return {
        "schema_version": SCHEMA_VERSION,
        "artifact_kind": "fighting_sprite_semantic_guard_report",
        "tool": {"name": "validate_fighting_sprite_semantics", "version": VERSION},
        "asset_id": contract["asset_id"],
        "profile": contract["profile"],
        "status": "passed" if not blockers else "failed",
        "blockers": sorted(set(blockers)),
        "warnings": warnings,
        "duplicate_project_roots": duplicates,
        "measurements": measurements,
        "claim_ceiling": "semantic_scale_gate_only",
    }


def self_check() -> dict[str, Any]:
    # Full physical fixtures live in ci/test_fighting_sprite_semantic_guard.py.
    checks = {
        "normalizes_repeated_tags": normalized_project_identity(
            "GAME [VER.001] [SGDK 211] [SGDK 211] [GEN] [GAME] [FIGHTING]"
        ) == "game",
        "distinguishes_titles": normalized_project_identity("GAME A [GEN]") != normalized_project_identity("GAME B [GEN]"),
    }
    with tempfile.TemporaryDirectory(prefix="fighting_identity_self_check_") as raw:
        projects = Path(raw) / "SGDK_projects"
        canonical = projects / "FIGHTER [VER.001] [SGDK 211] [GEN] [GAME] [FIGHTING]"
        duplicate = projects / "FIGHTER [VER.001] [SGDK 211] [SGDK 211] [GEN] [GAME] [FIGHTING]"
        canonical.mkdir(parents=True)
        duplicate.mkdir()
        checks["detects_duplicate_identity_negative_fixture"] = duplicate_project_roots(canonical) == [duplicate.name]
    failed = [name for name, passed in checks.items() if not passed]
    return {"status": "passed" if not failed else "failed", "passed": len(checks) - len(failed), "total": len(checks), "failed": failed}


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate")
    validate.add_argument("--project-root", type=Path, required=True)
    validate.add_argument("--contract", type=Path, required=True)
    sub.add_parser("self-check")
    return root


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv == ["--self-check"]:
        argv = ["self-check"]
    args = parser().parse_args(argv)
    if args.command == "self-check":
        result = self_check()
    else:
        result = validate_contract(args.project_root, args.contract)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
