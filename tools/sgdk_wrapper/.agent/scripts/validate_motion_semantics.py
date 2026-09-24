#!/usr/bin/env python3
"""Measure whether an animation strip behaves like its declared motion profile."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from animation_validation_common import (
    bbox, centroid, changed_ratio, crop_mask, image_mask, integer_replication_factor,
    load_object, mask_hash, resolve_inside, sha256_file, validate_approval_record,
    validate_canonical_schema, validate_production_provenance,
)


TOOL_VERSION = "1.2.0"
DEFAULT_REGISTRY = Path(__file__).resolve().parents[1] / "skills" / "art" / "sprite-animation" / "references" / "motion_profile_registry.json"
CANONICAL_REGISTRY_REL = "tools/sgdk_wrapper/.agent/skills/art/sprite-animation/references/motion_profile_registry.json"

NATIVE_LINEART_AUTHORSHIP = {"hand_authored_native", "assisted_native_reauthored"}
PROCEDURAL_LINEART_DERIVATIONS = {"procedural_contour_extraction", "mask_boundary_trace", "hardcoded_spans"}


def _validate_native_lineart_lineage(
    contract: dict[str, Any], project_root: Path, strip_sha256: str, blockers: list[str]
) -> None:
    lineage = contract.get("state_lineart_lineage")
    if not isinstance(lineage, dict) or lineage.get("lineart_role") != "native_key_pose_lineart":
        blockers.append("native_lineart_lineage_missing")
        return
    authorship = lineage.get("authorship_method")
    derivation = lineage.get("derivation_method")
    if authorship not in NATIVE_LINEART_AUTHORSHIP:
        blockers.append(
            "procedural_contour_declared_native_lineart"
            if authorship == "procedural_contour_probe" or derivation in PROCEDURAL_LINEART_DERIVATIONS
            else "native_lineart_authorship_unproven"
        )
    if derivation in PROCEDURAL_LINEART_DERIVATIONS:
        blockers.append("procedural_contour_declared_native_lineart")
    approval = lineage.get("approval_record")
    if not isinstance(approval, dict):
        blockers.append("native_lineart_approval_unbound")
        return
    try:
        approval_path = resolve_inside(project_root, approval.get("path", ""))
    except ValueError:
        blockers.append("native_lineart_approval_unbound")
        return
    blockers.extend(validate_approval_record(
        project_root, approval, {str(lineage.get("source_sha256", "")), strip_sha256}
    ))


def _contact_matches_artifact(mask: list[list[bool]], x: int, y: int) -> bool:
    if not mask or not mask[0] or x < 0 or y < 0 or x >= len(mask[0]) or y >= len(mask):
        return False
    visible_here = mask[y][x] or (y > 0 and mask[y - 1][x])
    visible_below = any(mask[row][x] for row in range(min(y + 1, len(mask)), len(mask)))
    return visible_here and not visible_below


def _registry_binding(registry_path: Path | None) -> dict[str, Any]:
    path = (registry_path or DEFAULT_REGISTRY).resolve()
    return {
        "path": CANONICAL_REGISTRY_REL,
        "sha256": sha256_file(path) if path.is_file() else None,
        "schema_version": "1.0.0",
        "is_canonical": path == DEFAULT_REGISTRY.resolve(),
    }


def validate(
    contract: dict[str, Any], project_root: Path, registry: dict[str, Any], registry_path: Path | None = None
) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []
    registry_binding = _registry_binding(registry_path)
    if registry_path is not None and registry_path.resolve() != DEFAULT_REGISTRY.resolve():
        blockers.append("noncanonical_motion_profile")
    try:
        schema_major = int(str(contract.get("schema_version", "0")).split(".", 1)[0])
    except ValueError:
        schema_major = 0
    if schema_major >= 3:
        schema_errors = validate_canonical_schema(contract, "animation_strip_contract")
        if schema_errors:
            blockers.append("animation_strip_schema_invalid")
    profile_id = contract.get("motion_profile_id")
    profile = registry.get("profiles", {}).get(profile_id)
    if not isinstance(profile, dict):
        return {
            "tool_name": "validate_motion_semantics",
            "tool_version": TOOL_VERSION,
            "status": "error",
            "blockers": ["noncanonical_motion_profile"],
            "warnings": [],
            "registry": registry_binding,
            "metrics": {},
        }
    artifact = contract.get("artifact")
    if not isinstance(artifact, dict):
        return {"status": "error", "blockers": ["strip_artifact_binding_missing"], "warnings": [], "metrics": {}}
    try:
        strip_path = resolve_inside(project_root, artifact.get("path", ""))
    except ValueError:
        return {"status": "error", "blockers": ["strip_artifact_path_invalid"], "warnings": [], "metrics": {}}
    if not strip_path.is_file() or sha256_file(strip_path) != artifact.get("sha256"):
        return {"status": "error", "blockers": ["strip_artifact_sha_mismatch"], "warnings": [], "metrics": {}}

    frames = contract.get("frames", [])
    replication_factors: list[int] = []
    with Image.open(strip_path) as image:
        image.load()
        mask = image_mask(image, int(artifact.get("transparent_index", 0)))
        frame_images = [image.crop((int(frame["x"]), int(frame["y"]), int(frame["x"]) + int(frame["w"]), int(frame["y"]) + int(frame["h"]))) for frame in frames]
        pixel_hashes = [hashlib.sha256(frame.convert("RGBA").tobytes()).hexdigest() for frame in frame_images]
        replication_factors = [integer_replication_factor(frame) for frame in frame_images]
    if replication_factors and all(value > 1 for value in replication_factors):
        blockers.append("native_pixel_integer_scale_masquerade")
    if schema_major >= 3:
        provenance_blockers, _ = validate_production_provenance(
            contract, project_root, str(artifact.get("sha256", ""))
        )
        blockers.extend(provenance_blockers)
    frame_masks: list[list[list[bool]]] = []
    hashes: list[str] = []
    areas: list[int] = []
    centroids: list[list[float] | None] = []
    boxes: list[list[int] | None] = []
    for frame in frames:
        local = crop_mask(mask, int(frame["x"]), int(frame["y"]), int(frame["w"]), int(frame["h"]))
        frame_masks.append(local)
        hashes.append(mask_hash(local))
        areas.append(sum(sum(1 for value in row if value) for row in local))
        centroids.append(centroid(local))
        boxes.append(bbox(local))

    distinct = len(set(hashes))
    if distinct < int(profile["minimum_distinct_frames"]):
        blockers.append("motion_has_too_few_distinct_frames")
    duplicate_groups: dict[str, list[int]] = {}
    for index, value in enumerate(hashes):
        duplicate_groups.setdefault(value, []).append(index)
    duplicate_groups = {key: value for key, value in duplicate_groups.items() if len(value) > 1}
    if duplicate_groups:
        for indexes in duplicate_groups.values():
            declared = all((frames[index].get("lineage") or {}).get("duplicate_role") == "approved_hold" for index in indexes)
            if profile["duplicate_policy"] == "forbid_png_duplicates_use_timing" or not declared:
                blockers.append("undeclared_duplicate_frame")
                break

    if any((frame.get("lineage") or {}).get("transformation") == "source_cell_reorder" for frame in frames):
        blockers.append("action_is_reordered_source_cells")

    authored_frames = [
        frame for frame in frames
        if (frame.get("lineage") or {}).get("transformation") in {"native_reauthored", "authored_inbetween"}
        and (frame.get("lineage") or {}).get("duplicate_role") != "approved_hold"
    ]
    authored_source_ids = [str((frame.get("lineage") or {}).get("source_frame_id", "")) for frame in authored_frames]
    if len(authored_frames) > 1 and len(set(authored_source_ids)) < len(authored_frames):
        blockers.append("single_pose_affine_animation_masquerade")
    if any((frame.get("lineage") or {}).get("transformation") == "mechanical_affine_probe" for frame in frames):
        blockers.append("mechanical_probe_cannot_prove_motion")

    _validate_native_lineart_lineage(contract, project_root, str(artifact.get("sha256", "")), blockers)

    support_positions: dict[str, list[tuple[int, int, int]]] = {}
    grounded_y: list[int] = []
    for index, frame in enumerate(frames):
        support = frame.get("support") or {}
        if support.get("grounded"):
            contacts = support.get("contacts") or []
            if not contacts:
                blockers.append("grounded_frame_without_support_contact")
            measurement_method = support.get("measurement_method")
            if measurement_method in {None, "declared_only"}:
                blockers.append("support_contact_not_artifact_bound")
            evidence = support.get("evidence")
            if measurement_method == "human_annotated_hash_bound":
                if not isinstance(evidence, dict) or evidence.get("subject_sha256") != artifact.get("sha256"):
                    blockers.append("support_contact_not_artifact_bound")
                else:
                    try:
                        evidence_path = resolve_inside(project_root, evidence.get("path", ""))
                    except ValueError:
                        blockers.append("support_contact_not_artifact_bound")
                    else:
                        if not evidence_path.is_file() or sha256_file(evidence_path) != evidence.get("sha256"):
                            blockers.append("support_contact_not_artifact_bound")
            for contact in contacts:
                contact_x, contact_y = int(contact.get("x", 0)), int(contact.get("y", 0))
                if measurement_method == "pixel_derived" and not _contact_matches_artifact(frame_masks[index], contact_x, contact_y):
                    blockers.append("support_contact_not_artifact_bound")
                support_positions.setdefault(str(contact.get("id", "")), []).append((index, contact_x, contact_y))
                grounded_y.append(contact_y)
    for positions in support_positions.values():
        for left, right in zip(positions, positions[1:]):
            if right[0] == left[0] + 1 and max(abs(right[1] - left[1]), abs(right[2] - left[2])) > 1:
                blockers.append("foot_slide_detected")
    if grounded_y and max(grounded_y) - min(grounded_y) > 1:
        blockers.append("pivot_declared_but_support_drifted")

    phases = [str(frame.get("phase", "")) for frame in frames]
    missing_patterns = [pattern for pattern in profile["required_phase_patterns"] if not any(re.search(pattern, phase, re.IGNORECASE) for phase in phases)]
    if missing_patterns:
        blockers.append("motion_profile_mismatch")

    same_dimensions = all(len(frame_masks[i]) == len(frame_masks[0]) and (not frame_masks[i] or len(frame_masks[i][0]) == len(frame_masks[0][0])) for i in range(len(frame_masks))) if frame_masks else True
    if not same_dimensions:
        blockers.append("motion_frame_dimensions_differ")
        adjacent = []
        closure = 0.0
    else:
        adjacent = [changed_ratio(frame_masks[i], frame_masks[i + 1]) for i in range(max(0, len(frame_masks) - 1))]
        closure = changed_ratio(frame_masks[-1], frame_masks[0]) if len(frame_masks) > 1 else 0.0
    min_change = float(profile["minimum_adjacent_change_ratio"])
    max_change = float(profile["maximum_adjacent_change_ratio"])
    if any(value < min_change for value in adjacent):
        blockers.append("adjacent_frame_delta_too_small")
    if any(value > max_change for value in adjacent):
        blockers.append("adjacent_frame_delta_too_large")
    if contract.get("timing_contract", {}).get("loop") and closure > float(profile["maximum_cycle_closure_ratio"]):
        blockers.append("cycle_closure_drift")
    area_range = (max(areas) - min(areas)) / max(1, max(areas)) if areas else 0.0
    if area_range < float(profile.get("minimum_area_range_ratio", 0.0)):
        blockers.append("motion_area_change_below_profile")
    valid_centroids = [value for value in centroids if value is not None]
    centroid_range = 0.0
    if valid_centroids:
        x_range = max(v[0] for v in valid_centroids) - min(v[0] for v in valid_centroids)
        y_range = max(v[1] for v in valid_centroids) - min(v[1] for v in valid_centroids)
        cell_scale = max(1, max(int(frame["w"]) for frame in frames), max(int(frame["h"]) for frame in frames))
        centroid_range = max(x_range, y_range) / cell_scale
        if centroid_range > float(profile.get("maximum_centroid_range_ratio", 1.0)):
            blockers.append("pivot_declared_but_mass_drifted")

    metrics = {
        "motion_profile_id": profile_id,
        "frame_mask_sha256": hashes,
        "frame_pixel_sha256": pixel_hashes,
        "distinct_frame_count": distinct,
        "duplicate_frame_groups": list(duplicate_groups.values()),
        "phases": phases,
        "missing_phase_patterns": missing_patterns,
        "adjacent_changed_ratio": [round(value, 8) for value in adjacent],
        "cycle_closure_ratio": round(closure, 8),
        "visible_area_by_frame": areas,
        "area_range_ratio": round(area_range, 8),
        "centroid_by_frame": centroids,
        "centroid_range_ratio": round(centroid_range, 8),
        "bbox_by_frame": boxes,
        "support_contacts_by_id": {key: value for key, value in support_positions.items()},
        "authored_source_frame_ids": authored_source_ids,
        "integer_replication_factor_by_frame": replication_factors,
        "schema_errors": schema_errors[:32] if schema_major >= 3 else [],
    }
    return {
        "tool_name": "validate_motion_semantics",
        "tool_version": TOOL_VERSION,
        "status": "ok" if not blockers else "error",
        "strip_sha256": artifact.get("sha256"),
        "registry": registry_binding,
        "blockers": sorted(set(blockers)),
        "warnings": warnings,
        "metrics": metrics,
    }


def self_check() -> int:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        image = Image.new("P", (64, 16), 0)
        image.putpalette([0, 0, 0, 255, 255, 255] + [0, 0, 0] * 254)
        draw = ImageDraw.Draw(image)
        for index, offset in enumerate((0, 1, 2, 1)):
            draw.rectangle((index * 16 + 4, 5 - offset, index * 16 + 9 + index, 12), outline=1)
        path = root / "run.png"
        image.save(path, bits=4, transparency=0)
        lineart_path = root / "run_lineart.png"
        image.crop((0, 0, 16, 16)).save(lineart_path, bits=4, transparency=0)
        approval_path = root / "lineart_approval.json"
        approval_path.write_text(json.dumps({"status": "approved", "subject_sha256": sha256_file(lineart_path)}), encoding="utf-8")
        phases = ["contact_left", "passing", "down_compression", "up_flight"]
        contract = {
            "motion_profile_id": "run_cycle",
            "artifact": {"path": "run.png", "sha256": sha256_file(path), "transparent_index": 0},
            "state_lineart_lineage": {
                "action": "run", "lineart_role": "native_key_pose_lineart",
                "source_asset_id": "run_lineart", "source_sha256": sha256_file(lineart_path),
                "source_path": "run_lineart.png", "approval_status": "approved_for_strip_authoring",
                "authorship_method": "hand_authored_native", "derivation_method": "hand_drawn_native",
                "approval_record": {"path": "lineart_approval.json", "sha256": sha256_file(approval_path), "subject_sha256": sha256_file(lineart_path)},
                "key_pose_ids": ["run_0", "run_1", "run_2", "run_3"],
            },
            "timing_contract": {"loop": True},
            "frames": [
                {"index": i, "x": i * 16, "y": 0, "w": 16, "h": 16, "phase": phases[i],
                 "lineage": {"source_frame_id": f"run_{i}", "transformation": "native_reauthored", "duplicate_role": "none"}}
                for i in range(4)
            ],
        }
        for frame in contract["frames"]:
            frame["support"] = {"grounded": True, "measurement_method": "pixel_derived", "contacts": [{"id": "ground", "x": 8, "y": 12}]}
        registry = load_object(DEFAULT_REGISTRY)
        positive = validate(contract, root, registry)
        reordered = json.loads(json.dumps(contract))
        reordered["frames"][1]["lineage"]["transformation"] = "source_cell_reorder"
        negative = validate(reordered, root, registry)
        duplicate = json.loads(json.dumps(contract))
        duplicate["frames"][1]["x"] = duplicate["frames"][0]["x"]
        duplicate_report = validate(duplicate, root, registry)
        sliding = json.loads(json.dumps(contract))
        sliding["frames"][1]["support"]["contacts"][0]["x"] = 12
        sliding_report = validate(sliding, root, registry)
        single_pose = json.loads(json.dumps(contract))
        for frame in single_pose["frames"]:
            frame["lineage"]["source_frame_id"] = "one_pose"
        single_pose_report = validate(single_pose, root, registry)
        procedural_lineart = json.loads(json.dumps(contract))
        procedural_lineart["state_lineart_lineage"]["authorship_method"] = "procedural_contour_probe"
        procedural_lineart["state_lineart_lineage"]["derivation_method"] = "procedural_contour_extraction"
        procedural_lineart_report = validate(procedural_lineart, root, registry)
        declared_contact = json.loads(json.dumps(contract))
        declared_contact["frames"][0]["support"]["measurement_method"] = "declared_only"
        declared_contact_report = validate(declared_contact, root, registry)
        pending_approval = json.loads(json.dumps(contract))
        approval_path.write_text(json.dumps({"status": "pending", "subject_sha256": sha256_file(lineart_path)}), encoding="utf-8")
        pending_approval["state_lineart_lineage"]["approval_record"]["sha256"] = sha256_file(approval_path)
        pending_approval_report = validate(pending_approval, root, registry)
        noncanonical = json.loads(json.dumps(contract))
        noncanonical["motion_profile_id"] = "jump_float"
        noncanonical_report = validate(noncanonical, root, registry)
    if positive["status"] != "ok":
        print(f"self-check failed: positive motion rejected: {positive}", file=sys.stderr)
        return 1
    if "action_is_reordered_source_cells" not in negative["blockers"]:
        print("self-check failed: source-cell reorder passed", file=sys.stderr)
        return 1
    if "undeclared_duplicate_frame" not in duplicate_report["blockers"]:
        print("self-check failed: undeclared duplicate passed", file=sys.stderr)
        return 1
    if "foot_slide_detected" not in sliding_report["blockers"]:
        print("self-check failed: planted support slide passed", file=sys.stderr)
        return 1
    if "single_pose_affine_animation_masquerade" not in single_pose_report["blockers"]:
        print("self-check failed: one source pose passed as native animation", file=sys.stderr)
        return 1
    if "procedural_contour_declared_native_lineart" not in procedural_lineart_report["blockers"]:
        print("self-check failed: procedural contour passed as native lineart", file=sys.stderr)
        return 1
    if "support_contact_not_artifact_bound" not in declared_contact_report["blockers"]:
        print("self-check failed: declared-only support contact passed", file=sys.stderr)
        return 1
    if "native_lineart_approval_status_invalid" not in pending_approval_report["blockers"]:
        print("self-check failed: pending lineart approval passed motion gate", file=sys.stderr)
        return 1
    if noncanonical_report["blockers"] != ["noncanonical_motion_profile"]:
        print("self-check failed: noncanonical motion profile passed", file=sys.stderr)
        return 1
    print("validate_motion_semantics self-check passed (profile, lineage, schema, native scale, approval, support)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--project-root", type=Path)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args(argv)
    if args.self_check:
        return self_check()
    if not args.contract or not args.project_root:
        parser.error("--contract and --project-root are required")
    report = validate(load_object(args.contract), args.project_root.resolve(), load_object(args.registry), args.registry)
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
