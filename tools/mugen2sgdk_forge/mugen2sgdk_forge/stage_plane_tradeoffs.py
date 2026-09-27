"""Optimistic two-plane scroll-speed tradeoff estimate from a source-view report."""
from __future__ import annotations

from itertools import combinations


def _line_tradeoff(row: dict, camera_frame_step: int) -> dict:
    counts = row.get("visible_pixels_by_layer", {})
    deltas = row.get("horizontal_delta_by_layer", {})
    if set(counts) != set(deltas):
        raise ValueError("source-view scanline must map every visible layer to a horizontal delta")

    groups: dict[float, dict] = {}
    for layer, count in counts.items():
        speed = round(float(deltas[layer]), 9)
        group = groups.setdefault(speed, {"speed": speed, "visible_pixels": 0, "layers": []})
        group["visible_pixels"] += int(count)
        group["layers"].append(layer)
    speeds = sorted(groups)
    if len(speeds) <= 2:
        return {"screen_y": row["screen_y"], "source_speed_groups": [groups[s] for s in speeds],
                "preserved_scroll_speeds": speeds, "remapped_visible_pixels": 0,
                "pixel_displacement_error_lower_bound": 0,
                "max_displacement_per_pixel_per_frame": 0.0,
                "status": "two_or_fewer_source_groups"}

    candidates = []
    for pair in combinations(speeds, 2):
        assignment = {}
        moved_pixels = 0
        weighted_error = 0.0
        max_per_pixel = 0.0
        for speed in speeds:
            target = min(pair, key=lambda candidate: (abs(speed - candidate), candidate))
            group = groups[speed]
            if target != speed:
                moved_pixels += group["visible_pixels"]
                mismatch = abs(speed - target) * camera_frame_step
                weighted_error += group["visible_pixels"] * mismatch
                max_per_pixel = max(max_per_pixel, mismatch)
            assignment[str(speed)] = target
        candidates.append((weighted_error, moved_pixels, pair, max_per_pixel, assignment))
    weighted_error, moved_pixels, pair, max_per_pixel, assignment = min(
        candidates, key=lambda item: (item[0], item[1], item[2]))
    return {"screen_y": row["screen_y"], "source_speed_groups": [groups[s] for s in speeds],
            "preserved_scroll_speeds": list(pair), "source_to_plane_speed_assignment": assignment,
            "remapped_visible_pixels": moved_pixels,
            "pixel_displacement_error_lower_bound": weighted_error,
            "max_displacement_per_pixel_per_frame": max_per_pixel,
            "status": "optimistic_two_speed_assignment"}


