"""Build an explicit, layer-aware two-plane scroll profile from a full camera sweep.

The report is an analysis aid for source translation. It does not assign VDP
plane priority, generate a tilemap, or prove a runtime budget.
"""
from __future__ import annotations

import math


def analyze(source_view: dict, source_view_sha256: str, spec: dict) -> dict:
    if not isinstance(source_view, dict) or not isinstance(spec, dict):
        raise ValueError("source-view report and profile spec must be JSON objects")
    if source_view.get("schema") != "mugen2sgdk_forge.stage_source_view_report/v1":
        raise ValueError("input is not a supported stage-source-view report")
    sweep = source_view.get("camera_sweep_profile")
    if not isinstance(sweep, dict) or sweep.get("schema") != \
            "mugen2sgdk_forge.stage_camera_sweep_profile/v1":
        raise ValueError("a full camera-sweep profile is required")
    cameras = sweep.get("camera_positions_from_left", [])
    if (not isinstance(cameras, list) or len(cameras) < 2
            or any(not isinstance(camera, int) or isinstance(camera, bool) for camera in cameras)
            or cameras != list(range(cameras[0], cameras[-1] + 1))):
        raise ValueError("camera sweep must contain every consecutive integer camera position")
    if sweep.get("sample_count") != len(cameras):
        raise ValueError("camera sweep sample_count does not match its positions")
    viewport_height = source_view.get("viewport", {}).get("height")
    sweep_rows = sweep.get("scanlines", [])
    if (not isinstance(viewport_height, int) or len(sweep_rows) != viewport_height
            or [row.get("screen_y") for row in sweep_rows] != list(range(viewport_height))):
        raise ValueError("camera sweep scanlines must cover the full viewport in order")
    if spec.get("schema") != "mugen2sgdk_forge.stage_plane_profile_spec/v1":
        raise ValueError("unsupported semantic plane-profile spec")
    profile_id = spec.get("profile_id")
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise ValueError("profile_id must be a non-empty string")
    mapping = spec.get("target_scroll_speed_by_layer")
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("target_scroll_speed_by_layer must be a non-empty object")
    clean_mapping: dict[str, float] = {}
    for layer, target in mapping.items():
        if not isinstance(layer, str) or not layer:
            raise ValueError("layer names must be non-empty strings")
        if isinstance(target, bool) or not isinstance(target, (int, float)) or not math.isfinite(target):
            raise ValueError(f"target speed for {layer} must be numeric")
        clean_mapping[layer] = round(float(target), 9)

    frame_step = spec.get("camera_frame_step", 4)
    if not isinstance(frame_step, int) or isinstance(frame_step, bool) or frame_step <= 0:
        raise ValueError("camera_frame_step must be a positive integer")

    assignments = []
    total_samples = 0
    remapped_samples = 0
    weighted_frame_error = 0.0
    max_anchor_drift = 0.0
    max_drift_case = None
    over_capacity = []
    for row in sweep_rows:
        y = int(row["screen_y"])
        speed_assignment: dict[str, float] = {}
        target_speeds = set()
        row_samples = 0
        for group in row.get("source_speed_groups", []):
            layers = group.get("layers")
            if not isinstance(layers, list) or not layers or any(
                    not isinstance(layer, str) or not layer for layer in layers):
                raise ValueError(f"source speed group at y={y} must name one or more layers")
            source_speed = round(float(group["speed"]), 9)
            target_by_layer = {clean_mapping.get(layer, source_speed)
                               for layer in layers}
            if len(target_by_layer) != 1:
                raise ValueError(
                    f"source speed {source_speed} at y={y} contains layers mapped to different targets; "
                    "the preview remapper can only change a complete source-speed group")
            target = target_by_layer.pop()
            key = str(source_speed)
            if key in speed_assignment and speed_assignment[key] != target:
                raise ValueError(f"ambiguous source-speed mapping at y={y}: {key}")
            speed_assignment[key] = target
            target_speeds.add(target)

            samples = int(group.get("visible_pixels", 0))
            distance = int(group.get("max_camera_distance", 0))
            if samples < 0 or distance < 0 or not math.isfinite(source_speed):
                raise ValueError(f"invalid source group measurement at y={y}")
            total_samples += samples
            row_samples += samples
            if abs(source_speed - target) > 1e-9:
                remapped_samples += samples
                weighted_frame_error += samples * abs(source_speed - target) * frame_step
                drift = distance * abs(source_speed - target)
                if drift > max_anchor_drift:
                    max_anchor_drift = drift
                    max_drift_case = {
                        "screen_y": y,
                        "source_speed": source_speed,
                        "target_speed": target,
                        "layers": list(group.get("layers", [])),
                        "max_camera_distance": distance,
                        "max_camera_from_left": group.get("max_camera_from_left"),
                        "anchor_drift_px": round(drift, 9),
                    }
        if len(target_speeds) > 2:
            over_capacity.append({"screen_y": y, "target_scroll_speeds": sorted(target_speeds)})
        assignments.append({
            "screen_y": y,
            "source_to_plane_speed_assignment": speed_assignment,
            "target_scroll_speeds": sorted(target_speeds),
            "source_speed_group_count": len(row.get("source_speed_groups", [])),
            "target_speed_group_count": len(target_speeds),
            "visible_pixel_samples": row_samples,
        })

    if not assignments:
        raise ValueError("camera sweep contains no scanlines")
    if total_samples != int(sweep.get("total_visible_pixel_samples", -1)):
        raise ValueError("camera sweep pixel-sample total does not match its scanline groups")
    if over_capacity:
        preview = ", ".join(str(row["screen_y"]) for row in over_capacity[:12])
        raise ValueError(f"profile exceeds two speeds on {len(over_capacity)} scanlines (first: {preview})")

    return {
        "schema": "mugen2sgdk_forge.stage_semantic_plane_profile_report/v1",
        "status": "analysis_only_two_speed_profile",
        "profile_id": profile_id,
        "description": spec.get("description", ""),
        "source_sha256": source_view.get("source_sha256"),
        "source_view_report_sha256": source_view_sha256,
        "camera_positions_from_left": cameras,
        "camera_samples": len(cameras),
        "camera_anchor_from_left": sweep.get("reference_camera_from_left"),
        "camera_frame_step_assumption": frame_step,
        "target_scroll_speed_by_layer": clean_mapping,
        "total_visible_pixel_samples": total_samples,
        "remapped_visible_pixel_samples": remapped_samples,
        "remapped_fraction": remapped_samples / total_samples if total_samples else 0.0,
        "mean_displacement_error_px_per_sample_per_frame":
            weighted_frame_error / total_samples if total_samples else 0.0,
        "maximum_anchor_displacement_lower_bound_px": round(max_anchor_drift, 9),
        "maximum_anchor_displacement_case": max_drift_case,
        "scanlines_over_two_target_speeds": 0,
        "cross_camera_scanline_profile": {"scanline_assignments": assignments},
        "limitations": [
            "source-space remap preview only; no coherent Plane A/B ownership or tile priority",
            "no authored pixel approval, palette-conflict report, ResComp, VRAM, DMA, or VBlank measurement",
            "source renderer rounding and BGCtrl animation are not compared with MUGEN runtime",
        ],
        "claim_ceiling": "source_composition_analysis_only",
    }
