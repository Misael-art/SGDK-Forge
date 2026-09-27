"""Tests for explicit layer-aware source-space two-plane profiles."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from mugen2sgdk_forge import stage_plane_profile  # noqa: E402


def _report(groups):
    return {
        "schema": "mugen2sgdk_forge.stage_source_view_report/v1",
        "source_sha256": "a" * 64,
        "viewport": {"height": 1},
        "camera_sweep_profile": {
            "schema": "mugen2sgdk_forge.stage_camera_sweep_profile/v1",
            "camera_positions_from_left": list(range(9)),
            "sample_count": 9,
            "reference_camera_from_left": 4,
            "total_visible_pixel_samples": sum(group["visible_pixels"] for group in groups),
            "scanlines": [{"screen_y": 0, "source_speed_groups": groups}],
        },
    }


def _group(speed, layer, samples=10, distance=4):
    return {"speed": speed, "layers": [layer], "visible_pixels": samples,
            "max_camera_distance": distance, "max_camera_from_left": 0}


def test_semantic_profile_maps_named_layers_and_reports_drift():
    report = _report([_group(0.0, "sky", 100, 4),
                      _group(0.5, "castle", 50, 4),
                      _group(0.75, "roof", 50, 4)])
    spec = {"schema": "mugen2sgdk_forge.stage_plane_profile_spec/v1",
            "profile_id": "castle_roof",
            "camera_frame_step": 2,
            "target_scroll_speed_by_layer": {"sky": 0.5, "castle": 0.5, "roof": 0.75}}
    result = stage_plane_profile.analyze(report, "b" * 64, spec)
    assert result["remapped_visible_pixel_samples"] == 100
    assert result["remapped_fraction"] == pytest.approx(0.5)
    assert result["mean_displacement_error_px_per_sample_per_frame"] == pytest.approx(0.5)
    assert result["maximum_anchor_displacement_lower_bound_px"] == pytest.approx(2.0)
    assignment = result["cross_camera_scanline_profile"]["scanline_assignments"][0]
    assert assignment["source_to_plane_speed_assignment"] == {
        "0.0": 0.5, "0.5": 0.5, "0.75": 0.75}
    assert assignment["target_scroll_speeds"] == [0.5, 0.75]


def test_semantic_profile_preserves_unmapped_source_speed():
    report = _report([_group(0.25, "unmapped_a"), _group(1.0, "unmapped_b")])
    spec = {"schema": "mugen2sgdk_forge.stage_plane_profile_spec/v1",
            "profile_id": "source_exact", "target_scroll_speed_by_layer": {"other": 0.0}}
    result = stage_plane_profile.analyze(report, "c" * 64, spec)
    assert result["remapped_visible_pixel_samples"] == 0
    assert result["cross_camera_scanline_profile"]["scanline_assignments"][0][
        "target_scroll_speeds"] == [0.25, 1.0]


def test_semantic_profile_rejects_profiles_over_two_speeds():
    report = _report([_group(0.0, "sky"), _group(0.5, "castle"), _group(1.0, "roof")])
    spec = {"schema": "mugen2sgdk_forge.stage_plane_profile_spec/v1",
            "profile_id": "bad", "target_scroll_speed_by_layer": {"none": 0.0}}
    with pytest.raises(ValueError, match="exceeds two speeds"):
        stage_plane_profile.analyze(report, "d" * 64, spec)


def test_semantic_profile_rejects_one_speed_group_split_across_targets():
    report = _report([{"speed": 0.5, "layers": ["a", "b"], "visible_pixels": 10,
                       "max_camera_distance": 4, "max_camera_from_left": 0}])
    spec = {"schema": "mugen2sgdk_forge.stage_plane_profile_spec/v1",
            "profile_id": "ambiguous",
            "target_scroll_speed_by_layer": {"a": 0.25, "b": 0.75}}
    with pytest.raises(ValueError, match="different targets"):
        stage_plane_profile.analyze(report, "e" * 64, spec)


def test_semantic_profile_rejects_non_object_and_unowned_source_groups():
    with pytest.raises(ValueError, match="JSON objects"):
        stage_plane_profile.analyze([], "f" * 64, {})
    report = _report([{"speed": 0.5, "layers": [], "visible_pixels": 10,
                       "max_camera_distance": 4}])
    spec = {"schema": "mugen2sgdk_forge.stage_plane_profile_spec/v1",
            "profile_id": "unowned", "target_scroll_speed_by_layer": {"other": 0.0}}
    with pytest.raises(ValueError, match="must name one or more layers"):
        stage_plane_profile.analyze(report, "f" * 64, spec)


def test_semantic_profile_requires_full_sweep_and_valid_frame_step():
    report = {"schema": "mugen2sgdk_forge.stage_source_view_report/v1",
              "source_sha256": "f" * 64}
    spec = {"schema": "mugen2sgdk_forge.stage_plane_profile_spec/v1",
            "profile_id": "invalid", "camera_frame_step": True,
            "target_scroll_speed_by_layer": {"sky": 0.0}}
    with pytest.raises(ValueError, match="full camera-sweep"):
        stage_plane_profile.analyze(report, "f" * 64, spec)
    report = _report([_group(0.0, "sky")])
    with pytest.raises(ValueError, match="positive integer"):
        stage_plane_profile.analyze(report, "f" * 64, spec)
    spec["camera_frame_step"] = 4
    report["camera_sweep_profile"]["camera_positions_from_left"] = [0, 2, 4]
    report["camera_sweep_profile"]["sample_count"] = 3
    with pytest.raises(ValueError, match="consecutive integer"):
        stage_plane_profile.analyze(report, "f" * 64, spec)