def _weighted_median(weighted_values: list[tuple[float, int]]) -> float:
    usable = sorted((float(value), int(weight)) for value, weight in weighted_values if weight > 0)
    if not usable:
        values = sorted(float(value) for value, _ in weighted_values)
        return values[len(values) // 2]
    half = sum(weight for _, weight in usable) / 2
    cumulative = 0
    for value, weight in usable:
        cumulative += weight
        if cumulative >= half:
            return value
    return usable[-1][0]


def _minimax_cluster_center(groups: list[dict]) -> tuple[float, float]:
    """Return a weighted tie-break center and its minimum worst anchor drift."""
    if len(groups) == 1:
        return float(groups[0]["speed"]), 0.0
    constrained = [group for group in groups if group["max_camera_distance"] > 0]
    if not constrained:
        center = _weighted_median([(group["speed"], group["visible_pixels"]) for group in groups])
        return center, 0.0

    low = 0.0
    high = ((max(float(group["speed"]) for group in constrained)
             - min(float(group["speed"]) for group in constrained))
            * max(int(group["max_camera_distance"]) for group in constrained))

    def feasible(radius: float) -> tuple[bool, float, float]:
        lower = max(float(group["speed"]) - radius / int(group["max_camera_distance"])
                    for group in constrained)
        upper = min(float(group["speed"]) + radius / int(group["max_camera_distance"])
                    for group in constrained)
        return lower <= upper, lower, upper

    for _ in range(64):
        middle = (low + high) / 2
        if feasible(middle)[0]:
            high = middle
        else:
            low = middle
    _, lower, upper = feasible(high)
    weights = [(float(group["speed"]), int(group["distance_weighted_pixels"]))
               for group in groups]
    if not any(weight > 0 for _, weight in weights):
        weights = [(float(group["speed"]), int(group["visible_pixels"])) for group in groups]
    center = min(upper, max(lower, _weighted_median(weights)))
    return round(center, 9), high


def _line_endpoint_minimax(rows_by_camera: list[tuple[int, dict]], anchor: int,
                           camera_frame_step: int) -> dict:
    """Create a two-speed continuous target minimizing worst sampled anchor drift.

    Unlike the legacy discrete optimizer, target speeds need not equal source
    layer deltas. That is a diagnostic lower bound: authoring a real plane at an
    intermediate speed requires compositing/redrawing its assigned layers.
    """
    groups: dict[float, dict] = {}
    screen_y = None
    for camera, row in rows_by_camera:
        if screen_y is None:
            screen_y = int(row["screen_y"])
        elif screen_y != int(row["screen_y"]):
            raise ValueError("endpoint minimax rows must refer to the same scanline")
        counts = row.get("visible_pixels_by_layer", {})
        deltas = row.get("horizontal_delta_by_layer", {})
        if set(counts) != set(deltas):
            raise ValueError("source-view scanline must map every visible layer to a horizontal delta")
        distance = abs(int(camera) - anchor)
        for layer, count in counts.items():
            speed = round(float(deltas[layer]), 9)
            group = groups.setdefault(speed, {"speed": speed, "visible_pixels": 0,
                                              "distance_weighted_pixels": 0,
                                              "max_camera_distance": 0, "layers": []})
            count = int(count)
            group["visible_pixels"] += count
            group["distance_weighted_pixels"] += count * distance
            if count > 0:
                group["max_camera_distance"] = max(group["max_camera_distance"], distance)
            if layer not in group["layers"]:
                group["layers"].append(layer)
    return _continuous_assignment(screen_y, groups, camera_frame_step)


def _continuous_assignment(screen_y: int, groups: dict[float, dict],
                           camera_frame_step: int) -> dict:
    speeds = sorted(groups)
    if len(speeds) <= 2:
        return {"screen_y": screen_y, "source_speed_groups": [groups[s] for s in speeds],
                "preserved_scroll_speeds": speeds, "target_scroll_speeds": speeds,
                "source_to_plane_speed_assignment": {str(speed): speed for speed in speeds},
                "remapped_visible_pixels": 0,
                "pixel_displacement_error_lower_bound": 0.0,
                "max_displacement_per_pixel_per_frame": 0.0,
                "maximum_anchor_displacement_lower_bound_px": 0.0,
                "status": "two_or_fewer_source_groups"}

    candidates = []
    for split in range(1, len(speeds)):
        clusters = [[groups[s] for s in speeds[:split]],
                    [groups[s] for s in speeds[split:]]]
        centers_and_radii = [_minimax_cluster_center(cluster) for cluster in clusters]
        centers = [center for center, _ in centers_and_radii]
        assignment = {str(group["speed"]): center
                      for cluster, (center, _) in zip(clusters, centers_and_radii)
                      for group in cluster}
        max_anchor_drift = max(
            (int(group["max_camera_distance"])
             * abs(float(group["speed"]) - assignment[str(group["speed"])])
             for group in groups.values()), default=0.0)
        weighted_anchor_error = sum(
            int(group["distance_weighted_pixels"])
            * abs(float(group["speed"]) - assignment[str(group["speed"])])
            for group in groups.values())
        moved = sum(int(group["visible_pixels"]) for group in groups.values()
                    if abs(float(group["speed"])
                           - assignment[str(group["speed"])]) > 1e-9)
        frame_error = sum(int(group["visible_pixels"])
                          * abs(float(group["speed"])
                                - assignment[str(group["speed"])])
                          * camera_frame_step for group in groups.values())
        key = (max_anchor_drift, weighted_anchor_error, moved, tuple(centers))
        candidates.append((key, clusters, centers, assignment, frame_error, moved,
                           weighted_anchor_error))
    _, clusters, centers, assignment, frame_error, moved, weighted_error = min(
        candidates, key=lambda candidate: candidate[0])
    max_anchor_drift = max(
        (int(group["max_camera_distance"])
         * abs(float(group["speed"]) - assignment[str(group["speed"])])
         for group in groups.values()), default=0.0)
    max_per_frame = max((abs(float(speed) - float(assignment[str(speed)]))
                         * camera_frame_step for speed in speeds), default=0.0)
    return {"screen_y": screen_y,
            "source_speed_groups": [groups[s] for s in speeds],
            "preserved_scroll_speeds": [speed for speed in speeds
                                         if abs(float(speed) - assignment[str(speed)]) <= 1e-9],
            "target_scroll_speeds": centers,
            "source_to_plane_speed_assignment": assignment,
            "remapped_visible_pixels": moved,
            "pixel_displacement_error_lower_bound": frame_error,
            "max_displacement_per_pixel_per_frame": max_per_frame,
            "anchor_weighted_displacement_error_lower_bound": weighted_error,
            "maximum_anchor_displacement_lower_bound_px": max_anchor_drift,
            "clusters_by_target_speed": [
                {"target_speed": center,
                 "source_speeds": [float(group["speed"]) for group in cluster],
                 "layers": sorted({layer for group in cluster for layer in group["layers"]})}
                for cluster, center in zip(clusters, centers)],
            "status": "continuous_two_speed_minimax_candidate"}


def _line_endpoint_minimax_sweep(row: dict, camera_frame_step: int) -> dict:
    groups = {round(float(group["speed"]), 9): group
              for group in row.get("source_speed_groups", [])}
    return _continuous_assignment(int(row["screen_y"]), groups, camera_frame_step)


def _line_discrete_sweep(row: dict, camera_frame_step: int) -> dict:
    groups = row.get("source_speed_groups", [])
    synthetic_counts = {f"speed_{index}": int(group["visible_pixels"])
                        for index, group in enumerate(groups)}
    synthetic_deltas = {f"speed_{index}": float(group["speed"])
                        for index, group in enumerate(groups)}
    result = _line_tradeoff({"screen_y": row["screen_y"],
                             "visible_pixels_by_layer": synthetic_counts,
                             "horizontal_delta_by_layer": synthetic_deltas},
                            camera_frame_step)
    result["source_speed_groups"] = groups
    return result


def analyze(source_view: dict, camera_frame_step: int = 4,
            reference_camera_from_left: int | None = None,
            objective: str = "visible_pixel_weighted_discrete") -> dict:
    if source_view.get("schema") != "mugen2sgdk_forge.stage_source_view_report/v1":
        raise ValueError("input is not a supported stage-source-view report")
    if not isinstance(camera_frame_step, int) or isinstance(camera_frame_step, bool) or camera_frame_step <= 0:
        raise ValueError("camera_frame_step must be a positive integer")
    if objective not in {"visible_pixel_weighted_discrete", "endpoint_minimax_continuous"}:
        raise ValueError("unsupported objective; expected visible_pixel_weighted_discrete or endpoint_minimax_continuous")
    output_views = []
    source_views = source_view.get("views", [])
    camera_sweep = source_view.get("camera_sweep_profile")
    if camera_sweep is not None and camera_sweep.get("schema") != \
            "mugen2sgdk_forge.stage_camera_sweep_profile/v1":
        raise ValueError("unsupported source-view camera sweep profile")
    camera_positions = [int(view["camera_from_left"]) for view in source_views]
    if not camera_positions:
        raise ValueError("source-view report must contain at least one camera view")
    inferred_anchor = (min(camera_positions) + max(camera_positions)) // 2
    anchor = inferred_anchor if reference_camera_from_left is None else reference_camera_from_left
    if not isinstance(anchor, int) or isinstance(anchor, bool) or not min(camera_positions) <= anchor <= max(camera_positions):
        raise ValueError("reference camera anchor must be an integer within sampled camera bounds")
    if objective == "endpoint_minimax_continuous" and camera_sweep is not None:
        if camera_sweep.get("reference_camera_from_left") != anchor:
            raise ValueError("tradeoff anchor must match the source camera sweep anchor")
    for view in source_views:
        lines = [_line_tradeoff(row, camera_frame_step) for row in view.get("scanlines", [])]
        total_visible = sum(sum(row.get("visible_pixels_by_layer", {}).values())
                            for row in view.get("scanlines", []))
        displaced = sum(line["remapped_visible_pixels"] for line in lines)
        error = sum(line["pixel_displacement_error_lower_bound"] for line in lines)
        over_capacity = [line for line in lines if line["status"] == "optimistic_two_speed_assignment"]
        output_views.append({
            "camera_from_left": view["camera_from_left"],
            "source_scanline_count": len(lines),
            "source_scanlines_over_two_speed_capacity": len(over_capacity),
            "total_visible_pixels": total_visible,
            "pixels_assigned_to_a_different_speed_group": displaced,
            "fraction_of_visible_pixels_assigned_differently": displaced / total_visible if total_visible else 0.0,
            "pixel_displacement_error_lower_bound": error,
            "mean_displacement_error_per_visible_pixel_per_frame": error / total_visible if total_visible else 0.0,
            "camera_frame_step": camera_frame_step,
            "scanline_assignments": lines,
        })

    cross_camera_lines = []
    heights = {len(view.get("scanlines", [])) for view in source_views}
    if len(heights) > 1:
        raise ValueError("all sampled camera views must have the same scanline count")
    height = next(iter(heights), 0)
    for y in range(height):
        counts_by_layer: dict[str, int] = {}
        deltas_by_layer: dict[str, float] = {}
        for view in source_views:
            row = view["scanlines"][y]
            for layer, count in row.get("visible_pixels_by_layer", {}).items():
                delta = round(float(row["horizontal_delta_by_layer"][layer]), 9)
                if layer in deltas_by_layer and deltas_by_layer[layer] != delta:
                    raise ValueError(f"layer {layer} has inconsistent scroll delta at scanline {y}")
                deltas_by_layer[layer] = delta
                counts_by_layer[layer] = counts_by_layer.get(layer, 0) + int(count)
        combined_row = {"screen_y": y, "visible_pixels_by_layer": counts_by_layer,
                        "horizontal_delta_by_layer": deltas_by_layer}
        if camera_sweep is not None and objective == "visible_pixel_weighted_discrete":
            sweep_rows = camera_sweep.get("scanlines", [])
            if len(sweep_rows) != height:
                raise ValueError("camera sweep height must match the source-view scanlines")
            cross_camera_lines.append(_line_discrete_sweep(sweep_rows[y], camera_frame_step))
        elif objective == "endpoint_minimax_continuous" and camera_sweep is not None:
            sweep_rows = camera_sweep.get("scanlines", [])
            if len(sweep_rows) != height:
                raise ValueError("camera sweep height must match the source-view scanlines")
            cross_camera_lines.append(_line_endpoint_minimax_sweep(sweep_rows[y],
                                                                    camera_frame_step))
        elif objective == "endpoint_minimax_continuous":
            rows_by_camera = [(int(view["camera_from_left"]), view["scanlines"][y])
                              for view in source_views]
            cross_camera_lines.append(_line_endpoint_minimax(rows_by_camera, anchor,
                                                               camera_frame_step))
        else:
            cross_camera_lines.append(_line_tradeoff(combined_row, camera_frame_step))
    cross_total = (int(camera_sweep["total_visible_pixel_samples"])
                   if camera_sweep is not None else
                   sum(sum(row.get("visible_pixels_by_layer", {}).values())
                       for view in source_views for row in view.get("scanlines", [])))
    cross_moved = sum(line["remapped_visible_pixels"] for line in cross_camera_lines)
    cross_error = sum(line["pixel_displacement_error_lower_bound"] for line in cross_camera_lines)
    cross_over = sum(len(line.get("source_speed_groups", [])) > 2
                     for line in cross_camera_lines)
    worst_line = max(cross_camera_lines,
                     key=lambda line: line["max_displacement_per_pixel_per_frame"], default=None)
    anchor_error = 0.0
    anchor_moved = 0
    max_anchor_case = None
    if camera_sweep is not None:
        for row, selected in zip(camera_sweep.get("scanlines", []), cross_camera_lines):
            assignment = selected.get("source_to_plane_speed_assignment", {})
            for group in row.get("source_speed_groups", []):
                source_speed = round(float(group["speed"]), 9)
                target_speed = float(assignment.get(str(source_speed), source_speed))
                mismatch = abs(source_speed - target_speed)
                anchor_error += int(group["distance_weighted_pixels"]) * mismatch
                if mismatch > 1e-9:
                    anchor_moved += int(group["visible_pixels"])
                    drift = int(group["max_camera_distance"]) * mismatch
                    candidate = (drift, group.get("max_camera_from_left"), int(row["screen_y"]),
                                 ", ".join(group.get("layers", [])), source_speed,
                                 target_speed, int(group["visible_pixels"]))
                    if max_anchor_case is None or candidate[0] > max_anchor_case[0]:
                        max_anchor_case = candidate
    else:
        for view in source_views:
            camera = int(view["camera_from_left"])
            distance_from_anchor = abs(camera - anchor)
            for row in view.get("scanlines", []):
                assignment = cross_camera_lines[int(row["screen_y"])].get("source_to_plane_speed_assignment", {})
                for layer, count in row.get("visible_pixels_by_layer", {}).items():
                    source_speed = round(float(row["horizontal_delta_by_layer"][layer]), 9)
                    target_speed = float(assignment.get(str(source_speed), source_speed))
                    drift = abs(source_speed - target_speed) * distance_from_anchor
                    anchor_error += int(count) * drift
                    if drift > 0:
                        anchor_moved += int(count)
                        candidate = (drift, camera, int(row["screen_y"]), layer, source_speed,
                                     target_speed, int(count))
                        if max_anchor_case is None or candidate[0] > max_anchor_case[0]:
                            max_anchor_case = candidate
    per_view_anchor = []
    for view in source_views:
        camera = int(view["camera_from_left"])
        distance_from_anchor = abs(camera - anchor)
        total = 0
        error = 0.0
        for row in view.get("scanlines", []):
            assignment = cross_camera_lines[int(row["screen_y"])].get("source_to_plane_speed_assignment", {})
            for layer, count in row.get("visible_pixels_by_layer", {}).items():
                source_speed = round(float(row["horizontal_delta_by_layer"][layer]), 9)
                target_speed = float(assignment.get(str(source_speed), source_speed))
                total += int(count)
                error += int(count) * abs(source_speed - target_speed) * distance_from_anchor
        per_view_anchor.append({"camera_from_left": camera,
                                "mean_anchor_alignment_drift_px_per_visible_pixel": error / total if total else 0.0})
    return {
        "schema": "mugen2sgdk_forge.stage_plane_tradeoffs_report/v1",
        "status": "analysis_only_optimistic_scroll_tradeoff",
        "source_sha256": source_view.get("source_sha256"),
        "source_view_report_schema": source_view.get("schema"),
        "camera_frame_step": camera_frame_step,
        "reference_camera_from_left": anchor,
        "reference_camera_anchor_basis": ("explicit_input" if reference_camera_from_left is not None
                                           else "midpoint_of_sampled_camera_bounds"),
        "objective": objective,
        "camera_sweep_sample_count": (camera_sweep.get("sample_count") if camera_sweep else None),
        "method": ("Per scanline, choose up to two source speeds minimizing visible-pixel-weighted absolute speed error; assign each other group to its nearest retained speed."
                   if objective == "visible_pixel_weighted_discrete" else
                   "Per scanline, partition ordered source speeds into up to two groups, then choose continuous target speeds minimizing worst anchor displacement over camera samples; weighted drift and changed pixels break ties."),
        "limitations": [
            "best two speed groups are selected independently per scanline and aggregated only over sampled camera views; this does not prove a coherent tilemap or Plane A/B ownership",
            "a dense camera sweep improves source visibility weights but still does not verify MUGEN runtime rasterization or subpixel rounding",
            "continuous intermediate target speeds require new compositing/redrawing; they are a lower-bound study, not a direct MUGEN layer-to-plane conversion",
            "does not model pixel priority interactions, palette, tile deduplication, ResComp, VRAM, DMA, VBlank, or artist judgment",
            "weighted scroll-speed error is a ranking proxy, not a perceptual approval or MUGEN runtime parity",
            "static source-view omits animated BG and BGCtrl",
        ],
        "views": output_views,
        "cross_camera_scanline_profile": {
            "camera_samples_from_left_bound": (camera_sweep.get("camera_positions_from_left")
                                               if camera_sweep
                                               else [view.get("camera_from_left") for view in source_views]),
            "source_scanlines_with_more_than_two_speed_groups": cross_over,
            "source_scanlines_over_two_speed_capacity": cross_over,
            "total_visible_pixel_samples": cross_total,
            "pixel_samples_assigned_to_a_different_speed_group": cross_moved,
            "fraction_of_pixel_samples_assigned_differently": cross_moved / cross_total if cross_total else 0.0,
            "pixel_displacement_error_lower_bound": cross_error,
            "mean_displacement_error_per_pixel_sample_per_frame": cross_error / cross_total if cross_total else 0.0,
            "maximum_displacement_per_pixel_per_frame": (
                worst_line["max_displacement_per_pixel_per_frame"] if worst_line else 0.0),
            "maximum_displacement_screen_y": worst_line["screen_y"] if worst_line else None,
            "camera_frame_step": camera_frame_step,
            "objective": objective,
            "scanline_assignments": cross_camera_lines,
        },
        "anchor_alignment_tradeoff": {
            "reference_camera_from_left": anchor,
            "anchor_basis": ("explicit_input" if reference_camera_from_left is not None
                             else "midpoint_of_sampled_camera_bounds"),
            "total_visible_pixel_samples": cross_total,
            "pixel_samples_with_speed_remap": anchor_moved,
            "mean_alignment_drift_px_per_visible_pixel_sample": anchor_error / cross_total if cross_total else 0.0,
            "maximum_alignment_drift_px": max_anchor_case[0] if max_anchor_case else 0.0,
            "maximum_alignment_drift_case": ({"camera_from_left": max_anchor_case[1],
                                               "screen_y": max_anchor_case[2],
                                               "layer": max_anchor_case[3],
                                               "source_speed": max_anchor_case[4],
                                               "assigned_speed": max_anchor_case[5],
                                               "visible_pixels": max_anchor_case[6]}
                                              if max_anchor_case else None),
            "by_camera": per_view_anchor,
            "method": "absolute(source_speed-assigned_speed) multiplied by horizontal camera distance from the reference anchor; source compositor camera samples only",
            "limitations": ["linear speed mismatch estimate, not rendered pixel correspondence or perceptual approval",
                            ("camera positions follow the declared sweep step"
                             if camera_sweep else "camera positions between sampled endpoints remain unverified"),
                            "MUGEN runtime rasterization remains unverified"],
        },
        "claim_ceiling": "source_derived_tradeoff_lower_bound_only",
    }
