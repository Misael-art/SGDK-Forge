#!/usr/bin/env python3
"""Validate one-action Mega Drive animation strip contracts.

Input: JSON matching tools/sgdk_wrapper/schemas/animation_strip_contract.schema.json.
Output: JSON report with status, blockers, warnings, and measured drift.

Contracts 1.x/2.x remain metadata-auditable. Production contracts 3.x are
artifact-bound: this tool opens the PNG and optional preview, rederives frame
content, validates cell boundaries, hashes, lineart lineage, and timing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

from animation_validation_common import (
    boundary_runs,
    crop_mask,
    image_mask,
    integer_replication_factor,
    mask_hash,
    ranges_overlap,
    resolve_inside,
    sha256_file,
    validate_approval_record,
    validate_canonical_schema,
    validate_production_provenance,
)
from validate_lineart_topology import measure as measure_lineart


TOOL_VERSION = "2.1.0"


@dataclass
class StripCheck:
    status: str
    blockers: list[str]
    warnings: list[str]
    metrics: dict[str, Any]


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _frame_pixel_hash(image: Image.Image) -> str:
    rgba = image.convert("RGBA")
    return hashlib.sha256(rgba.tobytes()).hexdigest()


def _allowed_contacts(artifact: dict[str, Any]) -> set[tuple[int, str]]:
    out: set[tuple[int, str]] = set()
    for item in artifact.get("allowed_boundary_contacts", []):
        if isinstance(item, dict) and isinstance(item.get("frame_index"), int) and item.get("edge") in {"left", "right", "top", "bottom"}:
            out.add((item["frame_index"], item["edge"]))
    return out


def _record_declares_mechanical_rasterization(value: Any) -> bool:
    """Detect explicit raster operations in a bound producer record.

    This is provenance enforcement, not a visual-quality judgement. It only
    fires when the record explicitly declares crop/resize/resampling or
    quantization/remapping as an operation.
    """
    mechanical_keys = {"crop", "resize", "resized", "quantization", "quantized", "palette_remap", "remap"}
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = str(key).lower()
            if normalized in {"resampling", "interpolation"} and str(item).lower() in {
                "nearest", "nearest_neighbor", "nearest-neighbor", "bilinear", "bicubic", "lanczos"
            }:
                return True
            if normalized in mechanical_keys and item not in {False, None, "", "none", "not_used"}:
                return True
            if _record_declares_mechanical_rasterization(item):
                return True
    elif isinstance(value, list):
        return any(_record_declares_mechanical_rasterization(item) for item in value)
    return False


def _bound_producer_record(data: dict[str, Any], root: Path) -> dict[str, Any] | None:
    provenance = data.get("production_provenance")
    binding = provenance.get("producer_record") if isinstance(provenance, dict) else None
    if not isinstance(binding, dict):
        return None
    try:
        path = resolve_inside(root, binding.get("path", ""))
    except ValueError:
        return None
    if not path.is_file() or sha256_file(path) != binding.get("sha256"):
        return None
    try:
        value = load_json(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    return value


def _validate_producer_truth(data: dict[str, Any], root: Path, blockers: list[str]) -> None:
    frames = data.get("frames") if isinstance(data.get("frames"), list) else []
    transformations = {
        (frame.get("lineage") or {}).get("transformation")
        for frame in frames if isinstance(frame, dict)
    }
    record = _bound_producer_record(data, root)
    if record is not None and transformations & {"native_reauthored", "authored_inbetween"}:
        if _record_declares_mechanical_rasterization(record):
            blockers.append("mechanical_resize_mislabeled_native")
        lineart = record.get("lineart_source") if isinstance(record, dict) else None
        if isinstance(lineart, dict):
            path = str(lineart.get("path", "")).lower()
            if path.endswith(".svg") or lineart.get("rasterizer"):
                blockers.append("vector_procedural_lineart_declared_native")

    source_hashes = [
        (frame.get("lineage") or {}).get("source_frame_sha256")
        for frame in frames if isinstance(frame, dict)
    ]
    source_ids = [
        (frame.get("lineage") or {}).get("source_frame_id")
        for frame in frames if isinstance(frame, dict)
    ]
    hashes_missing = any(not isinstance(value, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", value) for value in source_hashes)
    if len(frames) > 1 and len(source_ids) == len(set(source_ids)) and (hashes_missing or len(set(source_hashes)) == 1):
        blockers.append("source_frame_lineage_not_independent")


def _validate_source_frame_artifact(
    frame: dict[str, Any], frame_image: Image.Image, position: int, root: Path,
    blockers: list[str], metrics: dict[str, Any]
) -> None:
    """Bind a v3 lineage claim to bytes on disk and rederive its pixels.

    A declared frame id or invented SHA is metadata only.  The source artifact
    must resolve inside the project, its file SHA must match, and the optional
    sheet region (or the whole image) must hash to the strip cell.
    """
    lineage = frame.get("lineage") if isinstance(frame.get("lineage"), dict) else {}
    transformation = lineage.get("transformation")
    if transformation not in {"native_reauthored", "authored_inbetween"}:
        if transformation == "approved_hold":
            approved_id = lineage.get("approved_source_frame_id")
            approved_sha = lineage.get("approved_source_frame_sha256")
            if not isinstance(approved_id, str) or not approved_id or not isinstance(approved_sha, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", approved_sha):
                blockers.append("approved_hold_lineage_unbound")
        return

    binding = lineage.get("source_artifact")
    if not isinstance(binding, dict):
        blockers.append("source_frame_artifact_unbound")
        return
    try:
        source_path = resolve_inside(root, binding.get("path", ""))
    except ValueError:
        blockers.append("source_frame_artifact_unbound")
        return
    if not source_path.is_file():
        blockers.append("source_frame_artifact_unbound")
        return
    actual_file_sha = sha256_file(source_path)
    if actual_file_sha != binding.get("sha256"):
        blockers.append("source_frame_artifact_unbound")
        return
    declared_source_sha = lineage.get("source_frame_sha256")
    if declared_source_sha != actual_file_sha:
        blockers.append("source_frame_lineage_mismatch")
        return

    region = binding.get("region")
    try:
        with Image.open(source_path) as source:
            source.load()
            if region is None:
                crop = source.copy()
            elif isinstance(region, dict):
                x = _as_int(region.get("x"), -1)
                y = _as_int(region.get("y"), -1)
                w = _as_int(region.get("w"), -1)
                h = _as_int(region.get("h"), -1)
                if min(x, y, w, h) < 0 or x + w > source.width or y + h > source.height:
                    blockers.append("source_frame_region_outside")
                    return
                crop = source.crop((x, y, x + w, y + h))
            else:
                blockers.append("source_frame_artifact_unbound")
                return
            source_pixel_sha = _frame_pixel_hash(crop)
    except (OSError, ValueError):
        blockers.append("source_frame_artifact_unbound")
        return

    expected_pixel_sha = binding.get("pixel_sha256")
    if source_pixel_sha != expected_pixel_sha:
        blockers.append("source_frame_pixel_hash_mismatch")
        return
    strip_pixel_sha = _frame_pixel_hash(frame_image)
    if source_pixel_sha != strip_pixel_sha:
        blockers.append("source_frame_pixel_hash_mismatch")
        return
    metrics.setdefault("source_frame_artifacts", []).append({
        "frame_index": position,
        "path": source_path.relative_to(root.resolve()).as_posix(),
        "file_sha256": actual_file_sha,
        "pixel_sha256": source_pixel_sha,
    })


def _validate_approved_hold_lineage(data: dict[str, Any], blockers: list[str]) -> None:
    frames = data.get("frames") if isinstance(data.get("frames"), list) else []
    by_id = {
        (frame.get("lineage") or {}).get("source_frame_id"): frame
        for frame in frames if isinstance(frame, dict) and isinstance(frame.get("lineage"), dict)
    }
    for frame in frames:
        if not isinstance(frame, dict):
            continue
        lineage = frame.get("lineage") if isinstance(frame.get("lineage"), dict) else {}
        if lineage.get("transformation") != "approved_hold" and lineage.get("duplicate_role") != "approved_hold":
            continue
        reference_id = lineage.get("approved_source_frame_id")
        reference_sha = lineage.get("approved_source_frame_sha256")
        referenced = by_id.get(reference_id)
        referenced_sha = (referenced.get("lineage") or {}).get("source_frame_sha256") if isinstance(referenced, dict) else None
        if not isinstance(referenced, dict) or reference_sha != referenced_sha:
            blockers.append("approved_hold_lineage_unbound")


def _validate_artifact(
    data: dict[str, Any], root: Path, blockers: list[str], warnings: list[str], metrics: dict[str, Any]
) -> None:
    artifact = data.get("artifact")
    if not isinstance(artifact, dict):
        blockers.append("strip_artifact_binding_missing")
        return
    try:
        path = resolve_inside(root, artifact.get("path", ""))
    except ValueError as exc:
        blockers.append(f"strip_artifact_path_invalid:{exc}")
        return
    if not path.is_file():
        blockers.append("strip_artifact_missing")
        return
    actual_sha = sha256_file(path)
    _validate_approved_hold_lineage(data, blockers)
    metrics["strip_path"] = path.relative_to(root.resolve()).as_posix()
    metrics["strip_sha256"] = actual_sha
    if actual_sha != artifact.get("sha256"):
        blockers.append("strip_artifact_sha_mismatch")

    transparent_index = _as_int(artifact.get("transparent_index"), 0)
    with Image.open(path) as source:
        source.load()
        if source.mode != "P":
            blockers.append("strip_not_indexed_png")
        frames = data.get("frames", [])
        expected_w = sum(_as_int(frame.get("w"), 0) for frame in frames)
        expected_h = max((_as_int(frame.get("h"), 0) for frame in frames), default=0)
        if source.width != expected_w or source.height != expected_h:
            blockers.append("strip_dimensions_do_not_match_cells")
        full_mask = image_mask(source, transparent_index)
        allowed = _allowed_contacts(artifact)
        frame_masks: list[list[list[bool]]] = []
        frame_pixel_hashes: list[str] = []
        frame_mask_hashes: list[str] = []
        replication_factors: list[int] = []
        for position, frame in enumerate(frames):
            x, y = _as_int(frame.get("x"), -1), _as_int(frame.get("y"), -1)
            w, h = _as_int(frame.get("w"), -1), _as_int(frame.get("h"), -1)
            if min(x, y, w, h) < 0 or x + w > source.width or y + h > source.height:
                blockers.append(f"frame_cell_outside_strip:{position}")
                continue
            local = crop_mask(full_mask, x, y, w, h)
            frame_masks.append(local)
            frame_mask_hashes.append(mask_hash(local))
            local_image = source.crop((x, y, x + w, y + h))
            frame_pixel_hashes.append(_frame_pixel_hash(local_image))
            _validate_source_frame_artifact(frame, local_image, position, root, blockers, metrics)
            replication_factors.append(integer_replication_factor(local_image))
            for edge in ("left", "right", "top", "bottom"):
                if boundary_runs(local, edge) and (position, edge) not in allowed:
                    blockers.append(f"unexpected_frame_boundary_contact:{position}:{edge}")

        for index in range(len(frame_masks) - 1):
            if ranges_overlap(boundary_runs(frame_masks[index], "right"), boundary_runs(frame_masks[index + 1], "left")):
                blockers.append(f"neighbor_cell_fragment_detected:{index}:{index + 1}")
        metrics["frame_pixel_sha256"] = frame_pixel_hashes
        metrics["frame_mask_sha256"] = frame_mask_hashes
        metrics["frame_boundary_policy"] = "coordinate_scoped"
        metrics["integer_replication_factor_by_frame"] = replication_factors
        if replication_factors and all(value > 1 for value in replication_factors):
            blockers.append("native_pixel_integer_scale_masquerade")

    lineage = data.get("state_lineart_lineage")
    if isinstance(lineage, dict):
        try:
            lineart_path = resolve_inside(root, lineage.get("source_path", ""))
        except ValueError:
            blockers.append("state_lineart_path_invalid")
        else:
            if not lineart_path.is_file():
                blockers.append("state_lineart_file_missing")
            else:
                if sha256_file(lineart_path) != lineage.get("source_sha256"):
                    blockers.append("lineart_sha_unbound_to_file")
                topology = measure_lineart(lineart_path, transparent_index)
                metrics["lineart_topology"] = topology["metrics"]
                blockers.extend(code for code in topology["blockers"] if code not in blockers)
        blockers.extend(validate_approval_record(
            root,
            lineage.get("approval_record"),
            {str(lineage.get("source_sha256", "")), actual_sha},
        ))

    provenance_blockers, provenance_metrics = validate_production_provenance(data, root, actual_sha)
    blockers.extend(provenance_blockers)
    metrics["production_provenance"] = provenance_metrics
    _validate_producer_truth(data, root, blockers)

    timing = data.get("timing_contract")
    if not isinstance(timing, dict):
        blockers.append("timing_contract_missing")
    else:
        holds = timing.get("frame_holds_vblank")
        if not isinstance(holds, list) or len(holds) != len(data.get("frames", [])) or any(not isinstance(value, int) or value < 1 for value in holds):
            blockers.append("runtime_timing_contract_mismatch")
        preview = timing.get("preview")
        if isinstance(preview, dict):
            try:
                preview_path = resolve_inside(root, preview.get("path", ""))
            except ValueError:
                blockers.append("preview_timing_unbound")
            else:
                if not preview_path.is_file() or sha256_file(preview_path) != preview.get("sha256"):
                    blockers.append("preview_timing_unbound")
                else:
                    with Image.open(preview_path) as gif:
                        durations_ms: list[int] = []
                        for frame_index in range(getattr(gif, "n_frames", 1)):
                            gif.seek(frame_index)
                            durations_ms.append(int(gif.info.get("duration", 0)))
                    hz = float(timing.get("vblank_hz", 60.0))
                    measured_holds = [max(1, round(ms * hz / 1000.0)) for ms in durations_ms]
                    metrics["preview_frame_holds_vblank"] = measured_holds
                    if measured_holds != holds:
                        blockers.append("gif_delay_contract_mismatch")


def validate_strip(data: dict[str, Any], project_root: Path | None = None) -> StripCheck:
    blockers: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {}

    if data.get("asset_kind") != "animation_strip":
        blockers.append("asset_kind_not_animation_strip")

    if data.get("metadata_only") is True:
        blockers.append("metadata_only_asset_not_approved")

    if data.get("strip_layout") != "horizontal_single_action":
        blockers.append("strip_not_horizontal_single_action")

    action = data.get("action")
    actions = data.get("actions")
    if not isinstance(action, str) or not action.strip():
        blockers.append("missing_single_action")
    if isinstance(actions, list) and len(actions) != 1:
        blockers.append("multi_action_sheet")

    schema_version = str(data.get("schema_version", "0.0.0"))
    try:
        schema_major = int(schema_version.split(".", 1)[0])
    except ValueError:
        schema_major = 0
    if schema_major >= 3:
        schema_errors = validate_canonical_schema(data, "animation_strip_contract")
        if schema_errors:
            blockers.append("animation_strip_schema_invalid")
            metrics["schema_errors"] = schema_errors[:32]
    lineage = data.get("state_lineart_lineage")
    if schema_major >= 2 and not isinstance(lineage, dict):
        blockers.append("state_lineart_lineage_missing")
    elif schema_major < 2 and not isinstance(lineage, dict):
        warnings.append("legacy_contract_without_state_lineart_lineage")
    if isinstance(lineage, dict):
        if lineage.get("action") != action:
            blockers.append("state_lineart_action_mismatch")
        if lineage.get("lineart_role") != "native_key_pose_lineart":
            blockers.append("state_lineart_role_invalid")
        if lineage.get("approval_status") != "approved_for_strip_authoring":
            blockers.append("state_lineart_not_approved_for_strip")
        source_sha = lineage.get("source_sha256")
        if not isinstance(source_sha, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", source_sha):
            blockers.append("state_lineart_sha256_invalid")
        key_pose_ids = lineage.get("key_pose_ids")
        if not isinstance(key_pose_ids, list) or not key_pose_ids:
            blockers.append("state_lineart_key_pose_ids_missing")
        elif len(key_pose_ids) != len(set(key_pose_ids)):
            blockers.append("state_lineart_key_pose_ids_duplicated")

    frames = data.get("frames")
    if not isinstance(frames, list) or not frames:
        blockers.append("missing_frames")
        return StripCheck("error", blockers, warnings, metrics)

    declared_count = _as_int(data.get("frame_count"), -1)
    if declared_count != len(frames):
        blockers.append("frame_count_mismatch")

    thresholds = data.get("drift_thresholds") or {}
    pivot_limit = _as_int(thresholds.get("pivot_px"), 0)
    bbox_limit = _as_int(thresholds.get("bbox_px"), 0)
    palette_change_allowed = bool(thresholds.get("palette_changed_allowed", False))

    first = frames[0]
    base_y = _as_int(first.get("y"))
    base_w = _as_int(first.get("w"))
    base_h = _as_int(first.get("h"))
    base_pivot_x = _as_int(first.get("pivot_x"))
    base_pivot_y = _as_int(first.get("pivot_y"))

    max_pivot_drift = 0
    max_bbox_drift = 0
    last_x = -1
    expected_x = 0
    seen_indexes: set[int] = set()

    for expected_index, frame in enumerate(frames):
        index = _as_int(frame.get("index"), -1)
        x = _as_int(frame.get("x"), -1)
        y = _as_int(frame.get("y"), -1)
        w = _as_int(frame.get("w"), -1)
        h = _as_int(frame.get("h"), -1)
        pivot_x = _as_int(frame.get("pivot_x"), 0)
        pivot_y = _as_int(frame.get("pivot_y"), 0)

        if index in seen_indexes:
            blockers.append(f"duplicate_frame_index:{index}")
        seen_indexes.add(index)

        if index != expected_index:
            warnings.append(f"non_sequential_frame_index:{index}")

        if x <= last_x:
            blockers.append(f"frame_x_not_increasing:{index}")
        last_x = x
        if schema_major >= 3 and (x != expected_x or y != 0):
            blockers.append(f"frame_cell_not_contiguous:{index}")
        expected_x += max(0, w)

        if y != base_y:
            blockers.append(f"frame_y_drift:{index}")

        pivot_drift = max(abs(pivot_x - base_pivot_x), abs(pivot_y - base_pivot_y))
        bbox_drift = max(abs(w - base_w), abs(h - base_h))
        max_pivot_drift = max(max_pivot_drift, pivot_drift)
        max_bbox_drift = max(max_bbox_drift, bbox_drift)

        if not frame.get("phase"):
            blockers.append(f"missing_motion_phase:{index}")
        if schema_major >= 3:
            if "hold_frames" in frame:
                blockers.append(f"duplicate_timing_authority:{index}")
            frame_lineage = frame.get("lineage")
            if not isinstance(frame_lineage, dict):
                blockers.append(f"frame_lineage_missing:{index}")
            elif frame_lineage.get("transformation") == "source_cell_reorder":
                blockers.append("action_is_reordered_source_cells")
            support = frame.get("support")
            if not isinstance(support, dict):
                blockers.append(f"frame_support_contract_missing:{index}")
            elif support.get("grounded") is True and not support.get("contacts"):
                blockers.append(f"grounded_frame_without_support_contact:{index}")

    if max_pivot_drift > pivot_limit:
        blockers.append("pivot_drift_over_threshold")
    if max_bbox_drift > bbox_limit:
        blockers.append("bbox_drift_over_threshold")

    palette_hash = data.get("palette_hash")
    frame_palette_hashes = {
        frame.get("palette_hash")
        for frame in frames
        if isinstance(frame, dict) and frame.get("palette_hash")
    }
    if palette_hash and frame_palette_hashes and frame_palette_hashes != {palette_hash}:
        if palette_change_allowed:
            warnings.append("palette_changed_but_allowed")
        else:
            blockers.append("palette_drift_over_threshold")

    metrics.update(
        {
            "frame_count": len(frames),
            "max_pivot_drift_px": max_pivot_drift,
            "max_bbox_drift_px": max_bbox_drift,
            "horizontal_order": "error" if any(code.startswith("frame_x_not_increasing") or code.startswith("frame_cell_not_contiguous") for code in blockers) else "ok",
        }
    )

    if schema_major >= 3:
        if project_root is None:
            blockers.append("artifact_validation_requires_project_root")
        else:
            _validate_artifact(data, project_root.resolve(), blockers, warnings, metrics)

    return StripCheck("ok" if not blockers else "error", blockers, warnings, metrics)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError("input JSON must be an object")
    return value


def self_check() -> int:
    valid = {
        "schema_version": "2.0.0",
        "asset_id": "hero_idle",
        "asset_kind": "animation_strip",
        "action": "idle",
        "strip_layout": "horizontal_single_action",
        "frame_count": 2,
        "visual_dna_manifest": "visual_dna_manifest.example.json",
        "motion_phase_map": "motion_phase_map.md",
        "state_lineart_lineage": {
            "action": "idle",
            "lineart_role": "native_key_pose_lineart",
            "source_asset_id": "hero_idle_key_pose_lineart",
            "source_sha256": "a" * 64,
            "approval_status": "approved_for_strip_authoring",
            "key_pose_ids": ["idle_low", "idle_high"]
        },
        "pivot_policy": "bottom_center_feet",
        "drift_thresholds": {
            "pivot_px": 0,
            "bbox_px": 0,
            "palette_changed_allowed": False,
            "scale_percent": 0
        },
        "approval_status": "approved_for_sheet",
        "frames": [
            {"index": 0, "x": 0, "y": 0, "w": 32, "h": 48, "pivot_x": 16, "pivot_y": 47, "phase": "hold"},
            {"index": 1, "x": 32, "y": 0, "w": 32, "h": 48, "pivot_x": 16, "pivot_y": 47, "phase": "settle"}
        ]
    }
    invalid = dict(valid)
    invalid["actions"] = ["idle", "run"]
    invalid["metadata_only"] = True
    missing_lineage = dict(valid)
    missing_lineage.pop("state_lineart_lineage")
    wrong_action = dict(valid)
    wrong_action["state_lineart_lineage"] = dict(valid["state_lineart_lineage"])
    wrong_action["state_lineart_lineage"]["action"] = "run"
    legacy = dict(valid)
    legacy["schema_version"] = "1.0.0"
    legacy.pop("state_lineart_lineage")

    valid_report = validate_strip(valid)
    invalid_report = validate_strip(invalid)
    missing_lineage_report = validate_strip(missing_lineage)
    wrong_action_report = validate_strip(wrong_action)
    legacy_report = validate_strip(legacy)
    if valid_report.status != "ok":
        print("self-check failed: valid sample rejected", file=sys.stderr)
        return 1
    if invalid_report.status != "error" or "multi_action_sheet" not in invalid_report.blockers:
        print("self-check failed: invalid sample was not blocked", file=sys.stderr)
        return 1
    if "state_lineart_lineage_missing" not in missing_lineage_report.blockers:
        print("self-check failed: v2 contract without lineart lineage passed", file=sys.stderr)
        return 1
    if "state_lineart_action_mismatch" not in wrong_action_report.blockers:
        print("self-check failed: mismatched state lineart action passed", file=sys.stderr)
        return 1
    if legacy_report.status != "ok" or "legacy_contract_without_state_lineart_lineage" not in legacy_report.warnings:
        print("self-check failed: legacy v1 compatibility changed", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        strip = Image.new("P", (32, 16), 0)
        strip.putpalette([0, 0, 0, 255, 255, 255] + [0, 0, 0] * 254)
        draw = ImageDraw.Draw(strip)
        draw.rectangle((4, 3, 10, 13), outline=1)
        draw.rectangle((21, 3, 27, 13), outline=1)
        strip_path = root / "strip.png"
        strip.save(strip_path, bits=4, transparency=0)
        source_paths: list[Path] = []
        for index in range(2):
            source_path = root / f"source_{index}.png"
            strip.crop((index * 16, 0, (index + 1) * 16, 16)).save(source_path, bits=4, transparency=0)
            source_paths.append(source_path)
        lineart = Image.new("P", (16, 16), 0)
        lineart.putpalette(strip.getpalette())
        ImageDraw.Draw(lineart).rectangle((4, 3, 10, 13), outline=1)
        lineart_path = root / "lineart.png"
        lineart.save(lineart_path, bits=4, transparency=0)
        artifact_valid = dict(valid)
        artifact_valid["schema_version"] = "3.0.0"
        artifact_valid["frames"] = [dict(frame) for frame in valid["frames"]]
        for index, frame in enumerate(artifact_valid["frames"]):
            frame.update({"x": index * 16, "y": 0, "w": 16, "h": 16, "pivot_x": 8, "pivot_y": 15})
            frame["lineage"] = {
                "source_frame_id": f"idle_{index}", "source_frame_sha256": sha256_file(source_paths[index]),
                "source_artifact": {
                    "path": source_paths[index].name, "sha256": sha256_file(source_paths[index]),
                    "pixel_sha256": _frame_pixel_hash(Image.open(source_paths[index])),
                },
                "transformation": "native_reauthored", "duplicate_role": "none"
            }
            frame["support"] = {"grounded": True, "measurement_method": "pixel_derived", "contacts": [{"id": "feet", "x": 8, "y": 15}]}
        artifact_valid["artifact"] = {
            "path": "strip.png", "sha256": sha256_file(strip_path), "transparent_index": 0,
            "cell_policy": "fixed_cell_coordinate_scoped", "allowed_boundary_contacts": []
        }
        artifact_valid["state_lineart_lineage"] = dict(valid["state_lineart_lineage"])
        artifact_valid["state_lineart_lineage"].update({"source_path": "lineart.png", "source_sha256": sha256_file(lineart_path)})
        artifact_valid["timing_contract"] = {"vblank_hz": 60, "loop": True, "frame_holds_vblank": [6, 6]}
        artifact_valid["motion_profile_id"] = "idle_breathing"
        artifact_valid["metasprite_layout"] = {"hardware_cells_per_frame": 1, "peak_sprites_per_scanline": 1, "peak_pixels_per_scanline": 16}
        authored_source = root / "authored_source.png"
        lineart.save(authored_source, bits=4, transparency=0)
        producer_record = root / "producer_record.json"
        producer_record.write_text(json.dumps({
            "status": "passed", "source_kind": "hand_authored_pixel",
            "producer_kind": "pixel_editor_export", "subject_sha256": sha256_file(authored_source),
        }), encoding="utf-8")
        approval_record = root / "approval.json"
        approval_record.write_text(json.dumps({
            "status": "approved", "subject_sha256": sha256_file(lineart_path),
        }), encoding="utf-8")
        artifact_valid["state_lineart_lineage"].update({
            "authorship_method": "hand_authored_native", "derivation_method": "hand_drawn_native",
            "approval_record": {"path": "approval.json", "sha256": sha256_file(approval_record), "subject_sha256": sha256_file(lineart_path)},
        })
        artifact_valid["production_provenance"] = {
            "source_kind": "hand_authored_pixel", "producer_kind": "pixel_editor_export",
            "authored_source": {"path": "authored_source.png", "sha256": sha256_file(authored_source)},
            "producer_record": {"path": "producer_record.json", "sha256": sha256_file(producer_record), "subject_sha256": sha256_file(authored_source)},
        }
        artifact_report = validate_strip(artifact_valid, root)

        replicated = Image.new("P", (32, 16), 0)
        replicated.putpalette(strip.getpalette())
        small = Image.new("P", (16, 8), 0)
        small.putpalette(strip.getpalette())
        ImageDraw.Draw(small).rectangle((2, 1, 5, 6), fill=1)
        replicated = small.resize((32, 16), Image.Resampling.NEAREST)
        replicated_path = root / "replicated.png"
        replicated.save(replicated_path, bits=4, transparency=0)
        replicated_contract = json.loads(json.dumps(artifact_valid))
        replicated_contract["artifact"].update({"path": "replicated.png", "sha256": sha256_file(replicated_path)})
        replicated_report = validate_strip(replicated_contract, root)

        pending_approval = json.loads(json.dumps(artifact_valid))
        approval_record.write_text(json.dumps({"status": "pending", "subject_sha256": sha256_file(lineart_path)}), encoding="utf-8")
        pending_approval["state_lineart_lineage"]["approval_record"]["sha256"] = sha256_file(approval_record)
        pending_approval_report = validate_strip(pending_approval, root)
        approval_record.write_text(json.dumps({"status": "approved", "subject_sha256": sha256_file(lineart_path)}), encoding="utf-8")

        invalid_schema = json.loads(json.dumps(artifact_valid))
        invalid_schema["state_lineart_lineage"]["derivation_method"] = "manual_cluster_cleanup"
        invalid_schema_report = validate_strip(invalid_schema, root)

        procedural_pixels = json.loads(json.dumps(artifact_valid))
        procedural_pixels["production_provenance"]["source_kind"] = "procedural_primitive"
        procedural_pixels["production_provenance"]["producer_kind"] = "procedural_code_probe"
        procedural_record = root / "procedural_record.json"
        procedural_record.write_text(json.dumps({
            "status": "passed", "source_kind": "procedural_primitive",
            "producer_kind": "procedural_code_probe", "subject_sha256": sha256_file(authored_source),
        }), encoding="utf-8")
        procedural_pixels["production_provenance"]["producer_record"].update({
            "path": "procedural_record.json", "sha256": sha256_file(procedural_record),
        })
        procedural_pixels_report = validate_strip(procedural_pixels, root)

        bad_strip = strip.copy()
        bad_draw = ImageDraw.Draw(bad_strip)
        bad_draw.line((15, 6, 16, 6), fill=1)
        bad_path = root / "bad_strip.png"
        bad_strip.save(bad_path, bits=4, transparency=0)
        neighbor = json.loads(json.dumps(artifact_valid))
        neighbor["artifact"].update({
            "path": "bad_strip.png", "sha256": sha256_file(bad_path),
            "allowed_boundary_contacts": [
                {"frame_index": 0, "edge": "right", "reason": "adversarial"},
                {"frame_index": 1, "edge": "left", "reason": "adversarial"},
            ],
        })
        neighbor_report = validate_strip(neighbor, root)
        preview_frames = [strip.crop((0, 0, 16, 16)), strip.crop((16, 0, 32, 16))]
        preview_path = root / "wrong_timing.gif"
        preview_frames[0].save(preview_path, save_all=True, append_images=preview_frames[1:], duration=[200, 200], loop=0, transparency=0)
        wrong_timing = json.loads(json.dumps(artifact_valid))
        wrong_timing["timing_contract"]["preview"] = {"path": "wrong_timing.gif", "sha256": sha256_file(preview_path)}
        wrong_timing_report = validate_strip(wrong_timing, root)
        duplicate_timing = json.loads(json.dumps(artifact_valid))
        duplicate_timing["frames"][0]["hold_frames"] = 6
        duplicate_timing_report = validate_strip(duplicate_timing, root)
        mechanical = json.loads(json.dumps(artifact_valid))
        producer_record.write_text(json.dumps({
            "status": "passed", "source_kind": "hand_authored_pixel",
            "producer_kind": "pixel_editor_export", "subject_sha256": sha256_file(authored_source),
            "process": {"resampling": "NEAREST", "resize": True},
        }), encoding="utf-8")
        mechanical["production_provenance"]["producer_record"]["sha256"] = sha256_file(producer_record)
        mechanical_report = validate_strip(mechanical, root)
        vector = json.loads(json.dumps(artifact_valid))
        producer_record.write_text(json.dumps({
            "status": "passed", "source_kind": "hand_authored_pixel",
            "producer_kind": "pixel_editor_export", "subject_sha256": sha256_file(authored_source),
            "lineart_source": {"path": "lineart.svg", "rasterizer": "rsvg-convert"},
        }), encoding="utf-8")
        vector["production_provenance"]["producer_record"]["sha256"] = sha256_file(producer_record)
        vector_report = validate_strip(vector, root)
        producer_record.write_text(json.dumps({
            "status": "passed", "source_kind": "hand_authored_pixel",
            "producer_kind": "pixel_editor_export", "subject_sha256": sha256_file(authored_source),
        }), encoding="utf-8")
        shared_source = json.loads(json.dumps(artifact_valid))
        for frame in shared_source["frames"]:
            frame["lineage"]["source_frame_sha256"] = "a" * 64
        shared_source_report = validate_strip(shared_source, root)
        invented_lineage = json.loads(json.dumps(artifact_valid))
        for index, frame in enumerate(invented_lineage["frames"]):
            frame["lineage"].pop("source_artifact", None)
            frame["lineage"]["source_frame_sha256"] = "%064x" % (index + 101)
        invented_lineage_report = validate_strip(invented_lineage, root)
        invalid_hold = json.loads(json.dumps(artifact_valid))
        invalid_hold["frames"][1]["lineage"].update({
            "transformation": "approved_hold", "duplicate_role": "approved_hold",
            "approved_source_frame_id": "missing_approved_frame", "approved_source_frame_sha256": "b" * 64,
        })
        invalid_hold_report = validate_strip(invalid_hold, root)
        mismatched_lineage = json.loads(json.dumps(artifact_valid))
        mismatched_lineage["frames"][0]["lineage"]["source_frame_sha256"] = "c" * 64
        mismatched_lineage_report = validate_strip(mismatched_lineage, root)
    if artifact_report.status != "ok":
        print(f"self-check failed: artifact-bound positive rejected: {artifact_report.blockers}", file=sys.stderr)
        return 1
    if not any(code.startswith("neighbor_cell_fragment_detected") for code in neighbor_report.blockers):
        print("self-check failed: adjacent cell fragment passed", file=sys.stderr)
        return 1
    if "gif_delay_contract_mismatch" not in wrong_timing_report.blockers:
        print("self-check failed: preview timing divergence passed", file=sys.stderr)
        return 1
    if not any(code.startswith("duplicate_timing_authority") for code in duplicate_timing_report.blockers):
        print("self-check failed: duplicate timing authority passed", file=sys.stderr)
        return 1
    if "mechanical_resize_mislabeled_native" not in mechanical_report.blockers:
        print("self-check failed: mechanical resize mislabeled as native passed", file=sys.stderr)
        return 1
    if "vector_procedural_lineart_declared_native" not in vector_report.blockers:
        print("self-check failed: SVG-derived lineart passed as native", file=sys.stderr)
        return 1
    if "source_frame_lineage_not_independent" not in shared_source_report.blockers:
        print("self-check failed: shared source-frame lineage passed", file=sys.stderr)
        return 1
    if "source_frame_artifact_unbound" not in invented_lineage_report.blockers:
        print("self-check failed: invented frame hashes passed without physical artifacts", file=sys.stderr)
        return 1
    if "approved_hold_lineage_unbound" not in invalid_hold_report.blockers:
        print("self-check failed: approved_hold without referenced approved frame passed", file=sys.stderr)
        return 1
    if mismatched_lineage_report.blockers != ["source_frame_lineage_mismatch"]:
        print("self-check failed: source_frame_sha256 tamper was not isolated", file=sys.stderr)
        return 1
    if "native_pixel_integer_scale_masquerade" not in replicated_report.blockers:
        print("self-check failed: integer-expanded raster passed as native resolution", file=sys.stderr)
        return 1
    if "native_lineart_approval_status_invalid" not in pending_approval_report.blockers:
        print("self-check failed: pending approval passed as approved lineart", file=sys.stderr)
        return 1
    if "animation_strip_schema_invalid" not in invalid_schema_report.blockers:
        print("self-check failed: noncanonical contract bypassed bundled schema", file=sys.stderr)
        return 1
    if "code_authored_character_pixels" not in procedural_pixels_report.blockers:
        print("self-check failed: procedural character raster passed as native art", file=sys.stderr)
        return 1
    print("validate_strip self-check passed (schema, provenance, native scale, approval, artifact, timing)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="animation strip contract JSON")
    parser.add_argument("--project-root", type=Path, help="root used to resolve v3 artifact paths")
    parser.add_argument("--output", type=Path, help="optional report output path")
    parser.add_argument("--self-check", action="store_true", help="run built-in self-check")
    args = parser.parse_args(argv)

    if args.self_check:
        return self_check()
    if not args.input:
        parser.error("--input is required unless --self-check is used")

    report = validate_strip(load_json(args.input), args.project_root)
    payload = {
        "tool_name": "validate_strip",
        "tool_version": TOOL_VERSION,
        "status": report.status,
        "blockers": report.blockers,
        "warnings": report.warnings,
        "metrics": report.metrics,
    }
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report.status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
